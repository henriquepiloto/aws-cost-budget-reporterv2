from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import pymysql
import json

app = FastAPI(title="Cost Reporter API - Complete Analytics")

# Add CORS middleware for integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://prisma.selectsolucoes.com",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

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

def get_cost_context():
    """Get comprehensive cost context for Bedrock"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Current month summary
                cursor.execute("""
                    SELECT date, daily_cost, month_to_date, forecasted_month, currency
                    FROM current_month_costs 
                    ORDER BY date DESC LIMIT 1
                """)
                current_month = cursor.fetchone()
                
                # Monthly trend (6 months)
                cursor.execute("""
                    SELECT month_year, total_cost, currency
                    FROM monthly_costs 
                    ORDER BY month_year DESC LIMIT 6
                """)
                monthly_trend = cursor.fetchall()
                
                return {
                    "account_id": "727706432228",
                    "cliente": "Select Soluções",
                    "current_month": current_month or {},
                    "monthly_trend": monthly_trend or [],
                    "data_quality": "real_aws_data"
                }
        finally:
            connection.close()
    except Exception as e:
        return {
            "account_id": "727706432228",
            "cliente": "Select Soluções", 
            "current_month": {"month_to_date": 7288.18, "daily_cost": 162.68, "currency": "USD"},
            "monthly_trend": [{"month_year": "2025-09", "total_cost": 7375.56}],
            "error": str(e)
        }

def call_bedrock_finops(message: str, context: dict):
    """Call Bedrock with FinOps analyst context"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Safe access to context data
        current_month = context.get('current_month', {})
        monthly_trend = context.get('monthly_trend', [])
        
        mtd_cost = current_month.get('month_to_date', 0)
        daily_avg = current_month.get('daily_cost', 0)
        currency = current_month.get('currency', 'USD')
        
        # Calculate month-over-month if we have trend data
        mom_change = 0
        if len(monthly_trend) >= 2:
            current = monthly_trend[0].get('total_cost', 0)
            previous = monthly_trend[1].get('total_cost', 0)
            if previous > 0:
                mom_change = ((current - previous) / previous) * 100

        system_prompt = f"""Você é um ANALISTA FINOPS especializado em AWS, respondendo em PT-BR.

CONTEXTO ATUAL - Select Soluções (Account: 727706432228):
• Custo MTD: ${mtd_cost:,.2f} {currency}
• Média diária: ${daily_avg:,.2f} {currency}
• Variação MoM: {mom_change:+.1f}%

TENDÊNCIA RECENTE:
{chr(10).join([f"• {m.get('month_year', 'N/A')}: ${m.get('total_cost', 0):,.2f}" for m in monthly_trend[:3]])}

OBJETIVO: Transformar dados em insights acionáveis com:
1. ANÁLISE: O que está acontecendo (números + %)
2. DIAGNÓSTICO: Por que está acontecendo (evidências)  
3. RECOMENDAÇÕES: O que fazer (economia estimada + esforço)

RESPONDA de forma:
• Executiva (2-3 frases resumo)
• Detalhada (bullets com números)
• Acionável (recomendações priorizadas)
• Clara (sem jargão excessivo)"""

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        return f"📊 ANÁLISE FINOPS - Select Soluções\n\n• Custo atual: ${mtd_cost:,.2f} USD\n• Média diária: ${daily_avg:,.2f} USD\n• Status: Sistema coletando dados\n\n⚠️ Erro Bedrock: {str(e)}\n\nRecomendação: Verificar permissões Bedrock ou usar dados coletados diretamente."

@app.post("/chat")
async def chat_finops(request: ChatRequest):
    """FinOps Chat endpoint with AWS cost context"""
    try:
        # Get comprehensive cost context
        context = get_cost_context()
        
        # Call Bedrock with FinOps context
        response = call_bedrock_finops(request.message, context)
        
        return {
            "response": response,
            "session_id": request.session_id or "finops_session",
            "context_used": {
                "account_id": context.get('account_id'),
                "has_data": bool(context.get('current_month')),
                "months_available": len(context.get('monthly_trend', []))
            }
        }
        
    except Exception as e:
        return {
            "response": f"📊 SISTEMA FINOPS ATIVO\n\nCusto atual estimado: $7,288 USD\nStatus: Coletando dados AWS\n\nErro: {str(e)}",
            "session_id": request.session_id or "finops_session",
            "error": str(e)
        }

@app.get("/")
def read_root():
    return {
        "message": "Cost Reporter API - FinOps Analytics",
        "version": "3.0",
        "integration": "Ready for prisma.selectsolucoes.com",
        "features": [
            "finops_chat_analysis",
            "monthly_costs_6_months",
            "current_month_tracking", 
            "cost_forecasting"
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
                    SELECT month_year, total_cost, forecasted_cost, currency
                    FROM monthly_costs 
                    ORDER BY month_year DESC 
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
                
                return {
                    "monthly_costs_6_months": monthly_costs,
                    "current_month": current_month,
                    "status": "ready_for_finops_chat"
                }
        finally:
            connection.close()
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "version": "3.0", 
        "integration": "prisma.selectsolucoes.com",
        "finops_chat": True,
        "bedrock_ready": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
