# 🛡️ Backup & Rollback Plan - ECS Migration

## 🎯 **Objetivo**
Garantir que a migração para ECS não cause perda de dados ou interrupção dos serviços existentes.

## 📋 **Recursos Existentes Preservados**

### ✅ **Infraestrutura Mantida**
- **VPC:** `vpc-04c0a089dd691442c` (workflow VPC)
- **RDS:** `glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com`
- **Lambda:** `chatbot-auth` (Prisma Admin)
- **Security Groups:** `sg-0df74898d34cbea3d`
- **Subnets:** Existentes + adicionais se necessário
- **Route53:** `selectsolucoes.com` zone

### ✅ **Serviços Ativos Preservados**
- **Prisma Admin:** https://prisma.selectsolucoes.com
- **API Gateway:** `m153no51s0.execute-api.us-east-1.amazonaws.com`
- **S3 Buckets:** `prisma-admin-selectsolucoes`
- **CloudFront:** `E1SAZUX6DR5QF3`

## 🔒 **Estratégia de Backup**

### **1. Backup do Banco de Dados**
```bash
# Backup completo do RDS
aws rds create-db-snapshot \
  --db-instance-identifier glpi-database-instance-1 \
  --db-snapshot-identifier glpi-backup-before-ecs-migration-$(date +%Y%m%d)

# Backup específico das tabelas do Prisma Admin
mysqldump -h glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com \
  -u select_admin -p glpi_select \
  chatbot_users chatbot_config chatbot_visual_config > prisma_admin_backup.sql
```

### **2. Backup das Configurações**
```bash
# Backup da função Lambda
aws lambda get-function --function-name chatbot-auth > chatbot-auth-backup.json

# Backup das configurações do API Gateway
aws apigateway get-rest-api --rest-api-id m153no51s0 > api-gateway-backup.json

# Backup dos arquivos S3
aws s3 sync s3://prisma-admin-selectsolucoes/ ./s3-backup/
```

### **3. Backup do Código**
```bash
# Commit atual no GitHub
cd /home/hpiloto/aws-cost-budget-reporterv2
git add .
git commit -m "🛡️ Backup before ECS migration"
git push origin main
git tag -a "pre-ecs-migration" -m "Backup before ECS migration"
git push origin pre-ecs-migration
```

## 🚀 **Plano de Migração Segura**

### **Fase 1: Preparação (Zero Impacto)**
1. **Criar recursos ECS** (não afeta existentes)
2. **Configurar ECR repositories**
3. **Criar DynamoDB table** (nova)
4. **Configurar S3 buckets** (novos)

### **Fase 2: Deploy Gradual**
1. **Deploy ECS services** em modo teste
2. **Configurar ALB** em subdomínio teste
3. **Validar funcionamento** sem afetar produção
4. **Testes de integração**

### **Fase 3: Cutover Controlado**
1. **DNS switch** gradual
2. **Monitoramento ativo**
3. **Rollback imediato** se necessário

## 🔄 **Plano de Rollback**

### **Rollback Nível 1: DNS (< 5 minutos)**
```bash
# Reverter DNS para Lambda/API Gateway
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://rollback-dns.json
```

### **Rollback Nível 2: Infraestrutura (< 15 minutos)**
```bash
# Parar serviços ECS
aws ecs update-service \
  --cluster cost-reporter-cluster \
  --service cost-reporter-api-service \
  --desired-count 0

# Restaurar configurações originais
aws lambda update-function-configuration \
  --function-name chatbot-auth \
  --vpc-config file://original-vpc-config.json
```

### **Rollback Nível 3: Dados (< 30 minutos)**
```bash
# Restaurar snapshot do banco
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier glpi-database-instance-1-restored \
  --db-snapshot-identifier glpi-backup-before-ecs-migration-YYYYMMDD

# Restaurar dados específicos
mysql -h glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com \
  -u select_admin -p glpi_select < prisma_admin_backup.sql
```

## 📊 **Monitoramento Durante Migração**

### **Métricas Críticas**
- **Prisma Admin uptime:** https://prisma.selectsolucoes.com
- **API response time:** < 500ms
- **Database connections:** Monitorar RDS
- **Error rates:** CloudWatch Logs

### **Alertas Configurados**
```bash
# Alerta se Prisma Admin ficar indisponível
aws cloudwatch put-metric-alarm \
  --alarm-name "PrismaAdminDown" \
  --alarm-description "Prisma Admin is down" \
  --metric-name "StatusCheckFailed" \
  --namespace "AWS/Route53HealthCheck" \
  --statistic "Maximum" \
  --period 60 \
  --threshold 1 \
  --comparison-operator "GreaterThanOrEqualToThreshold"
```

## ✅ **Checklist de Validação**

### **Pré-Migração**
- [ ] Backup do RDS criado
- [ ] Backup da Lambda criado
- [ ] Backup do S3 criado
- [ ] Código commitado no GitHub
- [ ] Plano de rollback testado
- [ ] Equipe notificada

### **Durante Migração**
- [ ] Prisma Admin funcionando
- [ ] API Gateway respondendo
- [ ] Banco de dados acessível
- [ ] Logs sem erros críticos
- [ ] Métricas dentro do normal

### **Pós-Migração**
- [ ] ECS services rodando
- [ ] ALB funcionando
- [ ] DNS resolvendo
- [ ] SSL certificado válido
- [ ] Integração com RDS funcionando
- [ ] Monitoramento ativo

## 🚨 **Critérios de Rollback**

### **Rollback Automático Se:**
- Prisma Admin indisponível > 2 minutos
- Error rate > 5% por 5 minutos
- Response time > 2 segundos por 10 minutos
- Perda de conectividade com RDS

### **Rollback Manual Se:**
- Funcionalidades críticas não funcionando
- Dados inconsistentes
- Performance degradada significativamente
- Problemas de segurança identificados

## 📞 **Contatos de Emergência**

### **Equipe Técnica**
- **DevOps Lead:** Disponível durante migração
- **Database Admin:** Para questões de RDS
- **Network Admin:** Para questões de VPC/DNS

### **Comunicação**
- **Slack:** #migration-ecs
- **Email:** equipe-tecnica@selectsolucoes.com
- **Telefone:** Emergência 24/7

## 🎯 **Cronograma de Execução**

### **Preparação (1 dia)**
- Manhã: Backups e validações
- Tarde: Deploy de teste

### **Migração (4 horas)**
- 18:00-19:00: Deploy ECS
- 19:00-20:00: Testes
- 20:00-21:00: DNS switch
- 21:00-22:00: Validação final

### **Monitoramento (24 horas)**
- Monitoramento ativo por 24h
- Rollback disponível por 48h
- Cleanup após 1 semana

---

**🛡️ Este plano garante que a migração seja segura e reversível a qualquer momento!**
