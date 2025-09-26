"""
Prisma Cost Intelligence Platform - Backend API
Cloudinho AI Assistant with authentication and admin panel
"""

import json
import boto3
import hashlib
import jwt
import pymysql
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

def hash_password(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.db_config = {
            'host': 'glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com',
            'user': 'admin',
            'password': 'glpi123456',
            'database': 'prisma_cost_intelligence',
            'port': 3306,
            'charset': 'utf8mb4'
        }
        
    def get_connection(self):
        try:
            connection = pymysql.connect(**self.db_config)
            logger.info("Database connection established to existing RDS")
            return connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def init_tables(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS prisma_cost_intelligence")
            cursor.execute("USE prisma_cost_intelligence")
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'user') DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Chat configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_config (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    primary_color VARCHAR(7) DEFAULT '#3b82f6',
                    secondary_color VARCHAR(7) DEFAULT '#1e40af',
                    bot_name VARCHAR(100) DEFAULT 'Cloudinho',
                    welcome_message TEXT DEFAULT 'Olá! Sou o Cloudinho, seu assistente de análise de custos AWS. Como posso ajudar você hoje?',
                    company_name VARCHAR(255) DEFAULT 'Select Soluções',
                    theme ENUM('light', 'dark') DEFAULT 'light',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default admin user if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('admin@selectsolucoes.com',))
            if cursor.fetchone()[0] == 0:
                admin_password = hash_password('password')
                cursor.execute("""
                    INSERT INTO users (id, email, password, name, role, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('1', 'admin@selectsolucoes.com', admin_password, 'Administrador', 'admin', datetime.now()))
                logger.info("Default admin user created")
            
            # Insert default chat config if not exists
            cursor.execute("SELECT COUNT(*) FROM chat_config")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO chat_config (primary_color, secondary_color, bot_name, welcome_message, company_name, theme)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('#3b82f6', '#1e40af', 'Cloudinho', 
                     'Olá! Sou o Cloudinho, seu assistente de análise de custos AWS. Como posso ajudar você hoje?',
                     'Select Soluções', 'light'))
                logger.info("Default chat config created")
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing tables: {str(e)}")
            raise

# Global database manager
db_manager = DatabaseManager()

class CloudinhoAssistant:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        
    def ask(self, question: str) -> str:
        try:
            logger.info(f"Processing question: {question[:100]}...")
            
            # Contexto específico para custos AWS
            system_prompt = """Você é o Cloudinho, assistente especializado em FinOps e análise de custos AWS da Select Soluções.

CONTEXTO ATUAL:
- Cliente: 2ABrasil (exemplo mencionado)
- Especialidade: Otimização de custos AWS
- Foco: Análise financeira, recomendações práticas

Responda de forma:
- Executiva e objetiva
- Com dados específicos quando possível
- Recomendações acionáveis
- Em português brasileiro"""
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1000,
                    'system': system_prompt,
                    'messages': [{'role': 'user', 'content': question}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            logger.info(f"Generated response: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Cloudinho error: {str(e)}")
            return f"Olá! Sou o Cloudinho, seu assistente de custos AWS. No momento estou com dificuldades técnicas, mas posso ajudar com análise de custos, otimização e recomendações para AWS. Como posso ajudar você?"

def lambda_handler(event, context):
    global db_manager
    
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body')
        
        logger.info(f"Method: {http_method}, Path: {path}")
        
        request_data = {}
        if body:
            try:
                request_data = json.loads(body)
                logger.info(f"Request data: {json.dumps(request_data, default=str)}")
            except Exception as e:
                logger.error(f"Error parsing body: {str(e)}")
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        }
        
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS preflight'})}
        
        cloudinho = CloudinhoAssistant()
        
        # Route requests
        if path == '/chat':
            message = request_data.get('message', '')
            if not message:
                return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Message is required'})}
            
            response = cloudinho.ask(message)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'response': response, 'timestamp': datetime.now().isoformat()})
            }
        
        elif path == '/chat/config':
            # Return default config
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "config": {
                        "primaryColor": "#3b82f6",
                        "secondaryColor": "#1e40af",
                        "botName": "Cloudinho",
                        "welcomeMessage": "Olá! Sou o Cloudinho, seu assistente de análise de custos AWS. Como posso ajudar você hoje?",
                        "theme": "light"
                    }
                })
            }
        
        else:
            logger.warning(f"Unknown path: {path}")
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Endpoint not found'})}
    
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error', 'message': str(e)})
        }

def handler(event, context):
    return lambda_handler(event, context)
