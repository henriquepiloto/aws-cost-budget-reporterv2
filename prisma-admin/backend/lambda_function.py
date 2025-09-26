import json
import hashlib
import jwt
import pymysql
import boto3
import base64
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # CORS headers for all responses
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        
        # Handle preflight OPTIONS requests
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        if path == '/login' and method == 'POST':
            return handle_login(event, cors_headers)
        elif path == '/reset-password' and method == 'POST':
            return handle_reset_password(event, cors_headers)
        elif path == '/verify' and method == 'POST':
            return handle_verify(event, cors_headers)
        elif path == '/chat' and method == 'POST':
            return handle_chat(event, cors_headers)
        elif path == '/config' and method == 'GET':
            return get_config(event, cors_headers)
        elif path == '/config' and method == 'POST':
            return save_config(event, cors_headers)
        elif path == '/visual-config' and method == 'GET':
            return get_visual_config(event, cors_headers)
        elif path == '/visual-config' and method == 'POST':
            return save_visual_config(event, cors_headers)
        elif path == '/users' and method == 'GET':
            return get_users(event, cors_headers)
        elif path == '/users' and method == 'POST':
            return create_user(event, cors_headers)
        elif path == '/users' and method == 'PUT':
            return update_user(event, cors_headers)
        elif path == '/users' and method == 'DELETE':
            return delete_user(event, cors_headers)
        
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }

def get_db_connection():
    return pymysql.connect(
        host='glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com',
        user='select_admin',
        password='GR558AvfoYFz7NTZ1q8n',
        database='glpi_select',
        charset='utf8mb4'
    )

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists and add missing columns
    cursor.execute("SHOW TABLES LIKE 'chatbot_users'")
    if not cursor.fetchone():
        cursor.execute("""
        CREATE TABLE chatbot_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    # Add missing columns if they don't exist
    cursor.execute("SHOW COLUMNS FROM chatbot_users LIKE 'email'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE chatbot_users ADD COLUMN email VARCHAR(100) AFTER password")
    
    cursor.execute("SHOW COLUMNS FROM chatbot_users LIKE 'status'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE chatbot_users ADD COLUMN status VARCHAR(20) DEFAULT 'active' AFTER role")
    
    cursor.execute("SHOW COLUMNS FROM chatbot_users LIKE 'permissions'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE chatbot_users ADD COLUMN permissions TEXT AFTER status")
    
    cursor.execute("SHOW COLUMNS FROM chatbot_users LIKE 'updated_at'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE chatbot_users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        config_key VARCHAR(100),
        config_value TEXT,
        FOREIGN KEY (user_id) REFERENCES chatbot_users(id)
    )
    """)
    
    # Create visual config table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_visual_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        config_key VARCHAR(100) UNIQUE,
        config_value LONGTEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    
    # Create admin user
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute("""
    INSERT IGNORE INTO chatbot_users (username, password, email, role, permissions) 
    VALUES ('admin', %s, 'admin@selectsolucoes.com', 'admin', 'all')
    """, (admin_password,))
    
    conn.commit()

def verify_admin(event):
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        if payload.get('role') != 'admin':
            return None
        return payload
    except:
        return None

def handle_login(event, cors_headers):
    setup_database()
    data = json.loads(event['body'])
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password, role, status FROM chatbot_users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user and len(user) > 3 and user[3] == 'blocked':
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'error': 'User blocked'})
        }
    
    if user and user[1] == hashlib.sha256(password.encode()).hexdigest():
        token = jwt.encode({
            'user_id': user[0],
            'username': username,
            'role': user[2],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, 'secret_key', algorithm='HS256')
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'token': token, 'role': user[2]})
        }
    
    return {
        'statusCode': 401,
        'headers': cors_headers,
        'body': json.dumps({'error': 'Invalid credentials'})
    }

def handle_reset_password(event, cors_headers):
    data = json.loads(event['body'])
    username = data.get('username')
    
    temp_password = 'temp123'
    hashed = hashlib.sha256(temp_password.encode()).hexdigest()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE chatbot_users SET password = %s WHERE username = %s", (hashed, username))
    
    if cursor.rowcount > 0:
        conn.commit()
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': f'Password reset to: {temp_password}'})
        }
    
    return {
        'statusCode': 404,
        'headers': cors_headers,
        'body': json.dumps({'error': 'User not found'})
    }

def handle_verify(event, cors_headers):
    data = json.loads(event['body'])
    token = data.get('token')
    
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'valid': True, 'user': payload})
        }
    except:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'valid': False})
        }

def handle_chat(event, cors_headers):
    data = json.loads(event['body'])
    message = data.get('message', '')
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': message}]
            })
        )
        
        result = json.loads(response['body'].read())
        bot_response = result['content'][0]['text']
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'response': bot_response})
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'response': f'Olá! Como posso ajudar você hoje? (Bedrock temporariamente indisponível)'})
        }

def get_config(event, cors_headers):
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        user_id = payload['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT config_key, config_value FROM chatbot_config WHERE user_id = %s", (user_id,))
        configs = cursor.fetchall()
        
        config_dict = {config[0]: config[1] for config in configs}
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps(config_dict)
        }
    except:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Invalid token'})
        }

