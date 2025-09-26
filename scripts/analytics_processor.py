#!/usr/bin/env python3
"""
Analytics Processor - Fase 1
Processa dados coletados e gera métricas e tendências
"""

import json
import boto3
import pymysql
from datetime import datetime, timedelta
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
        
        return {
            'host': secret.get('host'),
            'username': secret['username'],
            'password': secret['password'],
            'port': secret.get('port', 3306),
            'dbname': secret.get('dbname', 'aws_costs')
        }
    except Exception as e:
        print(f"✗ Erro ao carregar credenciais: {e}")
        raise

def calculate_growth_rates(db_config):
    """Calcula taxas de crescimento mês a mês"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Calcular growth rate comparando com mês anterior
    cursor.execute("""
        UPDATE monthly_service_costs msc1
        JOIN monthly_service_costs msc2 ON 
            msc1.cliente = msc2.cliente AND
            msc1.account_id = msc2.account_id AND
            msc1.service_name = msc2.service_name AND
            msc1.region = msc2.region AND
            DATE_ADD(STR_TO_DATE(CONCAT(msc2.year_month, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH) = 
            STR_TO_DATE(CONCAT(msc1.year_month, '-01'), '%Y-%m-%d')
        SET msc1.growth_rate = 
            CASE 
                WHEN msc2.total_cost > 0 THEN 
                    ((msc1.total_cost - msc2.total_cost) / msc2.total_cost) * 100
                ELSE NULL
            END
        WHERE msc1.growth_rate IS NULL
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Taxas de crescimento calculadas")

def generate_cost_metrics(db_config):
    """Gera métricas agregadas para análise"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    
    # Limpar métricas do mês atual
    cursor.execute("DELETE FROM cost_metrics WHERE metric_period = %s", (current_month,))
    
    # Métrica: Total mensal por cliente
    cursor.execute("""
        INSERT INTO cost_metrics (cliente, account_id, metric_type, metric_period, metric_value)
        SELECT 
            cliente,
            account_id,
            'total_monthly',
            year_month,
            SUM(total_cost)
        FROM monthly_service_costs 
        WHERE year_month = %s
        GROUP BY cliente, account_id, year_month
    """, (current_month,))
    
    # Métrica: Serviço com maior custo por cliente
    cursor.execute("""
        INSERT INTO cost_metrics (cliente, account_id, metric_type, metric_period, metric_value, metric_text)
        SELECT 
            cliente,
            account_id,
            'top_service',
            year_month,
            MAX(total_cost),
            (SELECT service_name FROM monthly_service_costs msc2 
             WHERE msc2.cliente = msc1.cliente AND msc2.account_id = msc1.account_id 
             AND msc2.year_month = msc1.year_month
             ORDER BY total_cost DESC LIMIT 1)
        FROM monthly_service_costs msc1
        WHERE year_month = %s
        GROUP BY cliente, account_id, year_month
    """, (current_month,))
    
    # Métrica: Serviço com maior crescimento
    cursor.execute("""
        INSERT INTO cost_metrics (cliente, account_id, metric_type, metric_period, metric_value, metric_text)
        SELECT 
            cliente,
            account_id,
            'fastest_growing',
            year_month,
            MAX(growth_rate),
            (SELECT service_name FROM monthly_service_costs msc2 
             WHERE msc2.cliente = msc1.cliente AND msc2.account_id = msc1.account_id 
             AND msc2.year_month = msc1.year_month AND msc2.growth_rate IS NOT NULL
             ORDER BY growth_rate DESC LIMIT 1)
        FROM monthly_service_costs msc1
        WHERE year_month = %s AND growth_rate IS NOT NULL
        GROUP BY cliente, account_id, year_month
    """, (current_month,))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Métricas de custo geradas")

def detect_cost_trends(db_config):
    """Detecta tendências e gera alertas"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    
    # Limpar tendências do mês atual
    cursor.execute("DELETE FROM cost_trends WHERE trend_period = %s", (current_month,))
    
    # Detectar serviços com crescimento alto (>50%)
    cursor.execute("""
        INSERT INTO cost_trends 
        (cliente, account_id, service_name, trend_type, trend_period, growth_percentage, alert_level, description)
        SELECT 
            cliente,
            account_id,
            service_name,
            'increasing',
            year_month,
            growth_rate,
            CASE 
                WHEN growth_rate > 100 THEN 'critical'
                WHEN growth_rate > 50 THEN 'high'
                WHEN growth_rate > 20 THEN 'medium'
                ELSE 'low'
            END,
            CONCAT('Serviço ', service_name, ' teve crescimento de ', ROUND(growth_rate, 2), '% no mês')
        FROM monthly_service_costs 
        WHERE year_month = %s AND growth_rate > 20
    """, (current_month,))
    
    # Detectar serviços com custo alto (top 10% por cliente)
    cursor.execute("""
        INSERT INTO cost_trends 
        (cliente, account_id, service_name, trend_type, trend_period, growth_percentage, alert_level, description)
        SELECT 
            cliente,
            account_id,
            service_name,
            'stable',
            year_month,
            0,
            'medium',
            CONCAT('Serviço ', service_name, ' é um dos maiores custos: $', ROUND(total_cost, 2))
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY cliente, account_id ORDER BY total_cost DESC) as cost_rank,
                   COUNT(*) OVER (PARTITION BY cliente, account_id) as total_services
            FROM monthly_service_costs 
            WHERE year_month = %s
        ) ranked
        WHERE cost_rank <= GREATEST(1, total_services * 0.1) AND total_cost > 100
    """, (current_month,))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Tendências e alertas detectados")

def generate_summary_report(db_config):
    """Gera relatório resumo das análises"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    
    print(f"\n📊 RELATÓRIO DE ANÁLISE - {current_month}")
    print("=" * 50)
    
    # Total de custos por cliente
    cursor.execute("""
        SELECT cliente, SUM(metric_value) as total_cost
        FROM cost_metrics 
        WHERE metric_type = 'total_monthly' AND metric_period = %s
        GROUP BY cliente
        ORDER BY total_cost DESC
    """, (current_month,))
    
    print("\n💰 CUSTOS TOTAIS POR CLIENTE:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:,.2f}")
    
    # Alertas críticos
    cursor.execute("""
        SELECT cliente, service_name, growth_percentage, description
        FROM cost_trends 
        WHERE trend_period = %s AND alert_level IN ('critical', 'high')
        ORDER BY growth_percentage DESC
        LIMIT 10
    """, (current_month,))
    
    print("\n🚨 ALERTAS DE CRESCIMENTO:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: +{row[2]:.1f}%")
    
    # Serviços mais caros
    cursor.execute("""
        SELECT cliente, metric_text, metric_value
        FROM cost_metrics 
        WHERE metric_type = 'top_service' AND metric_period = %s
        ORDER BY metric_value DESC
        LIMIT 10
    """, (current_month,))
    
    print("\n📈 SERVIÇOS MAIS CAROS:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: ${row[2]:,.2f}")
    
    cursor.close()
    conn.close()

def main():
    """Função principal do processador de analytics"""
    print("🔍 Iniciando processamento de analytics...")
    
    db_config = get_database_credentials()
    
    # Executar análises
    calculate_growth_rates(db_config)
    generate_cost_metrics(db_config)
    detect_cost_trends(db_config)
    generate_summary_report(db_config)
    
    print("\n✅ Processamento de analytics concluído!")

if __name__ == "__main__":
    main()
