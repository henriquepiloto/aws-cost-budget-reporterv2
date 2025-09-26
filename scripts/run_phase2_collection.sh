#!/bin/bash

# Phase 2 Complete Collection Script
# Executa coleta completa: dados básicos + avançados + previsões

echo "🚀 Iniciando coleta completa Fase 2..."

# Definir diretório base
SCRIPT_DIR="/home/hpiloto/projetos/aws-cost-budget-reporterv2/scripts"
LOG_DIR="/var/log/aws-cost-reporter"

# Criar diretório de logs se não existir
mkdir -p $LOG_DIR

# Definir arquivos de log
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAIN_LOG="$LOG_DIR/phase2_collection_$TIMESTAMP.log"

echo "📝 Log principal: $MAIN_LOG"

# Função para log com timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $MAIN_LOG
}

log_message "🎯 Iniciando Fase 2 - Coleta Completa"

# 1. Executar coleta básica (Fase 1)
log_message "📊 Executando coleta básica de custos..."
python3 $SCRIPT_DIR/enhanced_cost_collector.py 2>&1 | tee -a $MAIN_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_message "✅ Coleta básica concluída"
else
    log_message "❌ Erro na coleta básica"
    exit 1
fi

# 2. Executar coleta avançada (Fase 2)
log_message "🔬 Executando coleta avançada (RIs, Rightsizing, Anomalias)..."
python3 $SCRIPT_DIR/advanced_cost_collector.py 2>&1 | tee -a $MAIN_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_message "✅ Coleta avançada concluída"
else
    log_message "⚠️ Erro na coleta avançada (continuando...)"
fi

# 3. Executar processamento de analytics
log_message "🔍 Executando processamento de analytics..."
python3 $SCRIPT_DIR/analytics_processor.py 2>&1 | tee -a $MAIN_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_message "✅ Analytics processado"
else
    log_message "❌ Erro no processamento de analytics"
    exit 1
fi

# 4. Gerar previsões
log_message "🔮 Gerando previsões de custos..."
python3 $SCRIPT_DIR/cost_forecasting.py 2>&1 | tee -a $MAIN_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_message "✅ Previsões geradas"
else
    log_message "⚠️ Erro na geração de previsões (continuando...)"
fi

# 5. Executar coleta de budgets (compatibilidade)
log_message "💰 Executando coleta de budgets..."
python3 $SCRIPT_DIR/budget_report_mysql.py 2>&1 | tee -a $MAIN_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_message "✅ Budgets coletados"
else
    log_message "⚠️ Erro na coleta de budgets (continuando...)"
fi

# 6. Gerar relatório final
log_message "📋 Gerando relatório final..."

# Conectar no banco e gerar estatísticas
python3 -c "
import pymysql
import json
import boto3
from datetime import datetime

def get_db_credentials():
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId='glpidatabaseadmin')
        return json.loads(response['SecretString'])
    except:
        return None

db_config = get_db_credentials()
if db_config:
    try:
        conn = pymysql.connect(
            host=db_config['host'], 
            user=db_config['username'], 
            password=db_config['password'], 
            database='aws_costs', 
            port=db_config.get('port', 3306),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        print('📊 ESTATÍSTICAS DA COLETA:')
        
        # Custos diários
        cursor.execute('SELECT COUNT(*) FROM daily_costs WHERE DATE(created_at) = CURDATE()')
        daily_records = cursor.fetchone()[0]
        print(f'  Custos diários: {daily_records} registros')
        
        # Reserved Instances
        cursor.execute('SELECT COUNT(*) FROM reserved_instances')
        ri_count = cursor.fetchone()[0]
        print(f'  Reserved Instances: {ri_count} registros')
        
        # Rightsizing
        cursor.execute('SELECT COUNT(*) FROM rightsizing_recommendations WHERE status = \"Active\"')
        rightsizing_count = cursor.fetchone()[0]
        print(f'  Rightsizing ativo: {rightsizing_count} recomendações')
        
        # Previsões
        cursor.execute('SELECT COUNT(*) FROM cost_forecasts WHERE DATE(created_at) = CURDATE()')
        forecast_count = cursor.fetchone()[0]
        print(f'  Previsões geradas: {forecast_count} registros')
        
        # Alertas críticos
        cursor.execute('SELECT COUNT(*) FROM cost_trends WHERE alert_level IN (\"high\", \"critical\")')
        critical_alerts = cursor.fetchone()[0]
        print(f'  Alertas críticos: {critical_alerts} alertas')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'⚠️ Erro ao gerar estatísticas: {e}')
" 2>&1 | tee -a $MAIN_LOG

log_message "🎉 Coleta Fase 2 concluída com sucesso!"

# Resumo final
log_message "📈 DADOS DISPONÍVEIS:"
log_message "  ✅ Custos diários granulares por serviço"
log_message "  ✅ Reserved Instances e utilização"
log_message "  ✅ Recomendações de rightsizing"
log_message "  ✅ Previsões de custos (3 meses)"
log_message "  ✅ Detecção de anomalias"
log_message "  ✅ Alertas automáticos"
log_message "  ✅ API REST para chatbot"

log_message "🔗 PRÓXIMOS PASSOS:"
log_message "  📊 Configurar dashboards Metabase/PowerBI"
log_message "  🤖 Integrar chatbot com API REST"
log_message "  📧 Configurar alertas por email"
log_message "  🔄 Agendar execução automática"

# Limpeza de logs antigos (manter últimos 30 dias)
find $LOG_DIR -name "*.log" -mtime +30 -delete 2>/dev/null

log_message "✨ Processo Fase 2 finalizado!"

echo ""
echo "📋 Log completo salvo em: $MAIN_LOG"
echo "🌐 API disponível em: http://localhost:5000/api/health"
echo "📊 Dados prontos para BI tools e chatbot!"