def save_config(event, cors_headers):
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        user_id = payload['user_id']
        
        data = json.loads(event['body'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for key, value in data.items():
            cursor.execute("""
                INSERT INTO chatbot_config (user_id, config_key, config_value) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE config_value = %s
            """, (user_id, key, value, value))
        
        conn.commit()
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Config saved'})
        }
    except:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Invalid token'})
        }

def get_visual_config(event, cors_headers):
    # Public endpoint - no authentication required for GET
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT config_key, config_value FROM chatbot_visual_config")
    configs = cursor.fetchall()
    
    config_dict = {config[0]: config[1] for config in configs}
    
    # Default values if not set
    defaults = {
        'logo_url': '',
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'sidebar_color': '#2c3e50',
        'app_name': 'Cloudinho'
    }
    
    for key, default_value in defaults.items():
        if key not in config_dict:
            config_dict[key] = default_value
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps(config_dict)
    }

def save_visual_config(event, cors_headers):
    admin = verify_admin(event)
    if not admin:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Admin access required'})
        }
    
    data = json.loads(event['body'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for key, value in data.items():
        cursor.execute("""
            INSERT INTO chatbot_visual_config (config_key, config_value) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE config_value = %s
        """, (key, value, value))
    
    conn.commit()
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'message': 'Visual config saved'})
    }

def get_users(event, cors_headers):
    admin = verify_admin(event)
    if not admin:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Admin access required'})
        }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get column names first
    cursor.execute("SHOW COLUMNS FROM chatbot_users")
    columns = [col[0] for col in cursor.fetchall()]
    
    # Build query based on available columns
    select_cols = ['id', 'username', 'role', 'created_at']
    if 'email' in columns:
        select_cols.insert(2, 'email')
    if 'status' in columns:
        select_cols.insert(-1, 'status')
    if 'permissions' in columns:
        select_cols.insert(-1, 'permissions')
    
    cursor.execute(f"SELECT {', '.join(select_cols)} FROM chatbot_users ORDER BY created_at DESC")
    users = cursor.fetchall()
    
    user_list = []
    for user in users:
        user_dict = {}
        for i, col in enumerate(select_cols):
            if i < len(user):
                if col == 'created_at' and user[i]:
                    user_dict[col] = user[i].isoformat()
                else:
                    user_dict[col] = user[i]
            else:
                user_dict[col] = None
        user_list.append(user_dict)
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps(user_list)
    }

def create_user(event, cors_headers):
    admin = verify_admin(event)
    if not admin:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Admin access required'})
        }
    
    data = json.loads(event['body'])
    username = data.get('username')
    password = data.get('password', 'temp123')
    email = data.get('email')
    role = data.get('role', 'user')
    permissions = data.get('permissions', 'chat')
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check which columns exist
        cursor.execute("SHOW COLUMNS FROM chatbot_users")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Build insert query based on available columns
        insert_cols = ['username', 'password', 'role']
        insert_vals = [username, hashed_password, role]
        
        if 'email' in columns and email:
            insert_cols.append('email')
            insert_vals.append(email)
        if 'permissions' in columns:
            insert_cols.append('permissions')
            insert_vals.append(permissions)
        
        placeholders = ', '.join(['%s'] * len(insert_vals))
        cursor.execute(f"""
            INSERT INTO chatbot_users ({', '.join(insert_cols)}) 
            VALUES ({placeholders})
        """, insert_vals)
        conn.commit()
        
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({'message': 'User created successfully'})
        }
    except pymysql.IntegrityError:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Username already exists'})
        }

def update_user(event, cors_headers):
    admin = verify_admin(event)
    if not admin:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Admin access required'})
        }
    
    data = json.loads(event['body'])
    user_id = data.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check which columns exist
    cursor.execute("SHOW COLUMNS FROM chatbot_users")
    columns = [col[0] for col in cursor.fetchall()]
    
    updates = []
    values = []
    
    if 'email' in data and 'email' in columns:
        updates.append('email = %s')
        values.append(data['email'])
    if 'role' in data:
        updates.append('role = %s')
        values.append(data['role'])
    if 'status' in data and 'status' in columns:
        updates.append('status = %s')
        values.append(data['status'])
    if 'permissions' in data and 'permissions' in columns:
        updates.append('permissions = %s')
        values.append(data['permissions'])
    if 'password' in data:
        updates.append('password = %s')
        values.append(hashlib.sha256(data['password'].encode()).hexdigest())
    
    if updates:
        values.append(user_id)
        cursor.execute(f"UPDATE chatbot_users SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'message': 'User updated successfully'})
    }

def delete_user(event, cors_headers):
    admin = verify_admin(event)
    if not admin:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Admin access required'})
        }
    
    query_params = event.get('queryStringParameters', {}) or {}
    user_id = query_params.get('id')
    
    if not user_id:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'User ID required'})
        }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM chatbot_config WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM chatbot_users WHERE id = %s", (user_id,))
    conn.commit()
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'message': 'User deleted successfully'})
    }
