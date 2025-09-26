# AWS Cost Budget Reporter v2

Sistema completo de monitoramento e relatórios de custos AWS usando arquitetura ECS Fargate.

## 🚀 Status do Projeto

**✅ IMPLANTADO E FUNCIONANDO**

- **URL**: https://costcollector.selectsolucoes.com
- **Status**: Ativo e operacional
- **Arquitetura**: ECS Fargate com containers Docker
- **SSL**: Certificado válido via ACM

## 🏗️ Arquitetura

### Componentes Principais
- **ECS Fargate Cluster**: Execução de containers serverless
- **Application Load Balancer**: Distribuição de tráfego com SSL
- **ECR**: Repositórios de imagens Docker
- **DynamoDB**: Armazenamento de dados de custo
- **S3**: Buckets para frontend e relatórios
- **Route53**: DNS e certificado SSL
- **Secrets Manager**: Credenciais seguras

### Serviços
1. **API Service**: API REST para consulta de dados
2. **Data Collector**: Coleta automática de dados de custo
3. **Report Generator**: Geração de relatórios periódicos

## 📦 Containers Docker

### API Service
```dockerfile
FROM python:3.11-slim
# FastAPI + Uvicorn
EXPOSE 8000
```

### Data Collector
```dockerfile
FROM python:3.11-slim
# Boto3 + Cost Explorer API
```

### Report Generator
```dockerfile
FROM python:3.11-slim
# Boto3 + Jinja2 templates
```

## 🛠️ Deploy

### Pré-requisitos
- AWS CLI configurado
- Docker instalado
- Terraform instalado

### Build e Deploy
```bash
# Build e push das imagens
./build-and-deploy.sh

# Deploy da infraestrutura
cd cost-reporter/infrastructure/terraform
terraform init
terraform apply
```

## 🌐 Endpoints da API

- `GET /` - Informações da API
- `GET /health` - Health check
- `GET /costs` - Dados de custo coletados

## 📊 Recursos AWS Utilizados

### Compute
- **ECS Fargate**: 2 tasks API service
- **EventBridge**: Agendamento de tarefas

### Storage
- **DynamoDB**: cost-reporter-cost-data
- **S3**: Frontend e relatórios
- **ECR**: 3 repositórios de imagens

### Network
- **VPC**: Integração com infraestrutura existente
- **ALB**: Load balancer com SSL
- **Route53**: DNS costcollector.selectsolucoes.com

### Security
- **ACM**: Certificado SSL automático
- **Secrets Manager**: Credenciais RDS
- **IAM**: Roles e políticas específicas

## 💰 Otimização de Custos

- **Fargate Spot**: Até 70% de economia
- **Auto Scaling**: Ajuste automático de capacidade
- **Scheduled Tasks**: Execução sob demanda
- **Lifecycle Policies**: Limpeza automática de imagens

## 🔧 Configuração

### Variáveis Terraform
```hcl
domain_name = "costcollector.selectsolucoes.com"
environment = "prod"
```

### Integração com Recursos Existentes
- **VPC**: vpc-04c0a089dd691442c
- **RDS**: glpi-database-instance-1
- **Lambda**: chatbot-auth (preservado)

## 📈 Monitoramento

- **CloudWatch Logs**: /ecs/cost-reporter/*
- **ECS Service Events**: Monitoramento automático
- **ALB Health Checks**: Verificação de saúde

## 🔄 CI/CD

Repositório integrado com build automatizado:
- Dockerfiles otimizados
- Scripts de deploy
- Gitignore configurado
- Documentação completa

---

**Desenvolvido por**: Henrique Piloto  
**Repositório**: aws-cost-budget-reporterv2  
**Última atualização**: 2025-09-26
