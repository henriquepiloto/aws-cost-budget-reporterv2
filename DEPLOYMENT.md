# Deployment Guide - Cost Reporter v3.0

## 🚀 Esteira de Deploy Completa

### **Deploy Automático Local**
```bash
# Deploy completo
make deploy

# Ou manualmente
./deploy-local.sh
```

### **Comandos Disponíveis**

#### **Build e Deploy:**
```bash
make build          # Build local das imagens
make deploy         # Deploy completo para AWS
make clean          # Limpa imagens Docker
```

#### **Testes e Monitoramento:**
```bash
make test           # Testa todos os endpoints
make status         # Status do serviço ECS
make logs           # Logs em tempo real
```

#### **Infraestrutura:**
```bash
make infra-plan     # Terraform plan
make infra-apply    # Terraform apply
```

## 📋 Endpoints para Teste

### **Análise Completa:**
```bash
# Visão geral completa
curl https://costcollector.selectsolucoes.com/costs/overview

# Custos mensais (6 meses)
curl https://costcollector.selectsolucoes.com/costs/monthly

# Mês atual
curl https://costcollector.selectsolucoes.com/costs/current-month

# Orçamentos
curl https://costcollector.selectsolucoes.com/budgets

# Alertas
curl https://costcollector.selectsolucoes.com/alerts
```

### **Análise Detalhada:**
```bash
# Por serviço
curl https://costcollector.selectsolucoes.com/costs/by-service

# Recursos específicos
curl https://costcollector.selectsolucoes.com/costs/resources

# Health check
curl https://costcollector.selectsolucoes.com/health
```

## 🔧 Configuração

### **Variáveis de Ambiente:**
- **Region**: us-east-1
- **Cluster**: cost-reporter-cluster
- **Domain**: costcollector.selectsolucoes.com

### **Secrets Manager:**
- **Secret**: cost-reporter-db-credentials
- **Database**: cost_reporter (MySQL)

### **Recursos AWS:**
- **VPC**: vpc-04c0a089dd691442c
- **RDS**: glpi-database-instance-1
- **ECR**: 3 repositórios de imagens

## 🔄 Fluxo de Deploy

1. **Build** → Construção das imagens Docker
2. **Push** → Upload para ECR
3. **Update** → Atualização do serviço ECS
4. **Health Check** → Verificação automática
5. **Logs** → Monitoramento em tempo real

## ⏰ Coleta Automática

### **Agendamento:**
- **Frequência**: Diária às 06:00 UTC
- **EventBridge**: cost-reporter-data-collector-schedule
- **Target**: ECS Task Fargate

### **Dados Coletados:**
- Custos mensais (6 meses)
- Custos diários do mês atual
- Previsões de custo
- Orçamentos da conta
- Alertas de custo

## 📊 Estrutura de Dados

### **Tabelas MySQL:**
```sql
monthly_costs         # Custos mensais
current_month_costs   # Mês atual diário
budgets              # Orçamentos AWS
cost_alerts          # Alertas de custo
cost_data_detailed   # Detalhamento por serviço
```

## 🎯 Verificação de Deploy

### **Status do Sistema:**
```bash
# Status ECS
make status

# Teste completo
make test

# Logs em tempo real
make logs
```

### **Exemplo de Resposta Saudável:**
```json
{
  "status": "healthy",
  "version": "3.0",
  "features": [
    "monthly_costs_6_months",
    "current_month_tracking",
    "cost_forecasting", 
    "budget_monitoring",
    "daily_alerts_tracking"
  ]
}
```

## 🚨 Troubleshooting

### **Problemas Comuns:**

1. **Task falhando**: Verificar logs com `make logs`
2. **API não respondendo**: Verificar health check
3. **Dados não coletados**: Verificar permissões IAM
4. **Erro de banco**: Verificar Secrets Manager

### **Comandos de Debug:**
```bash
# Status detalhado
aws ecs describe-services --cluster cost-reporter-cluster --services cost-reporter-api-service

# Logs específicos
aws logs tail /ecs/cost-reporter/data-collector --follow

# Teste de conectividade
curl -v https://costcollector.selectsolucoes.com/health
```

---

**Sistema v3.0 - Complete Analytics**  
**Última atualização**: 2025-09-26
