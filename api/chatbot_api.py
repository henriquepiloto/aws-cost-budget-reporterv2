#!/usr/bin/env python3
"""
Chatbot API - Fase 2
API REST para consultas de custos via chatbot
"""

from flask import Flask, request, jsonify
import pymysql
import json
import boto3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def get_database_credentials():
    """Recupera credenciais do banco de dados do AWS Secrets Manager"""
    secret_name = "glpidatabaseadmin"
    region_name = "us-east-1"
    
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        return {
            'host': secret.get('host'),
            'username': secret['username'],
            'password': secret['password'],
            'port': secret.get('port', 3306),
            'dbname': secret.get('dbname', 'aws_costs')
        }
    except Exception as e:
        return None

def get_db_connection():
    """Cria conexão com o banco"""
    db_config = get_database_credentials()
    if not db_config:
        return None
    
    return pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/costs/monthly/<cliente>', methods=['GET'])
def get_monthly_costs(cliente):
    """Retorna custos mensais de um cliente"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Últimos 6 meses
        cursor.execute("""
            SELECT 
                year_month,
                SUM(total_cost) as monthly_total,
                COUNT(DISTINCT service_name) as services_count
            FROM monthly_service_costs 
            WHERE cliente = %s 
            AND year_month >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 6 MONTH), '%%Y-%%m')
            GROUP BY year_month
            ORDER BY year_month DESC
        """, (cliente,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "monthly_costs": results,
            "total_months": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/costs/top-services/<cliente>', methods=['GET'])
def get_top_services(cliente):
    """Retorna top serviços por custo de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_month = datetime.now().strftime('%Y-%m')
        limit = request.args.get('limit', 10)
        
        cursor.execute("""
            SELECT 
                service_name,
                SUM(total_cost) as service_cost,
                AVG(growth_rate) as avg_growth_rate,
                COUNT(DISTINCT account_id) as accounts_count
            FROM monthly_service_costs 
            WHERE cliente = %s AND year_month = %s
            GROUP BY service_name
            ORDER BY service_cost DESC
            LIMIT %s
        """, (cliente, current_month, int(limit)))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "month": current_month,
            "top_services": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/costs/daily/<cliente>', methods=['GET'])
def get_daily_costs(cliente):
    """Retorna custos diários de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        days = int(request.args.get('days', 30))
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                cost_date,
                SUM(amount) as daily_total,
                COUNT(DISTINCT service_name) as services_count
            FROM daily_costs 
            WHERE cliente = %s AND cost_date >= %s
            GROUP BY cost_date
            ORDER BY cost_date DESC
        """, (cliente, start_date))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "period_days": days,
            "daily_costs": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/<cliente>', methods=['GET'])
