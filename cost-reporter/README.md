# Cost Reporter - ECS Implementation

Sistema de monitoramento de custos AWS implementado com ECS Fargate.

## 🌐 Acesso

**URL Produção**: https://costcollector.selectsolucoes.com

## 🏗️ Arquitetura

### Serviços ECS
- **API Service**: FastAPI REST API (2 tasks)
- **Data Collector**: Coleta dados Cost Explorer
- **Report Generator**: Gera relatórios S3

### Infraestrutura
- **Cluster**: cost-reporter-cluster
- **Load Balancer**: SSL + Health checks
- **Storage**: DynamoDB + S3
- **Networking**: VPC existente integrada

## 🚀 Deploy

```bash
# Build containers
./build-and-deploy.sh

# Deploy infraestrutura
cd infrastructure/terraform
terraform apply
```

## 📊 Endpoints

- `GET /` - API info
- `GET /health` - Health check  
- `GET /costs` - Cost data

## 🔧 Configuração

Domain: costcollector.selectsolucoes.com
Environment: prod
Region: us-east-1
