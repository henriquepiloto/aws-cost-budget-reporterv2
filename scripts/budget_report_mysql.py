#!/usr/bin/env python3
import json
import boto3
import pymysql
from datetime import datetime
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

def setup_budget_table(db_config):
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database="aws_costs", 
        port=db_config['port'],
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente VARCHAR(100),
            account_id VARCHAR(20),
            budget_name VARCHAR(200),
            budget_limit DECIMAL(10,2),
            actual_spend DECIMAL(10,2),
            forecasted_spend DECIMAL(10,2),
            percentage_used DECIMAL(5,2),
            alert_threshold DECIMAL(5,2),
            alert_triggered BOOLEAN,
            time_period VARCHAR(20),
            data_coleta DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_budget (cliente, account_id, budget_name, data_coleta)
        )""")
    conn.commit()
    conn.close()

def get_budgets_data(session, account_id):
    try:
        budgets_client = session.client("budgets", region_name="us-east-1")
        response = budgets_client.describe_budgets(AccountId=account_id)
        budgets_data = []
        
        for budget in response["Budgets"]:
            budget_name = budget["BudgetName"]
            budget_limit = float(budget["BudgetLimit"]["Amount"])
            time_period = budget["TimeUnit"]
            
            actual_spend = 0
            forecasted_spend = 0
            
            if "ActualSpend" in budget:
                actual_spend = float(budget["ActualSpend"]["Amount"])
            if "ForecastedSpend" in budget:
                forecasted_spend = float(budget["ForecastedSpend"]["Amount"])
            
            percentage_used = (actual_spend / budget_limit * 100) if budget_limit > 0 else 0
            
            alert_threshold = 80
            alert_triggered = percentage_used > alert_threshold
            
            budgets_data.append({
                "budget_name": budget_name,
                "budget_limit": budget_limit,
                "actual_spend": actual_spend,
                "forecasted_spend": forecasted_spend,
                "percentage_used": round(percentage_used, 2),
                "alert_threshold": alert_threshold,
                "alert_triggered": alert_triggered,
                "time_period": time_period
            })
            
        return budgets_data
        
    except Exception as e:
        return []

def assume_role(account_id, role_name):
    try:
        sts_client = boto3.client("sts", region_name="us-east-1")
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"budget-report-{account_id}")
        credentials = response["Credentials"]
        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"])
    except: return None

def save_budgets_to_mysql(budget_data, db_config):
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database="aws_costs", 
        port=db_config['port'],
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    today = datetime.now().date()
    
    cursor.execute("DELETE FROM budget_alerts WHERE data_coleta = %s", (today,))
    
    for record in budget_data:
        cursor.execute("""
            INSERT INTO budget_alerts 
            (cliente, account_id, budget_name, budget_limit, actual_spend, forecasted_spend, 
             percentage_used, alert_threshold, alert_triggered, time_period, data_coleta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
            record["cliente"], record["account_id"], record["budget_name"],
            record["budget_limit"], record["actual_spend"], record["forecasted_spend"],
            record["percentage_used"], record["alert_threshold"], record["alert_triggered"],
            record["time_period"], today))
    
    conn.commit()
    conn.close()

def main():
    # Carrega credenciais do Secrets Manager
    db_config = get_database_credentials()
    print(f"Conectando no MySQL: {db_config['host']}")
    setup_budget_table(db_config)
    
    # Carrega roles do S3 ao invés de arquivo local
    roles_data = load_roles_from_s3()
    
    budget_data = []
    print("Coletando dados de budgets...")
    
    for role in roles_data:
        session = assume_role(role["account_id"], role["role_name"])
        if not session: 
            continue
            
        budgets = get_budgets_data(session, role["account_id"])
        
        for budget in budgets:
            budget["cliente"] = role["cliente"]
            budget["account_id"] = role["account_id"]
            budget_data.append(budget)
            
        print(f"✓ {role["cliente"]} - {role["account_id"]} - {len(budgets)} budgets")
    
    save_budgets_to_mysql(budget_data, db_config)
    print(f"✓ Dados de budget salvos no MySQL: {len(budget_data)} registros")

if __name__ == "__main__":
    main()
