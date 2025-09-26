#!/bin/bash

# Enhanced Cost Collection Script
# Executa coleta granular e processamento de analytics

echo "🚀 Iniciando coleta aprimorada de custos AWS..."

# Definir diretório base
SCRIPT_DIR="/home/hpiloto/projetos/aws-cost-budget-reporterv2/scripts"
LOG_DIR="/var/log/aws-cost-reporter"

# Criar diretório de logs se não existir
mkdir -p $LOG_DIR

# Definir arquivos de log
COLLECTION_LOG="$LOG_DIR/enhanced_collection_$(date +%Y%m%d_%H%M%S).log"
ANALYTICS_LOG="$LOG_DIR/analytics_$(date +%Y%m%d_%H%M%S).log"

echo "📝 Logs salvos em:"
echo "  Coleta: $COLLECTION_LOG"
echo "  Analytics: $ANALYTICS_LOG"

# Executar coleta aprimorada
echo "📊 Executando coleta granular de custos..."
python3 $SCRIPT_DIR/enhanced_cost_collector.py 2>&1 | tee $COLLECTION_LOG

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Coleta concluída com sucesso"
    
    # Executar processamento de analytics
    echo "🔍 Executando processamento de analytics..."
    python3 $SCRIPT_DIR/analytics_processor.py 2>&1 | tee $ANALYTICS_LOG
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ Analytics processado com sucesso"
        
        # Executar coleta de budgets (mantém compatibilidade)
        echo "💰 Executando coleta de budgets..."
        python3 $SCRIPT_DIR/budget_report_mysql.py 2>&1 | tee -a $COLLECTION_LOG
        
        echo "🎉 Coleta aprimorada concluída!"
        echo "📊 Dados disponíveis para:"
        echo "  - Análise diária de custos por serviço"
        echo "  - Tendências de crescimento"
        echo "  - Alertas automáticos"
        echo "  - Dashboards Metabase/PowerBI"
        
    else
        echo "❌ Erro no processamento de analytics"
        exit 1
    fi
else
    echo "❌ Erro na coleta de dados"
    exit 1
fi

# Limpeza de logs antigos (manter últimos 30 dias)
find $LOG_DIR -name "*.log" -mtime +30 -delete 2>/dev/null

echo "✨ Processo completo finalizado!"
