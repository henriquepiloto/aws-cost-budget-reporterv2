import boto3
import pymysql
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_db_credentials():
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = secrets_client.get_secret_value(SecretId='cost-reporter-db-credentials')
    return json.loads(secret['SecretString'])

def collect_cost_data():
    db_creds = get_db_credentials()
    
    host_port = db_creds['host'].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    
    connection = pymysql.connect(
        host=host,
        port=port,
        user=db_creds['username'],
        password=db_creds['password'],
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS cost_reporter")
            cursor.execute("USE cost_reporter")
            
            # Create monthly costs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monthly_costs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    month_year VARCHAR(7) NOT NULL,
                    total_cost DECIMAL(12,4) NOT NULL,
                    forecasted_cost DECIMAL(12,4),
                    currency VARCHAR(3) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_month (month_year)
                )
            """)
            
            # Create current month tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS current_month_costs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    daily_cost DECIMAL(12,4) NOT NULL,
                    month_to_date DECIMAL(12,4) NOT NULL,
                    forecasted_month DECIMAL(12,4),
                    currency VARCHAR(3) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_date (date)
                )
            """)
            
            ce = boto3.client('ce', region_name='us-east-1')
            
            today = datetime.now().date()
            
            # 1. Collect last 6 months costs
            for i in range(6):
                month_start = (today.replace(day=1) - relativedelta(months=i))
                month_end = month_start + relativedelta(months=1)
                
                response = ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': month_start.strftime('%Y-%m-%d'),
                        'End': month_end.strftime('%Y-%m-%d')
                    },
                    Granularity='MONTHLY',
                    Metrics=['BlendedCost']
                )
                
                if response['ResultsByTime']:
                    result = response['ResultsByTime'][0]
                    cost = float(result['Total']['BlendedCost']['Amount'])
                    month_year = month_start.strftime('%Y-%m')
                    
                    cursor.execute("""
                        INSERT INTO monthly_costs (month_year, total_cost, currency)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        total_cost = VALUES(total_cost)
                    """, (month_year, cost, 'USD'))
            
            # 2. Current month daily tracking
            month_start = today.replace(day=1)
            
            # Get daily costs for current month
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': month_start.strftime('%Y-%m-%d'),
                    'End': today.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            
            month_to_date = 0
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                daily_cost = float(result['Total']['BlendedCost']['Amount'])
                month_to_date += daily_cost
                
                cursor.execute("""
                    INSERT INTO current_month_costs (date, daily_cost, month_to_date, currency)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    daily_cost = VALUES(daily_cost),
                    month_to_date = VALUES(month_to_date)
                """, (date, daily_cost, month_to_date, 'USD'))
            
            connection.commit()
            print(f"Collected cost data for chat context: {today}")
            
    finally:
        connection.close()

if __name__ == "__main__":
    collect_cost_data()
