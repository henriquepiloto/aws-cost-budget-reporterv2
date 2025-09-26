#!/usr/bin/env python3
import json
import boto3
import pymysql
from datetime import datetime, timedelta
import calendar
import os

def get_database_credentials():
    """Recupera credenciais do banco de dados do AWS Secrets Manager"""
    secret_name = "glpidatabaseadmin"
    region_name = "us-east-1"
    
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        print(f"✓ Credenciais carregadas do Secrets Manager: {secret_name}")
        return {
            'host': secret.get('host', 'glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com'),
            'username': secret['username'],
            'password': secret['password'],
            'port': secret.get('port', 3306),
            'dbname': secret.get('dbname', 'aws_costs')
        }
    except Exception as e:
        print(f"✗ Erro ao carregar credenciais do Secrets Manager: {e}")
        raise

def load_roles_from_s3():
    """Carrega o arquivo roles.json diretamente do S3"""
    s3_roles_uri = os.environ.get('S3_ROLES_URI')
    if not s3_roles_uri:
        raise ValueError("Variável de ambiente S3_ROLES_URI não definida")
    
    # Parse S3 URI (s3://bucket/key)
    if not s3_roles_uri.startswith('s3://'):
        raise ValueError("S3_ROLES_URI deve começar com 's3://'")
    
    uri_parts = s3_roles_uri[5:].split('/', 1)
    bucket_name = uri_parts[0]
    object_key = uri_parts[1] if len(uri_parts) > 1 else 'roles.json'
    
    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        roles_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"✓ Roles carregadas do S3: {s3_roles_uri}")
        return roles_data
    except Exception as e:
        print(f"✗ Erro ao carregar roles do S3: {e}")
        raise

def setup_database(db_config):
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        port=db_config['port'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS aws_costs")
    conn.close()
    
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente VARCHAR(100),
            account_id VARCHAR(20),
            mes_anterior DECIMAL(10,2),
            atual_mtd DECIMAL(10,2),
            projecao DECIMAL(10,2),
            data_relatorio DATE,
            mes_referencia VARCHAR(7),
            ano_mes_anterior VARCHAR(7),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_report (cliente, account_id, data_relatorio)
        )""")
    cursor.execute("CREATE INDEX idx_mes_referencia ON cost_reports(mes_referencia)")
    cursor.execute("CREATE INDEX idx_cliente_data ON cost_reports(cliente, data_relatorio)")
    conn.commit()
    conn.close()

def save_to_mysql(cost_data, db_config):
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    today = datetime.now().date()
    mes_atual = datetime.now().strftime('%Y-%m')
    now = datetime.now()
    first_day_current = now.replace(day=1)
    last_day_previous = first_day_current - timedelta(days=1)
    mes_anterior = last_day_previous.strftime('%Y-%m')
    cursor.execute("DELETE FROM cost_reports WHERE data_relatorio = %s AND mes_referencia = %s", (today, mes_atual))
    for record in cost_data:
        cursor.execute("""
            INSERT INTO cost_reports 
            (cliente, account_id, mes_anterior, atual_mtd, projecao, data_relatorio, mes_referencia, ano_mes_anterior)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                mes_anterior = VALUES(mes_anterior),
                atual_mtd = VALUES(atual_mtd),
                projecao = VALUES(projecao),
                mes_referencia = VALUES(mes_referencia),
                ano_mes_anterior = VALUES(ano_mes_anterior),
                created_at = CURRENT_TIMESTAMP""", (
            record['cliente'], record['account_id'], record['mes_anterior'],
            record['atual_mtd'], record['projecao'], today, mes_atual, mes_anterior))
    conn.commit()
    conn.close()

def assume_role(account_id, role_name):
    try:
        sts_client = boto3.client('sts', region_name='us-east-1')
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"cost-report-{account_id}")
        credentials = response['Credentials']
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    except: return None

def get_cost_data(session, start_date, end_date):
    try:
        ce_client = session.client('ce', region_name='us-east-1')
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY', Metrics=['BlendedCost'])
        total_cost = sum(float(result['Total']['BlendedCost']['Amount']) for result in response['ResultsByTime'])
        return round(total_cost, 2)
    except: return 0

def get_current_month_cost(session):
    try:
        ce_client = session.client('ce', region_name='us-east-1')
        now = datetime.now()
        start_current = now.replace(day=1).strftime('%Y-%m-%d')
        end_current = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_current, 'End': end_current},
            Granularity='DAILY', Metrics=['BlendedCost'])
        total_cost = sum(float(result['Total']['BlendedCost']['Amount']) for result in response['ResultsByTime'])
        days_elapsed = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        if days_elapsed > 0:
            projected_cost = (total_cost / days_elapsed) * days_in_month
        else: projected_cost = total_cost
        return round(total_cost, 2), round(projected_cost, 2)
    except: return 0, 0

def main():
    # Carrega credenciais do Secrets Manager
    db_config = get_database_credentials()
    print(f"Conectando no MySQL: {db_config['host']}")
    setup_database(db_config)
    
    # Carrega roles do S3 ao invés de arquivo local
    roles_data = load_roles_from_s3()
    
    now = datetime.now()
    first_day_current = now.replace(day=1)
    last_day_previous = first_day_current - timedelta(days=1)
    first_day_previous = last_day_previous.replace(day=1)
    start_previous = first_day_previous.strftime('%Y-%m-%d')
    end_previous = (last_day_previous + timedelta(days=1)).strftime('%Y-%m-%d')
    cost_data = []
    print("Coletando dados de custos...")
    for role in roles_data:
        session = assume_role(role['account_id'], role['role_name'])
        if not session: continue
        previous_cost = get_cost_data(session, start_previous, end_previous)
        current_mtd, projected = get_current_month_cost(session)
        cost_data.append({
            'cliente': role['cliente'], 'account_id': role['account_id'],
            'mes_anterior': previous_cost, 'atual_mtd': current_mtd, 'projecao': projected})
        print(f"✓ {role['cliente']} - {role['account_id']}")
    save_to_mysql(cost_data, db_config)
    print(f"✓ Dados salvos no MySQL: {len(cost_data)} registros")

if __name__ == "__main__":
    main()
