"""
Prisma Cost Intelligence Platform - Backend API
Cloudinho AI Assistant with customizable admin panel
"""

import json
import boto3
import pymysql
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CloudinhoAssistant:
    """Cloudinho - AI Assistant for AWS Cost Intelligence"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        self.personality = self._load_personality()
        
    def _load_personality(self) -> str:
        """Load Cloudinho's personality and context"""
        return """
        Você é o Cloudinho, um assistente especialista em custos AWS muito amigável e humanizado.
        
        PERSONALIDADE:
        - Sempre responda de forma calorosa e amigável, como um consultor experiente
        - Use emojis apropriados para tornar a conversa mais humana
        - Seja proativo em sugerir otimizações e insights
        - Explique conceitos técnicos de forma simples e didática
        - Sempre termine com uma pergunta ou sugestão para continuar ajudando
        
        CONTEXTO:
        - Você trabalha na Select Soluções, especializada em otimização de custos AWS
        - Tem acesso a dados reais de custos, previsões e recomendações
        - Pode analisar tendências, alertas e oportunidades de economia
        - Sempre baseie suas respostas em dados concretos quando disponível
        
        ESTILO DE RESPOSTA:
        - Cumprimente sempre de forma calorosa
        - Use linguagem brasileira natural e profissional
        - Seja específico com números e valores quando relevante
        - Ofereça insights acionáveis, não apenas dados
        - Mantenha um tom otimista e solucionador
        """
    
    def ask(self, question: str, context_data: Dict = None) -> str:
        """Process user question with Cloudinho's personality"""
        try:
            # Build context from data
            data_context = ""
            if context_data:
                data_context = f"\nDADOS DISPONÍVEIS:\n{json.dumps(context_data, indent=2, ensure_ascii=False)}"
            
            # Build prompt
            prompt = f"""
            {self.personality}
            
            PERGUNTA DO USUÁRIO: {question}
            {data_context}
            
            Responda como o Cloudinho, sendo específico, útil e amigável. Use os dados fornecidos para dar insights precisos.
            """
            
            # Call Bedrock
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Cloudinho error: {e}")
            return "Ops! 😅 Tive um pequeno problema técnico. Pode tentar novamente? Estou aqui para ajudar!"

