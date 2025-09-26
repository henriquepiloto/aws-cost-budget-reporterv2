# Cost Reporter v3.0 - Complete Analytics

Sistema avançado de monitoramento de custos AWS com análise completa e previsões.

## 🌐 Acesso

**URL Produção**: https://costcollector.selectsolucoes.com

## 📊 Funcionalidades

### **Análise Completa de Custos:**
- Custos mensais dos últimos 6 meses
- Acompanhamento diário do mês atual
- Previsões de custo (forecast)
- Orçamentos da conta AWS
- Contagem de alertas por mês

### **Detalhamento Avançado:**
- Custos por serviço AWS
- Tipos de uso específicos
- Recursos individuais (EC2, RDS, etc.)
- Análise por região e AZ

## 🏗️ Arquitetura

### **Serviços ECS:**
- **Data Collector**: Coleta automática (diária 06:00 UTC)
- **API Service**: FastAPI REST API (1 task)
- **Report Generator**: Relatórios S3

### **Infraestrutura:**
- **Cluster**: cost-reporter-cluster
- **Database**: MySQL RDS (cost_reporter)
- **Load Balancer**: SSL + Health checks
- **Storage**: MySQL + S3

## 🌐 Endpoints da API

### **Análise Completa:**
```
GET /costs/overview      # Visão geral completa
GET /costs/monthly       # Últimos 6 meses  
GET /costs/current-month # Progresso mês atual
GET /budgets            # Orçamentos + % uso
GET /alerts             # Alertas do mês
```

### **Análise Detalhada:**
```
GET /costs/detailed      # Por serviço
GET /costs/by-service   # Agregação
GET /costs/resources    # Por recurso
GET /health             # Status sistema
```

## 📊 Exemplo de Dados

```json
{
  "monthly_costs_6_months": [
    {"year_month": "2025-09", "total_cost": 4850.25}
  ],
  "current_month": {
    "date": "2025-09-26",
    "daily_cost": 162.60,
    "month_to_date": 4230.45,
    "forecasted_month": 4950.00
  },
  "budgets": [{
    "budget_name": "Monthly-Budget",
    "budget_limit": 5000.00,
    "usage_percentage": 84.61
  }],
  "alerts_this_month": {
    "alert_count": 3
  }
}
```

## 🚀 Deploy

```bash
# Build containers
./build-and-deploy.sh

# Deploy infraestrutura
cd infrastructure/terraform
terraform apply

# Teste completo
make test
```

## 🔧 Configuração

- **Domain**: costcollector.selectsolucoes.com
- **Environment**: prod
- **Region**: us-east-1
- **Database**: cost_reporter (MySQL)

## ⏰ Coleta Automática

- **Frequência**: Diária às 06:00 UTC
- **EventBridge**: Agendamento automático
- **Dados**: 6 meses + mês atual + previsões
- **Fontes**: Cost Explorer + Budgets + Forecast APIs

---

**v3.0 - Complete Analytics**  
**Última atualização**: 2025-09-26
