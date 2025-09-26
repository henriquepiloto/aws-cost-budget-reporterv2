# Enhanced Analytics - Fase 1 Implementada

## 🎯 Objetivos Alcançados

### ✅ Estrutura de Dados Granular
- **daily_costs**: Custos diários por serviço e região
- **monthly_service_costs**: Agregados mensais com métricas
- **cost_metrics**: KPIs e métricas calculadas
- **cost_trends**: Tendências e alertas automáticos
- **aws_services**: Catálogo de serviços AWS

### ✅ Coleta Aprimorada
- Dados diários por serviço AWS
- Granularidade por região
- Histórico persistente
- Cálculo automático de crescimento

### ✅ Analytics Automático
- Taxas de crescimento mês a mês
- Detecção de tendências
- Alertas por nível de criticidade
- Relatórios automáticos

## 📊 Estrutura de Dados

### Tabela: daily_costs
```sql
- cliente, account_id, service_name, region
- cost_date, amount, currency
- usage_type, operation
- Índices otimizados para consultas
```

### Tabela: monthly_service_costs
```sql
- Agregados mensais por serviço
- total_cost, avg_daily_cost, growth_rate
- Métricas min/max/dias de uso
```

### Tabela: cost_metrics
```sql
- Métricas calculadas: total_monthly, top_service, fastest_growing
- Suporte a valores numéricos e textuais
- Dados extras em JSON
```

### Tabela: cost_trends
```sql
- Tendências: increasing, decreasing, stable, volatile
- Níveis de alerta: low, medium, high, critical
- Scores de confiança
```

## 🚀 Como Usar

### 1. Executar Coleta Completa
```bash
./scripts/run_enhanced_collection.sh
```

### 2. Coleta Apenas Dados
```bash
python3 scripts/enhanced_cost_collector.py
```

### 3. Processar Analytics
```bash
python3 scripts/analytics_processor.py
```

## 📈 Queries para Dashboards

### Custos Diários por Cliente
```sql
SELECT 
    cliente,
    cost_date,
    SUM(amount) as daily_total
FROM daily_costs 
WHERE cost_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY cliente, cost_date
ORDER BY cost_date DESC;
```

### Top 10 Serviços por Custo
```sql
SELECT 
    service_name,
    SUM(total_cost) as total_cost,
    AVG(growth_rate) as avg_growth
FROM monthly_service_costs 
WHERE year_month = DATE_FORMAT(CURDATE(), '%Y-%m')
GROUP BY service_name
ORDER BY total_cost DESC
LIMIT 10;
```

### Alertas Críticos
```sql
SELECT 
    cliente,
    service_name,
    growth_percentage,
    alert_level,
    description
FROM cost_trends 
WHERE alert_level IN ('high', 'critical')
ORDER BY growth_percentage DESC;
```

### Crescimento por Cliente (6 meses)
```sql
SELECT 
    cliente,
    year_month,
    SUM(total_cost) as monthly_total,
    AVG(growth_rate) as avg_growth_rate
FROM monthly_service_costs 
WHERE year_month >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 6 MONTH), '%Y-%m')
GROUP BY cliente, year_month
ORDER BY cliente, year_month;
```

### Análise por Região
```sql
SELECT 
    region,
    service_name,
    SUM(amount) as total_cost,
    COUNT(DISTINCT cliente) as clients_count
FROM daily_costs 
WHERE cost_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY region, service_name
ORDER BY total_cost DESC;
```

## 🔍 Views Disponíveis

### v_monthly_costs_summary
- Resumo mensal por cliente
- Contagem de serviços
- Maior custo por serviço
- Taxa média de crescimento

### v_top_services_by_cost
- Ranking de serviços por custo
- Particionado por cliente/mês
- Útil para identificar top gastadores

### v_cost_growth_analysis
- Categorização de crescimento
- High/Medium/Low Growth
- Identificação de decreases significativos

## 📊 Métricas Disponíveis

### Automáticas (cost_metrics)
- **total_monthly**: Custo total mensal por cliente
- **top_service**: Serviço mais caro por cliente
- **fastest_growing**: Serviço com maior crescimento

### Tendências (cost_trends)
- **increasing**: Serviços em crescimento
- **stable**: Serviços estáveis mas caros
- **volatile**: Serviços com variação alta

## 🎨 Integração com BI Tools

### Metabase
1. Conectar no MySQL aws_costs
2. Usar queries prontas acima
3. Criar dashboards com:
   - Gráficos de linha (tendências)
   - Barras (top serviços)
   - Tabelas (alertas)

### PowerBI
1. Conectar via MySQL connector
2. Importar views principais
3. Criar relacionamentos automáticos
4. Dashboards interativos

### AWS QuickSight
1. Conectar no RDS MySQL
2. Usar datasets das views
3. Análises automáticas com ML
4. Alertas integrados

## 🤖 Preparação para Chatbot

### Estrutura Otimizada
- Dados normalizados para consultas rápidas
- Métricas pré-calculadas
- Textos descritivos em cost_trends
- JSON adicional para contexto

### Queries Exemplo para Chatbot
```sql
-- "Qual cliente gastou mais este mês?"
SELECT cliente, metric_value 
FROM cost_metrics 
WHERE metric_type = 'total_monthly' 
ORDER BY metric_value DESC LIMIT 1;

-- "Quais serviços estão crescendo muito?"
SELECT cliente, service_name, growth_percentage 
FROM cost_trends 
WHERE trend_type = 'increasing' AND alert_level = 'high';

-- "Custo diário dos últimos 7 dias"
SELECT cost_date, SUM(amount) as daily_total 
FROM daily_costs 
WHERE cost_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
GROUP BY cost_date;
```

## 📝 Próximos Passos (Fase 2)

### Funcionalidades Planejadas
- [ ] Coleta de Reserved Instances
- [ ] Análise de Rightsizing
- [ ] Previsões com ML
- [ ] Alertas por email/Slack
- [ ] API REST para chatbot
- [ ] Dashboard web integrado

### Otimizações
- [ ] Particionamento de tabelas por data
- [ ] Índices compostos otimizados
- [ ] Cache de queries frequentes
- [ ] Compressão de dados históricos

## 🔧 Configuração

### Variáveis de Ambiente
```bash
export S3_ROLES_URI="s3://seu-bucket/roles.json"
export AWS_DEFAULT_REGION="us-east-1"
```

### Permissões IAM Adicionais
```json
{
  "Effect": "Allow",
  "Action": [
    "ce:GetDimensionValues",
    "ce:GetCostAndUsage",
    "ce:GetUsageReport"
  ],
  "Resource": "*"
}
```

### Cron Job Sugerido
```bash
# Coleta diária às 6h
0 6 * * * /home/ubuntu/aws-cost-budget-reporterv2/scripts/run_enhanced_collection.sh

# Analytics às 7h (após coleta)
0 7 * * * /usr/bin/python3 /home/ubuntu/aws-cost-budget-reporterv2/scripts/analytics_processor.py
```

## 📞 Suporte

Para dúvidas sobre a implementação da Fase 1:
- Consulte os logs em `/var/log/aws-cost-reporter/`
- Verifique as views no banco para validar dados
- Execute queries de exemplo para testar