def get_alerts(cliente):
    """Retorna alertas de custo de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                service_name,
                trend_type,
                growth_percentage,
                alert_level,
                description,
                created_at
            FROM cost_trends 
            WHERE cliente = %s 
            AND alert_level IN ('medium', 'high', 'critical')
            ORDER BY 
                CASE alert_level 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                END,
                growth_percentage DESC
            LIMIT 20
        """, (cliente,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "alerts": results,
            "total_alerts": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecasts/<cliente>', methods=['GET'])
def get_forecasts(cliente):
    """Retorna previsões de custo de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                service_name,
                forecast_period,
                predicted_cost,
                confidence_interval_lower,
                confidence_interval_upper,
                prediction_accuracy,
                trend_direction,
                growth_rate
            FROM cost_forecasts 
            WHERE cliente = %s 
            ORDER BY forecast_period, predicted_cost DESC
        """, (cliente,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "forecasts": results,
            "total_forecasts": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/savings/<cliente>', methods=['GET'])
def get_savings_opportunities(cliente):
    """Retorna oportunidades de economia de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Rightsizing opportunities
        cursor.execute("""
            SELECT 
                'Rightsizing' as opportunity_type,
                resource_id,
                current_instance_type,
                recommended_instance_type,
                estimated_savings,
                savings_percentage,
                confidence_level
            FROM rightsizing_recommendations 
            WHERE cliente = %s AND status = 'Active'
            ORDER BY estimated_savings DESC
            LIMIT 10
        """, (cliente,))
        
        rightsizing = cursor.fetchall()
        
        # RI utilization
        cursor.execute("""
            SELECT 
                'RI Optimization' as opportunity_type,
                ri_id,
                instance_type,
                utilization_percentage,
                (fixed_price * (100 - COALESCE(utilization_percentage, 0)) / 100) as potential_savings
            FROM reserved_instances 
            WHERE cliente = %s AND state = 'active' 
            AND COALESCE(utilization_percentage, 0) < 80
            ORDER BY potential_savings DESC
            LIMIT 10
        """, (cliente,))
        
        ri_optimization = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "rightsizing_opportunities": rightsizing,
            "ri_optimization": ri_optimization,
            "total_opportunities": len(rightsizing) + len(ri_optimization)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/<cliente>', methods=['GET'])
def get_client_summary(cliente):
    """Retorna resumo completo de um cliente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_month = datetime.now().strftime('%Y-%m')
        
        # Custo total atual
        cursor.execute("""
            SELECT SUM(total_cost) as current_month_total
            FROM monthly_service_costs 
            WHERE cliente = %s AND year_month = %s
        """, (cliente, current_month))
        
        current_total = cursor.fetchone()['current_month_total'] or 0
        
        # Top 3 serviços
        cursor.execute("""
            SELECT service_name, total_cost
            FROM monthly_service_costs 
            WHERE cliente = %s AND year_month = %s
            ORDER BY total_cost DESC
            LIMIT 3
        """, (cliente, current_month))
        
        top_services = cursor.fetchall()
        
        # Alertas críticos
        cursor.execute("""
            SELECT COUNT(*) as critical_alerts
            FROM cost_trends 
            WHERE cliente = %s AND alert_level IN ('high', 'critical')
        """, (cliente,))
        
        critical_alerts = cursor.fetchone()['critical_alerts']
        
        # Economia potencial
        cursor.execute("""
            SELECT SUM(estimated_savings) as potential_savings
            FROM rightsizing_recommendations 
            WHERE cliente = %s AND status = 'Active'
        """, (cliente,))
        
        potential_savings = cursor.fetchone()['potential_savings'] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "cliente": cliente,
            "current_month": current_month,
            "current_month_total": float(current_total),
            "top_services": top_services,
            "critical_alerts": critical_alerts,
            "potential_savings": float(potential_savings),
            "summary_generated_at": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def natural_language_query():
    """Endpoint para consultas em linguagem natural"""
    try:
        data = request.get_json()
        query = data.get('query', '').lower()
        cliente = data.get('cliente', '')
        
        # Mapeamento simples de consultas
        if 'custo total' in query or 'gasto total' in query:
            return get_client_summary(cliente)
        elif 'serviços mais caros' in query or 'top serviços' in query:
            return get_top_services(cliente)
        elif 'alertas' in query or 'problemas' in query:
            return get_alerts(cliente)
        elif 'previsão' in query or 'forecast' in query:
            return get_forecasts(cliente)
        elif 'economia' in query or 'savings' in query:
            return get_savings_opportunities(cliente)
        elif 'diário' in query or 'últimos dias' in query:
            return get_daily_costs(cliente)
        else:
            return jsonify({
                "message": "Consulta não reconhecida. Tente: 'custo total', 'top serviços', 'alertas', 'previsão', 'economia'",
                "available_queries": [
                    "Qual o custo total?",
                    "Quais os serviços mais caros?",
                    "Há alertas de custo?",
                    "Qual a previsão para próximo mês?",
                    "Quais oportunidades de economia?"
                ]
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