class DatabaseManager:
    """Database connection and query manager"""
    
    def __init__(self):
        self.db_config = self._get_database_credentials()
        
    def _get_database_credentials(self) -> Dict:
        """Get database credentials from Secrets Manager"""
        try:
            session = boto3.session.Session()
            client = session.client('secretsmanager', region_name='us-east-1')
            response = client.get_secret_value(SecretId='glpidatabaseadmin')
            secret = json.loads(response['SecretString'])
            
            return {
                'host': secret.get('host'),
                'username': secret['username'],
                'password': secret['password'],
                'port': secret.get('port', 3306),
                'database': 'aws_costs'
            }
        except Exception as e:
            logger.error(f"Database credentials error: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        return pymysql.connect(
            host=self.db_config['host'],
            user=self.db_config['username'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            port=self.db_config['port'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []

class CostAnalytics:
    """Cost analytics and data processing"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_client_summary(self, cliente: str) -> Dict:
        """Get comprehensive client summary"""
        current_month = datetime.now().strftime('%Y-%m')
        
        # Monthly total
        monthly_query = """
            SELECT SUM(total_cost) as monthly_total
            FROM monthly_service_costs 
            WHERE cliente = %s AND year_month = %s
        """
        monthly_result = self.db.execute_query(monthly_query, (cliente, current_month))
        monthly_total = monthly_result[0]['monthly_total'] if monthly_result else 0
        
        # Top services
        services_query = """
            SELECT service_name, total_cost, growth_rate
            FROM monthly_service_costs 
            WHERE cliente = %s AND year_month = %s
            ORDER BY total_cost DESC
            LIMIT 5
        """
        top_services = self.db.execute_query(services_query, (cliente, current_month))
        
        # Alerts
        alerts_query = """
            SELECT COUNT(*) as alert_count
            FROM cost_trends 
            WHERE cliente = %s AND alert_level IN ('high', 'critical')
        """
        alerts_result = self.db.execute_query(alerts_query, (cliente,))
        alert_count = alerts_result[0]['alert_count'] if alerts_result else 0
        
        # Savings opportunities
        savings_query = """
            SELECT SUM(estimated_savings) as potential_savings
            FROM rightsizing_recommendations 
            WHERE cliente = %s AND status = 'Active'
        """
        savings_result = self.db.execute_query(savings_query, (cliente,))
        potential_savings = savings_result[0]['potential_savings'] if savings_result else 0
        
        return {
            'cliente': cliente,
            'monthly_total': float(monthly_total or 0),
            'top_services': top_services,
            'alert_count': alert_count,
            'potential_savings': float(potential_savings or 0),
            'month': current_month
        }
    
    def get_cost_trends(self, cliente: str, days: int = 30) -> Dict:
        """Get cost trends for client"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                cost_date,
                SUM(amount) as daily_total
            FROM daily_costs 
            WHERE cliente = %s AND cost_date >= %s
            GROUP BY cost_date
            ORDER BY cost_date
        """
        
        results = self.db.execute_query(query, (cliente, start_date))
        
        return {
            'cliente': cliente,
            'period_days': days,
            'daily_trends': results,
            'total_days': len(results)
        }
    
    def get_forecasts(self, cliente: str) -> Dict:
        """Get cost forecasts for client"""
        query = """
            SELECT 
                service_name,
                forecast_period,
                predicted_cost,
                trend_direction,
                prediction_accuracy
            FROM cost_forecasts 
            WHERE cliente = %s 
            ORDER BY forecast_period, predicted_cost DESC
            LIMIT 10
        """
        
        forecasts = self.db.execute_query(query, (cliente,))
        
        return {
            'cliente': cliente,
            'forecasts': forecasts,
            'total_forecasts': len(forecasts)
        }

class AdminPanel:
    """Admin panel for customization"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def get_branding_config(self, tenant_id: str = 'default') -> Dict:
        """Get branding configuration"""
        # For MVP, return default config
        # In production, this would come from database
        return {
            'company_name': 'Select Soluções',
            'logo_url': 'https://prisma.selectsolucoes.com/assets/logo.png',
            'primary_color': '#1f2937',
            'secondary_color': '#3b82f6',
            'accent_color': '#10b981',
            'font_family': 'Inter, sans-serif',
            'cloudinho_avatar': 'https://prisma.selectsolucoes.com/assets/cloudinho-avatar.png'
        }
    
    def update_branding_config(self, tenant_id: str, config: Dict) -> bool:
        """Update branding configuration"""
        # For MVP, just return success
        # In production, save to database
        logger.info(f"Branding updated for {tenant_id}: {config}")
        return True

# Initialize components
db_manager = DatabaseManager()
cloudinho = CloudinhoAssistant()
analytics = CostAnalytics(db_manager)
admin_panel = AdminPanel(db_manager)

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        # Parse body if present
        request_data = {}
        if body:
            try:
                request_data = json.loads(body)
            except:
                pass
        
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': os.environ.get('CORS_ORIGIN', '*'),
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle OPTIONS (CORS preflight)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Route requests
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'Prisma Cost Intelligence',
                    'cloudinho': 'online',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        elif path.startswith('/api/chat'):
            # Cloudinho chat endpoint
            question = request_data.get('question', '')
            cliente = request_data.get('cliente', '')
            
            if not question:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Question is required'})
                }
            
            # Get context data for the client
            context_data = {}
            if cliente:
                context_data = analytics.get_client_summary(cliente)
            
            # Get Cloudinho's response
            response = cloudinho.ask(question, context_data)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'response': response,
                    'cloudinho': 'Cloudinho',
                    'timestamp': datetime.now().isoformat(),
                    'context_used': bool(context_data)
                })
            }
        
        elif path.startswith('/api/summary/'):
            # Client summary endpoint
            cliente = path.split('/')[-1]
            summary = analytics.get_client_summary(cliente)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(summary)
            }
        
        elif path.startswith('/api/trends/'):
            # Cost trends endpoint
            cliente = path.split('/')[-1]
            days = int(query_params.get('days', 30))
            trends = analytics.get_cost_trends(cliente, days)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(trends)
            }
        
        elif path.startswith('/api/forecasts/'):
            # Forecasts endpoint
            cliente = path.split('/')[-1]
            forecasts = analytics.get_forecasts(cliente)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(forecasts)
            }
        
        elif path == '/api/admin/branding':
            # Admin branding endpoint
            if http_method == 'GET':
                tenant_id = query_params.get('tenant', 'default')
                config = admin_panel.get_branding_config(tenant_id)
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(config)
                }
            
            elif http_method == 'PUT':
                tenant_id = request_data.get('tenant', 'default')
                config = request_data.get('config', {})
                success = admin_panel.update_branding_config(tenant_id, config)
                
                return {
                    'statusCode': 200 if success else 500,
                    'headers': headers,
                    'body': json.dumps({'success': success})
                }
        
        else:
            # Default response
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

# For local testing
def handler(event, context):
    return lambda_handler(event, context)
