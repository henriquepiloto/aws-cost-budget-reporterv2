#!/bin/bash
export AWS_DEFAULT_REGION=us-east-1
cd /home/ubuntu/script_cost
echo "$(date): Iniciando relatório de custos..." >> cost_report.log
echo "$(date): Baixando roles.json atualizado do S3..." >> cost_report.log
aws s3 cp s3://script-piloto/roles.json ./roles.json >> cost_report.log 2>&1
if [ $? -eq 0 ]; then
    echo "$(date): roles.json atualizado com sucesso" >> cost_report.log
else
    echo "$(date): ERRO ao baixar roles.json" >> cost_report.log
    exit 1
fi
python3 cost_report_mysql.py >> cost_report.log 2>&1
echo "$(date): Relatório concluído" >> cost_report.log
