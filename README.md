# AWS Cost Budget Reporter v3.0

Sistema de monitoramento de custos AWS com Chat FinOps inteligente, arquitetura ECS Fargate e coleta básica de dados.

## 🚀 Status do Projeto

**✅ IMPLANTADO E FUNCIONANDO**

- **URL**: https://costcollector.selectsolucoes.com
- **Status**: Ativo e operacional
- **Versão**: 3.0 - FinOps Chat + Basic Analytics
- **Arquitetura**: ECS Fargate com containers Docker

## 💬 Chat FinOps Inteligente

### **Funcionalidade Principal:**
- **Chat especializado** em análise de custos AWS
- **Contexto automático** com dados reais da conta
- **Integração Bedrock** para respostas inteligentes
- **Análise executiva** com recomendações acionáveis

## 📊 Dados Coletados

### **Coleta Básica de Custos:**
- **Custos mensais**: Últimos 6 meses com histórico
- **Mês atual**: Acompanhamento diário + acumulado
- **Account ID**: 727706432228 (Select Soluções)

## 🌐 Endpoints da API

### **Endpoints Implementados:**
- `POST /chat` - Chat FinOps com contexto AWS
- `GET /costs/overview` - Visão geral dos custos
- `GET /health` - Status do sistema
- `GET /` - Informações da API

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

### **Tabelas MySQL (Implementadas):**

```sql
-- Custos mensais (6 meses)
monthly_costs: month_year, total_cost, forecasted_cost, currency

-- Acompanhamento mês atual  
current_month_costs: date, daily_cost, month_to_date, forecasted_month, currency
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
    {"month_year": "2025-09", "total_cost": 4850.25, "currency": "USD"},
    {"month_year": "2025-08", "total_cost": 4720.18, "currency": "USD"}
  ],
  "current_month": {
    "date": "2025-09-26",
    "daily_cost": 162.60,
    "month_to_date": 4230.45,
    "forecasted_month": 4950.00,
    "currency": "USD"
  }
}
```

## 💬 Exemplo de Chat FinOps

```bash
# Pergunta ao chat
curl -X POST https://costcollector.selectsolucoes.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Como estão os custos este mês?"}'

# Resposta inteligente
{
  "response": "📊 ANÁLISE FINOPS - Select Soluções\n\n• Custo MTD: $7,288.18 USD\n• Média diária: $162.68 USD\n• Variação MoM: +24.7%\n\nRECOMENDAÇÕES:\n• Revisar instâncias EC2 subutilizadas\n• Considerar Reserved Instances\n• Economia estimada: $500-800/mês",
  "session_id": "finops_session",
  "context_used": {
    "account_id": "727706432228",
    "has_data": true,
    "months_available": 6
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
**v2.0**: Migração ECS + estrutura básica  
**v3.0**: Chat FinOps inteligente + coleta básica de custos  

---

**Desenvolvido por**: Henrique Piloto  
**Repositório**: aws-cost-budget-reporterv2  
**URL**: https://costcollector.selectsolucoes.com  
**Chat FinOps**: POST /chat  
**Última atualização**: 2025-09-26
