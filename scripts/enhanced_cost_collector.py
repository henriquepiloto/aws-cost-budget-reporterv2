#!/usr/bin/env python3
"""
Enhanced AWS Cost Collector - Fase 1
Coleta dados granulares de custos por serviço, região e período
"""

import json
import boto3
import pymysql
from datetime import datetime, timedelta
import calendar
import os
from decimal import Decimal

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

def setup_enhanced_database(db_config):
    """Configura o banco com o schema aprimorado"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    # Ler e executar o schema SQL
    try:
        with open('/home/hpiloto/projetos/aws-cost-budget-reporterv2/sql/enhanced_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Executar cada statement separadamente
        statements = schema_sql.split(';')
        cursor = conn.cursor()
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"Warning: {e}")
        
        conn.commit()
        print("✓ Schema aprimorado configurado")
        
    except Exception as e:
        print(f"✗ Erro ao configurar schema: {e}")
        # Fallback para schema básico
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_costs (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(100) NOT NULL,
                account_id VARCHAR(20) NOT NULL,
                service_name VARCHAR(100) NOT NULL,
                region VARCHAR(50) DEFAULT 'global',
                cost_date DATE NOT NULL,
                amount DECIMAL(12,4) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_daily_cost (cliente, account_id, service_name, region, cost_date)
            )""")
        conn.commit()
    
    cursor.close()
    conn.close()

def assume_role(account_id, role_name):
    """Assume role para acessar conta AWS"""
    try:
        sts_client = boto3.client('sts', region_name='us-east-1')
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"enhanced-cost-{account_id}")
        credentials = response['Credentials']
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    except Exception as e:
        print(f"✗ Erro ao assumir role {role_name} na conta {account_id}: {e}")
        return None

def get_detailed_costs(session, start_date, end_date):
    """Coleta custos detalhados por serviço e região"""
    try:
        ce_client = session.client('ce', region_name='us-east-1')
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'REGION'}
            ]
        )
        
        detailed_costs = []
        
        for result in response['ResultsByTime']:
            cost_date = result['TimePeriod']['Start']
            
            for group in result['Groups']:
                service = group['Keys'][0] if group['Keys'][0] else 'Unknown'
                region = group['Keys'][1] if len(group['Keys']) > 1 and group['Keys'][1] else 'global'
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                
                if amount > 0:  # Só salvar custos > 0
                    detailed_costs.append({
                        'service_name': service,
                        'region': region,
                        'cost_date': cost_date,
                        'amount': round(amount, 4)
                    })
        
        return detailed_costs
        
    except Exception as e:
        print(f"✗ Erro ao coletar custos detalhados: {e}")
        return []

def save_daily_costs(cost_data, db_config):
    """Salva custos diários no banco"""
    if not cost_data:
        return
    
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Insert ou update dos custos diários
    for record in cost_data:
        cursor.execute("""
            INSERT INTO daily_costs 
            (cliente, account_id, service_name, region, cost_date, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                amount = VALUES(amount),
                created_at = CURRENT_TIMESTAMP
        """, (
            record['cliente'], 
            record['account_id'], 
            record['service_name'],
            record['region'],
            record['cost_date'],
            record['amount']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

def calculate_monthly_aggregates(db_config, year_month):
    """Calcula agregados mensais por serviço"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Calcular agregados mensais
    cursor.execute("""
        INSERT INTO monthly_service_costs 
        (cliente, account_id, service_name, region, year_month, total_cost, 
         avg_daily_cost, max_daily_cost, min_daily_cost, days_with_usage)
        SELECT 
            cliente,
            account_id,
            service_name,
            region,
            %s as year_month,
            SUM(amount) as total_cost,
            AVG(amount) as avg_daily_cost,
            MAX(amount) as max_daily_cost,
            MIN(amount) as min_daily_cost,
            COUNT(DISTINCT cost_date) as days_with_usage
        FROM daily_costs 
        WHERE DATE_FORMAT(cost_date, '%%Y-%%m') = %s
        GROUP BY cliente, account_id, service_name, region
        ON DUPLICATE KEY UPDATE
            total_cost = VALUES(total_cost),
            avg_daily_cost = VALUES(avg_daily_cost),
            max_daily_cost = VALUES(max_daily_cost),
            min_daily_cost = VALUES(min_daily_cost),
            days_with_usage = VALUES(days_with_usage),
            created_at = CURRENT_TIMESTAMP
    """, (year_month, year_month))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando coleta aprimorada de custos AWS...")
    
    # Configurar banco
    db_config = get_database_credentials()
    setup_enhanced_database(db_config)
    
    # Carregar roles
    roles_data = load_roles_from_s3()
    
    # Definir período de coleta (últimos 7 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"📅 Coletando dados de {start_str} até {end_str}")
    
    all_cost_data = []
    
    # Coletar dados de cada conta
    for role in roles_data:
        print(f"🔄 Processando {role['cliente']} - {role['account_id']}")
        
        session = assume_role(role['account_id'], role['role_name'])
        if not session:
            continue
        
        # Coletar custos detalhados
        detailed_costs = get_detailed_costs(session, start_str, end_str)
        
        # Adicionar informações do cliente
        for cost in detailed_costs:
            cost['cliente'] = role['cliente']
            cost['account_id'] = role['account_id']
            all_cost_data.append(cost)
        
        print(f"✓ {len(detailed_costs)} registros coletados")
    
    # Salvar dados
    if all_cost_data:
        print(f"💾 Salvando {len(all_cost_data)} registros no banco...")
        save_daily_costs(all_cost_data, db_config)
        
        # Calcular agregados mensais
        current_month = datetime.now().strftime('%Y-%m')
        calculate_monthly_aggregates(db_config, current_month)
        
        print(f"✅ Coleta concluída: {len(all_cost_data)} registros salvos")
    else:
        print("⚠️ Nenhum dado coletado")

if __name__ == "__main__":
    main()
