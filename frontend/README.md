# Cloudinho FinOps Frontend

Frontend Next.js para o sistema Cloudinho FinOps - Chat inteligente para análise de custos AWS.

## 🌐 **Acesso**
**URL Produção**: https://cloudinho.selectsolucoes.com

## 🚀 **Funcionalidades**

### **Autenticação**
- Sistema de login com JWT
- Controle de usuários e roles
- Logs de acesso detalhados

### **Chat FinOps**
- Integração com Amazon Bedrock (Claude 3.5 Sonnet)
- Contexto de custos AWS em tempo real
- Interface moderna e responsiva
- Histórico de conversas

### **Controle de Usuários**
- Gerenciamento de usuários
- Logs de ações e acessos
- Sistema de permissões

## 🛠 **Tecnologias**

- **Framework**: Next.js 14
- **Linguagem**: TypeScript
- **Estilização**: Tailwind CSS
- **Banco de Dados**: MySQL (compartilhado)
- **Autenticação**: JWT + bcrypt
- **Deploy**: Docker + ECS Fargate

## 📦 **Desenvolvimento Local**

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build
npm start
```

## 🚀 **Deploy**

```bash
# Deploy automático
./deploy.sh
```

## 🗄️ **Banco de Dados**

### **Tabelas Utilizadas**
- `users` - Usuários do sistema
- `user_logs` - Logs de acesso
- `chat_logs` - Histórico de conversas

### **Configuração**
- **Host**: glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com
- **Database**: cost_reporter
- **Credenciais**: AWS Secrets Manager

## 🔧 **Variáveis de Ambiente**

```env
NODE_ENV=production
API_URL=https://costs.selectsolucoes.com
DB_HOST=glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com
DB_USER=select_admin
DB_NAME=cost_reporter
DB_PASSWORD=<from-secrets-manager>
JWT_SECRET=cloudinho-secret-key-2024
```

## 🏗️ **Arquitetura**

```
Frontend (Next.js) → API Backend → Bedrock
       ↓
   MySQL Database
```

## 📊 **Monitoramento**

- **Logs**: CloudWatch `/ecs/cost-reporter/frontend`
- **Health Check**: `/api/health`
- **Métricas**: ECS + ALB

## 🔐 **Segurança**

- Autenticação JWT
- Senhas criptografadas (bcrypt)
- HTTPS obrigatório
- Logs de auditoria

## 🎯 **Roadmap**

- [ ] Dashboard Metabase (iframe)
- [ ] Análise de tickets
- [ ] Relatórios personalizados
- [ ] Notificações em tempo real
