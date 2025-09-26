"""
Cloudinho AI Assistant - Versão Simplificada
"""

import json
import boto3
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CloudinhoAssistant:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        
    def ask(self, question: str) -> str:
        try:
            logger.info(f"Processing question: {question[:100]}...")
            
            # Contexto específico para custos AWS
            system_prompt = """Você é o Cloudinho, assistente especializado em FinOps e análise de custos AWS da Select Soluções.

CONTEXTO ATUAL:
- Cliente: 2ABrasil (exemplo mencionado)
- Especialidade: Otimização de custos AWS
- Foco: Análise financeira, recomendações práticas

Responda de forma:
- Executiva e objetiva
- Com dados específicos quando possível
- Recomendações acionáveis
- Em português brasileiro"""
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1000,
                    'system': system_prompt,
                    'messages': [{'role': 'user', 'content': question}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            logger.info(f"Generated response: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Cloudinho error: {str(e)}")
            return f"Olá! Sou o Cloudinho, seu assistente de custos AWS. No momento estou com dificuldades técnicas, mas posso ajudar com análise de custos, otimização e recomendações para AWS. Como posso ajudar você?"

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body')
        
        logger.info(f"Method: {http_method}, Path: {path}")
        
        request_data = {}
        if body:
            try:
                request_data = json.loads(body)
                logger.info(f"Request data: {json.dumps(request_data, default=str)}")
            except Exception as e:
                logger.error(f"Error parsing body: {str(e)}")
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        }
        
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS preflight'})}
        
        cloudinho = CloudinhoAssistant()
        
        # Route requests
        if path == '/chat':
            message = request_data.get('message', '')
            if not message:
                return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Message is required'})}
            
            response = cloudinho.ask(message)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'response': response, 'timestamp': datetime.now().isoformat()})
            }
        
        elif path == '/chat/config':
            # Return default config
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "config": {
                        "primaryColor": "#3b82f6",
                        "secondaryColor": "#1e40af",
                        "botName": "Cloudinho",
                        "welcomeMessage": "Olá! Sou o Cloudinho, seu assistente de análise de custos AWS. Como posso ajudar você hoje?",
                        "theme": "light"
                    }
                })
            }
        
        else:
            logger.warning(f"Unknown path: {path}")
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Endpoint not found'})}
    
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error', 'message': str(e)})
        }

def handler(event, context):
    return lambda_handler(event, context)
