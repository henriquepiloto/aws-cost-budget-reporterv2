# Deployment Guide

## 🚀 Esteira de Deploy

### GitHub Actions (Automático)
```yaml
# Trigger: Push para main branch
# Ações: Build → Push ECR → Update ECS
```

### Deploy Local
```bash
# Deploy completo
make deploy

# Ou manualmente
./deploy-local.sh
```

## 📋 Comandos Disponíveis

### Build
```bash
make build          # Build local das imagens
make deploy         # Deploy completo para AWS
```

### Testes
```bash
make test           # Testa endpoints da API
make status         # Status do serviço ECS
```

### Infraestrutura
```bash
make infra-plan     # Terraform plan
make infra-apply    # Terraform apply
```

### Monitoramento
```bash
make logs           # Logs em tempo real
make clean          # Limpa imagens Docker
```

## 🔧 Configuração

### Secrets GitHub Actions
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Variáveis
- **Region**: us-east-1
- **Cluster**: cost-reporter-cluster
- **Domain**: costcollector.selectsolucoes.com

## 🔄 Fluxo de Deploy

1. **Commit** → Push para main
2. **GitHub Actions** → Build automático
3. **ECR** → Push das imagens
4. **ECS** → Update do serviço
5. **Verificação** → Health check automático

## ✅ Verificação

```bash
# Status do deploy
make status

# Teste da API
make test

# Logs em tempo real
make logs
```
