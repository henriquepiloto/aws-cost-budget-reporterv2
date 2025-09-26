# AWS Cost Budget Reporter v3.0

Sistema completo de monitoramento e análise de custos AWS com arquitetura ECS Fargate e coleta avançada de dados.

## 🚀 Status do Projeto

**✅ IMPLANTADO E FUNCIONANDO**

- **URL**: https://costcollector.selectsolucoes.com
- **Status**: Ativo e operacional
- **Versão**: 3.0 - Complete Analytics
- **Arquitetura**: ECS Fargate com containers Docker

## 📊 Dados Coletados

### **Análise Completa de Custos:**
- **Custos mensais**: Últimos 6 meses com histórico
- **Mês atual**: Acompanhamento diário + acumulado
- **Previsões**: Forecast de custos futuros
- **Orçamentos**: Limites e % de utilização
- **Alertas**: Contagem de alertas por mês

### **Detalhamento por Serviço:**
- EC2, RDS, ECS, S3, Lambda, CloudWatch
- Tipos de uso específicos por serviço
- Recursos individuais (instâncias, volumes)
- Custos por região e zona de disponibilidade

## 🌐 Endpoints da API

### **Análise Completa:**
- `GET /costs/overview` - Visão geral completa
- `GET /costs/monthly` - Últimos 6 meses
- `GET /costs/current-month` - Progresso do mês atual
- `GET /budgets` - Orçamentos com % de uso
- `GET /alerts` - Alertas do mês atual

### **Análise Detalhada:**
- `GET /costs/detailed` - Detalhamento por serviço
- `GET /costs/by-service` - Agregação por serviço
- `GET /costs/resources` - Custos por recurso
- `GET /health` - Status do sistema

## 🏗️ Arquitetura

### **Componentes Principais:**
- **ECS Fargate Cluster**: Execução serverless
- **Application Load Balancer**: SSL + distribuição
- **MySQL RDS**: Armazenamento de dados
- **EventBridge**: Agendamento automático
- **Secrets Manager**: Credenciais seguras

### **Serviços:**
1. **Data Collector**: Coleta automática de dados AWS
2. **API Service**: REST API para consultas
3. **Report Generator**: Geração de relatórios

## 📦 Estrutura de Dados

### **Tabelas MySQL:**

```sql
-- Custos mensais (6 meses)
monthly_costs: year_month, total_cost, forecasted_cost, currency

-- Acompanhamento mês atual  
current_month_costs: date, daily_cost, month_to_date, forecasted_month

-- Orçamentos da conta
budgets: budget_name, budget_limit, actual_spend, forecasted_spend

-- Alertas de custo
cost_alerts: alert_date, alert_type, actual_amount, message

-- Detalhamento por serviço
cost_data_detailed: service_name, usage_type, cost, resource_id
```

## ⏰ Coleta Automática

- **Frequência**: Diária às 06:00 UTC
- **Período**: Últimos 6 meses + mês atual
- **Fontes**: Cost Explorer + Budgets API + Forecast API
- **Armazenamento**: MySQL com UPSERT (evita duplicatas)

## 🛠️ Deploy

### **Pré-requisitos:**
- AWS CLI configurado
- Docker instalado
- Terraform instalado

### **Deploy Completo:**
```bash
# Clone do repositório
git clone https://github.com/henriquepiloto/aws-cost-budget-reporterv2.git
cd aws-cost-budget-reporterv2

# Deploy da infraestrutura
cd cost-reporter/infrastructure/terraform
terraform init
terraform apply

# Deploy dos containers
cd ../../..
make deploy
```

### **Comandos Disponíveis:**
```bash
make deploy         # Deploy completo
make build          # Build das imagens
make test           # Teste dos endpoints
make status         # Status do ECS
make logs           # Logs em tempo real
make clean          # Limpeza
```

## 📈 Recursos AWS Utilizados

### **Compute:**
- ECS Fargate (1 task API service)
- EventBridge (agendamento)
- Lambda (preservado para compatibilidade)

### **Storage:**
- MySQL RDS (Aurora)
- S3 (frontend e relatórios)
- ECR (repositórios Docker)

### **Network:**
- VPC existente integrada
- Application Load Balancer + SSL
- Route53 DNS

### **Security:**
- ACM (certificado SSL)
- Secrets Manager (credenciais)
- IAM roles específicas

## 💰 Otimização de Custos

- **Fargate Spot**: Até 70% economia
- **1 Task**: Redução de 50% vs 2 tasks
- **Scheduled Tasks**: Execução sob demanda
- **Auto Scaling**: Ajuste automático

## 📊 Exemplo de Dados Coletados

```json
{
  "monthly_costs_6_months": [
    {"year_month": "2025-09", "total_cost": 4850.25, "currency": "USD"},
    {"year_month": "2025-08", "total_cost": 4720.18, "currency": "USD"}
  ],
  "current_month": {
    "date": "2025-09-26",
    "daily_cost": 162.60,
    "month_to_date": 4230.45,
    "forecasted_month": 4950.00
  },
  "budgets": [
    {
      "budget_name": "Monthly-Budget",
      "budget_limit": 5000.00,
      "actual_spend": 4230.45,
      "usage_percentage": 84.61
    }
  ],
  "alerts_this_month": {
    "alert_count": 3,
    "last_message": "Budget threshold exceeded"
  }
}
```

## 🔧 Configuração

### **Variáveis Terraform:**
```hcl
domain_name = "costcollector.selectsolucoes.com"
environment = "prod"
region = "us-east-1"
```

### **Integração:**
- **VPC**: vpc-04c0a089dd691442c
- **RDS**: glpi-database-instance-1
- **Secrets**: cost-reporter-db-credentials

## 📈 Monitoramento

- **CloudWatch Logs**: /ecs/cost-reporter/*
- **Health Checks**: Automáticos via ALB
- **Métricas**: CPU, memória, requests
- **Alertas**: SNS notifications

## 🔄 Esteira de Deploy

- **Scripts locais**: deploy-local.sh + Makefile
- **Docker**: Multi-stage builds otimizados
- **ECR**: Push automático de imagens
- **ECS**: Update de serviços
- **Gitignore**: Configurado para Terraform

## 🎯 Evolução do Projeto

**v1.0**: Sistema básico Lambda  
**v2.0**: Migração ECS + detalhamento por serviço  
**v3.0**: Análise completa com orçamentos, previsões e alertas  

---

**Desenvolvido por**: Henrique Piloto  
**Repositório**: aws-cost-budget-reporterv2  
**URL**: https://costcollector.selectsolucoes.com  
**Última atualização**: 2025-09-26
