from fastapi import FastAPI
import boto3
import pymysql
import json

app = FastAPI(title="Cost Reporter API - Complete Analytics")

def get_db_credentials():
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = secrets_client.get_secret_value(SecretId='cost-reporter-db-credentials')
    return json.loads(secret['SecretString'])

def get_db_connection():
    db_creds = get_db_credentials()
    host_port = db_creds['host'].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    
    return pymysql.connect(
        host=host,
        port=port,
        user=db_creds['username'],
        password=db_creds['password'],
        database='cost_reporter',
        charset='utf8mb4'
    )

@app.get("/")
def read_root():
    return {
        "message": "Cost Reporter API - Complete Analytics",
        "version": "3.0",
        "features": [
            "monthly_costs_6_months",
            "current_month_tracking", 
            "cost_forecasting",
            "budget_monitoring",
            "daily_alerts_tracking"
        ]
    }

@app.get("/costs/overview")
def get_cost_overview():
    """Complete cost overview with all required metrics"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Last 6 months costs
                cursor.execute("""
                    SELECT year_month, total_cost, forecasted_cost, currency
                    FROM monthly_costs 
                    ORDER BY year_month DESC 
                    LIMIT 6
                """)
                monthly_costs = cursor.fetchall()
                
                # Current month progress
                cursor.execute("""
                    SELECT date, daily_cost, month_to_date, forecasted_month, currency
                    FROM current_month_costs 
                    ORDER BY date DESC 
                    LIMIT 1
                """)
                current_month = cursor.fetchone()
                
                # Budgets
                cursor.execute("""
                    SELECT budget_name, budget_limit, actual_spend, 
                           forecasted_spend, currency, time_period
                    FROM budgets
                """)
                budgets = cursor.fetchall()
                
                # Alerts count this month
                cursor.execute("""
                    SELECT COUNT(*) as alert_count, 
                           MAX(actual_amount) as max_amount,
                           MAX(message) as last_message
                    FROM cost_alerts 
                    WHERE YEAR(alert_date) = YEAR(CURDATE()) 
                    AND MONTH(alert_date) = MONTH(CURDATE())
                """)
                alerts = cursor.fetchone()
                
                return {
                    "monthly_costs_6_months": monthly_costs,
                    "current_month": current_month,
                    "budgets": budgets,
                    "alerts_this_month": alerts
                }
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e)}

@app.get("/costs/monthly")
def get_monthly_costs():
    """Last 6 months costs"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT year_month, total_cost, forecasted_cost, currency, created_at
                    FROM monthly_costs 
                    ORDER BY year_month DESC 
                    LIMIT 6
                """)
                return {"monthly_costs": cursor.fetchall()}
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e), "monthly_costs": []}

@app.get("/costs/current-month")
def get_current_month():
    """Current month daily tracking"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM current_month_costs 
                    ORDER BY date DESC 
                    LIMIT 31
                """)
                return {"current_month": cursor.fetchall()}
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e), "current_month": []}

@app.get("/budgets")
def get_budgets():
    """All budgets with actual and forecasted spend"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT budget_name, budget_limit, actual_spend, 
                           forecasted_spend, currency, time_period,
                           ROUND((actual_spend / budget_limit) * 100, 2) as usage_percentage,
                           ROUND((forecasted_spend / budget_limit) * 100, 2) as forecast_percentage
                    FROM budgets
                    ORDER BY usage_percentage DESC
                """)
                return {"budgets": cursor.fetchall()}
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e), "budgets": []}

@app.get("/alerts")
def get_cost_alerts():
    """Cost alerts for current month"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT alert_date, alert_type, threshold_amount, 
                           actual_amount, budget_name, message
                    FROM cost_alerts 
                    WHERE YEAR(alert_date) = YEAR(CURDATE()) 
                    AND MONTH(alert_date) = MONTH(CURDATE())
                    ORDER BY alert_date DESC
                """)
                alerts = cursor.fetchall()
                
                cursor.execute("""
                    SELECT COUNT(*) as total_alerts_this_month
                    FROM cost_alerts 
                    WHERE YEAR(alert_date) = YEAR(CURDATE()) 
                    AND MONTH(alert_date) = MONTH(CURDATE())
                """)
                count = cursor.fetchone()
                
                return {
                    "alerts": alerts,
                    "summary": count
                }
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e), "alerts": []}

@app.get("/costs")
def get_costs():
    """Legacy endpoint - returns overview"""
    return get_cost_overview()

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "version": "3.0", 
        "features": [
            "monthly_costs_6_months",
            "current_month_tracking", 
            "cost_forecasting",
            "budget_monitoring",
            "daily_alerts_tracking"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
