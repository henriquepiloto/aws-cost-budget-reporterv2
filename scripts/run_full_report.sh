#!/bin/bash
export AWS_DEFAULT_REGION=us-east-1
cd /home/ubuntu/script_cost
echo "$(date): Iniciando relatório completo..." >> cost_report.log
aws s3 cp s3://script-piloto/roles.json ./roles.json >> cost_report.log 2>&1
echo "$(date): Executando relatório de custos..." >> cost_report.log
python3 cost_report_mysql.py >> cost_report.log 2>&1
echo "$(date): Executando relatório de budgets..." >> cost_report.log
python3 budget_report_mysql.py >> cost_report.log 2>&1
echo "$(date): Relatórios concluídos" >> cost_report.log
