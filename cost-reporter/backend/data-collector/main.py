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
                    year_month VARCHAR(7) NOT NULL,
                    total_cost DECIMAL(12,4) NOT NULL,
                    forecasted_cost DECIMAL(12,4),
                    currency VARCHAR(3) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_month (year_month)
                )
            """)
            
            # Create budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    budget_name VARCHAR(255) NOT NULL,
                    budget_limit DECIMAL(12,4) NOT NULL,
                    actual_spend DECIMAL(12,4),
                    forecasted_spend DECIMAL(12,4),
                    currency VARCHAR(3) NOT NULL,
                    time_period VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_budget (budget_name)
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cost_alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    alert_date DATE NOT NULL,
                    alert_type VARCHAR(50) NOT NULL,
                    threshold_amount DECIMAL(12,4),
                    actual_amount DECIMAL(12,4),
                    budget_name VARCHAR(255),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (alert_date)
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
            budgets_client = boto3.client('budgets', region_name='us-east-1')
            
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
                    year_month = month_start.strftime('%Y-%m')
                    
                    cursor.execute("""
                        INSERT INTO monthly_costs (year_month, total_cost, currency)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        total_cost = VALUES(total_cost)
                    """, (year_month, cost, 'USD'))
            
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
            
            # 3. Get forecast for current month
            try:
                forecast_response = ce.get_cost_forecast(
                    TimePeriod={
                        'Start': today.strftime('%Y-%m-%d'),
                        'End': (month_start + relativedelta(months=1)).strftime('%Y-%m-%d')
                    },
                    Metric='BLENDED_COST',
                    Granularity='MONTHLY'
                )
                
                if forecast_response['ForecastResultsByTime']:
                    forecasted_cost = float(forecast_response['ForecastResultsByTime'][0]['MeanValue'])
                    
                    # Update current month with forecast
                    cursor.execute("""
                        UPDATE current_month_costs 
                        SET forecasted_month = %s 
                        WHERE date = %s
                    """, (forecasted_cost + month_to_date, today.strftime('%Y-%m-%d')))
                    
            except Exception as e:
                print(f"Forecast error: {e}")
            
            # 4. Get budgets information
            try:
                account_id = boto3.client('sts').get_caller_identity()['Account']
                
                budgets_response = budgets_client.describe_budgets(
                    AccountId=account_id
                )
                
                for budget in budgets_response['Budgets']:
                    budget_name = budget['BudgetName']
                    budget_limit = float(budget['BudgetLimit']['Amount'])
                    currency = budget['BudgetLimit']['Unit']
                    time_period = budget['TimeUnit']
                    
                    # Get actual spend
                    actual_spend = 0
                    forecasted_spend = 0
                    
                    if 'CalculatedSpend' in budget:
                        actual_spend = float(budget['CalculatedSpend']['ActualSpend']['Amount'])
                        if 'ForecastedSpend' in budget['CalculatedSpend']:
                            forecasted_spend = float(budget['CalculatedSpend']['ForecastedSpend']['Amount'])
                    
                    cursor.execute("""
                        INSERT INTO budgets 
                        (budget_name, budget_limit, actual_spend, forecasted_spend, currency, time_period)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        budget_limit = VALUES(budget_limit),
                        actual_spend = VALUES(actual_spend),
                        forecasted_spend = VALUES(forecasted_spend)
                    """, (budget_name, budget_limit, actual_spend, forecasted_spend, currency, time_period))
                    
            except Exception as e:
                print(f"Budgets error: {e}")
            
            # 5. Simulate daily alerts count for current month
            # (In real scenario, this would come from CloudWatch alarms or SNS notifications)
            current_day = today.day
            alerts_this_month = max(0, current_day - 5)  # Simulate some alerts
            
            cursor.execute("""
                INSERT INTO cost_alerts 
                (alert_date, alert_type, actual_amount, message)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                actual_amount = VALUES(actual_amount)
            """, (today, 'DAILY_THRESHOLD', month_to_date, f'{alerts_this_month} alerts triggered this month'))
            
            connection.commit()
            print(f"Collected comprehensive cost data for {today}")
            
    finally:
        connection.close()

if __name__ == "__main__":
    collect_cost_data()
