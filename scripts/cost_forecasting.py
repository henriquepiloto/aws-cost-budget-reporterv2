#!/usr/bin/env python3
"""
Cost Forecasting - Fase 2
Gera previsões de custos usando dados históricos
"""

import json
import boto3
import pymysql
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

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

def get_historical_data(db_config, months_back=6):
    """Recupera dados históricos para previsão"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Buscar dados dos últimos X meses
    cursor.execute("""
        SELECT 
            cliente,
            account_id,
            service_name,
            year_month,
            total_cost,
            STR_TO_DATE(CONCAT(year_month, '-01'), '%Y-%m-%d') as month_date
        FROM monthly_service_costs 
        WHERE year_month >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL %s MONTH), '%%Y-%%m')
        ORDER BY cliente, account_id, service_name, year_month
    """, (months_back,))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def calculate_trend_direction(costs):
    """Calcula direção da tendência"""
    if len(costs) < 2:
        return 'stable'
    
    # Calcular tendência linear
    x = np.arange(len(costs)).reshape(-1, 1)
    y = np.array(costs)
    
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    
    if slope > 0.1:
        return 'increasing'
    elif slope < -0.1:
        return 'decreasing'
    else:
        return 'stable'

def forecast_linear(costs, periods_ahead=3):
    """Previsão linear simples"""
    if len(costs) < 2:
        return costs[-1] if costs else 0, 0.5
    
    x = np.arange(len(costs)).reshape(-1, 1)
    y = np.array(costs)
    
    # Modelo linear
    model = LinearRegression()
    model.fit(x, y)
    
    # Prever próximos períodos
    future_x = np.arange(len(costs), len(costs) + periods_ahead).reshape(-1, 1)
    predictions = model.predict(future_x)
    
    # Calcular R² como medida de confiança
    r2_score = model.score(x, y)
    confidence = max(0.1, min(0.95, r2_score))
    
    return predictions, confidence

def generate_forecasts(db_config):
    """Gera previsões para todos os clientes e serviços"""
    historical_data = get_historical_data(db_config)
    
    # Organizar dados por cliente/conta/serviço
    data_groups = {}
    for row in historical_data:
        cliente, account_id, service_name, year_month, total_cost, month_date = row
        key = (cliente, account_id, service_name)
        
        if key not in data_groups:
            data_groups[key] = []
        
        data_groups[key].append({
            'year_month': year_month,
            'total_cost': float(total_cost),
            'month_date': month_date
        })
    
    forecasts = []
    
    for (cliente, account_id, service_name), data in data_groups.items():
        if len(data) < 3:  # Precisa de pelo menos 3 pontos
            continue
        
        # Ordenar por data
        data.sort(key=lambda x: x['month_date'])
        costs = [d['total_cost'] for d in data]
        
        # Gerar previsões para próximos 3 meses
        predictions, confidence = forecast_linear(costs, 3)
        trend = calculate_trend_direction(costs)
        
        # Calcular taxa de crescimento
        if len(costs) >= 2:
            growth_rate = ((costs[-1] - costs[0]) / costs[0]) * 100 if costs[0] > 0 else 0
        else:
            growth_rate = 0
        
        # Gerar previsões mensais
        current_date = datetime.now()
        for i, prediction in enumerate(predictions):
            forecast_date = current_date + timedelta(days=30 * (i + 1))
            forecast_period = forecast_date.strftime('%Y-%m')
            
            # Calcular intervalo de confiança (±20% baseado na variabilidade)
            std_dev = np.std(costs) if len(costs) > 1 else prediction * 0.1
            confidence_interval = std_dev * 1.96  # 95% confidence
            
            forecasts.append({
                'cliente': cliente,
                'account_id': account_id,
                'service_name': service_name,
                'forecast_period': forecast_period,
                'forecast_type': 'monthly',
                'predicted_cost': max(0, prediction),
                'confidence_interval_lower': max(0, prediction - confidence_interval),
                'confidence_interval_upper': prediction + confidence_interval,
                'prediction_accuracy': confidence * 100,
                'trend_direction': trend,
                'growth_rate': growth_rate
            })
    
    return forecasts

def save_forecasts(forecasts, db_config):
    """Salva previsões no banco"""
    if not forecasts:
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
    
    # Limpar previsões antigas
    cursor.execute("DELETE FROM cost_forecasts WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)")
    
    for forecast in forecasts:
        cursor.execute("""
            INSERT INTO cost_forecasts 
            (cliente, account_id, service_name, forecast_period, forecast_type,
             predicted_cost, confidence_interval_lower, confidence_interval_upper,
             prediction_accuracy, trend_direction, growth_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                predicted_cost = VALUES(predicted_cost),
                confidence_interval_lower = VALUES(confidence_interval_lower),
                confidence_interval_upper = VALUES(confidence_interval_upper),
                prediction_accuracy = VALUES(prediction_accuracy),
                trend_direction = VALUES(trend_direction),
                growth_rate = VALUES(growth_rate),
                created_at = CURRENT_TIMESTAMP
        """, (
            forecast['cliente'], forecast['account_id'], forecast['service_name'],
            forecast['forecast_period'], forecast['forecast_type'],
            forecast['predicted_cost'], forecast['confidence_interval_lower'],
            forecast['confidence_interval_upper'], forecast['prediction_accuracy'],
            forecast['trend_direction'], forecast['growth_rate']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

def generate_forecast_summary(db_config):
    """Gera resumo das previsões"""
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    print(f"\n📈 RESUMO DE PREVISÕES")
    print("=" * 50)
    
    # Previsões por cliente para próximo mês
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m')
    
    cursor.execute("""
        SELECT 
            cliente,
            SUM(predicted_cost) as total_predicted,
            AVG(prediction_accuracy) as avg_accuracy,
            COUNT(DISTINCT service_name) as services_count
        FROM cost_forecasts 
        WHERE forecast_period = %s
        GROUP BY cliente
        ORDER BY total_predicted DESC
        LIMIT 10
    """, (next_month,))
    
    print(f"\n💰 PREVISÕES PARA {next_month}:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: ${row[1]:,.2f} (Precisão: {row[2]:.1f}%, {row[3]} serviços)")
    
    # Serviços com maior crescimento previsto
    cursor.execute("""
        SELECT 
            service_name,
            AVG(growth_rate) as avg_growth,
            SUM(predicted_cost) as total_predicted,
            COUNT(DISTINCT cliente) as clients_count
        FROM cost_forecasts 
        WHERE forecast_period = %s AND trend_direction = 'increasing'
        GROUP BY service_name
        ORDER BY avg_growth DESC
        LIMIT 10
    """, (next_month,))
    
    print(f"\n📊 SERVIÇOS COM MAIOR CRESCIMENTO PREVISTO:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: +{row[1]:.1f}% (${row[2]:,.2f}, {row[3]} clientes)")
    
    cursor.close()
    conn.close()

def main():
    """Função principal"""
    print("🔮 Iniciando geração de previsões de custos...")
    
    try:
        db_config = get_database_credentials()
        
        # Gerar previsões
        print("📊 Analisando dados históricos...")
        forecasts = generate_forecasts(db_config)
        
        if forecasts:
            print(f"💾 Salvando {len(forecasts)} previsões...")
            save_forecasts(forecasts, db_config)
            
            # Gerar resumo
            generate_forecast_summary(db_config)
            
            print(f"\n✅ Previsões geradas com sucesso!")
        else:
            print("⚠️ Dados históricos insuficientes para previsões")
    
    except ImportError:
        print("⚠️ Bibliotecas ML não instaladas. Instale: pip install scikit-learn numpy")
    except Exception as e:
        print(f"✗ Erro na geração de previsões: {e}")

if __name__ == "__main__":
    main()
