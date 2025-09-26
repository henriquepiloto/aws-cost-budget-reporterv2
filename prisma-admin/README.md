# 🔐 Prisma - Painel Administrativo Cloudinho

Sistema completo de administração para chatbot IA com interface web, autenticação, gerenciamento de usuários e customização visual.

## 🌐 **Acesso ao Sistema**
**URL:** https://prisma.selectsolucoes.com  
**Credenciais Admin:** `admin` / `admin123`

## 📋 **Funcionalidades**

### 🔐 **Autenticação & Segurança**
- Sistema de login com JWT tokens
- Controle de acesso baseado em roles (admin/user)
- Sessões persistentes com auto-login
- Proteção de rotas administrativas

### 💬 **Chat com IA**
- Integração com Amazon Bedrock (Claude 3.5 Sonnet)
- Interface de chat em tempo real
- Configurações personalizáveis (modelo, temperatura, tokens)
- Histórico de conversas

### 👥 **Gerenciamento de Usuários**
- CRUD completo de usuários
- Controle de status (ativo/bloqueado)
- Reset de senhas
- Permissões granulares
- Estatísticas de usuários

### 🎨 **Customização Visual**
- **Nome da aplicação** personalizável
- **Logo personalizado** via URL
- **Cores customizáveis:**
  - Cor primária (botões, elementos ativos)
  - Cor secundária (gradientes)
  - Cor do menu lateral
- **Preview em tempo real**
- **Persistência no banco de dados**

### ⚙️ **Configurações do Sistema**
- Parâmetros do modelo de IA
- Configurações por usuário
- Status do sistema
- Monitoramento de recursos

## 🏗️ **Arquitetura**

### **Frontend**
- **Tecnologia:** HTML5 + CSS3 + JavaScript (Vanilla)
- **Hospedagem:** Amazon S3 + CloudFront
- **Domínio:** prisma.selectsolucoes.com
- **SSL:** AWS Certificate Manager

### **Backend**
- **API:** AWS Lambda + API Gateway
- **Linguagem:** Python 3.9
- **Autenticação:** JWT tokens
- **CORS:** Configurado para acesso web

### **Banco de Dados**
- **Tipo:** Amazon RDS MySQL
- **Instância:** glpi-database-instance-1
- **Tabelas:**
  - `chatbot_users` - Usuários do sistema
  - `chatbot_config` - Configurações por usuário
  - `chatbot_visual_config` - Configurações visuais globais

### **IA & Chat**
- **Serviço:** Amazon Bedrock
- **Modelo:** Claude 3.5 Sonnet
- **Região:** us-east-1

## 📁 **Estrutura do Projeto**

```
prisma-cloudinho-admin/
├── frontend/
│   ├── index.html          # Interface principal
│   └── test.html           # Página de teste
├── backend/
│   └── lambda_function.py  # Função Lambda
├── infrastructure/
│   ├── terraform/          # Configurações Terraform
│   └── aws-cli/           # Scripts AWS CLI
├── docs/
│   ├── API.md             # Documentação da API
│   ├── DEPLOYMENT.md      # Guia de deploy
│   └── CUSTOMIZATION.md   # Guia de customização
└── README.md              # Este arquivo
```

## 🚀 **Instalação & Deploy**

### **Pré-requisitos**
- Conta AWS configurada
- Domínio registrado
- Instância RDS MySQL

### **1. Configurar Backend**
```bash
# Criar função Lambda
aws lambda create-function \
  --function-name chatbot-auth \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-package.zip

# Configurar API Gateway
aws apigateway create-rest-api --name prisma-api
```

### **2. Configurar Frontend**
```bash
# Criar bucket S3
aws s3 mb s3://prisma-admin-selectsolucoes

# Upload dos arquivos
aws s3 sync frontend/ s3://prisma-admin-selectsolucoes/

# Configurar CloudFront
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

### **3. Configurar Banco de Dados**
```sql
-- Criar tabelas necessárias
CREATE TABLE chatbot_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE chatbot_visual_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE,
    config_value LONGTEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🎨 **Customização Visual**

### **Configurações Disponíveis**
1. **Nome da Aplicação**
   - Aparece em toda interface
   - Padrão: "Cloudinho"

2. **Logo Personalizado**
   - URL de imagem externa
   - Formatos: PNG, JPG, SVG
   - Tamanho recomendado: 150x50px

3. **Cores**
   - **Primária:** Botões, links, elementos ativos
   - **Secundária:** Gradientes, elementos secundários  
   - **Menu Lateral:** Cor de fundo do sidebar

### **Como Personalizar**
1. Acesse o painel admin
2. Vá em "🎨 Aparência"
3. Altere as configurações desejadas
4. Clique "💾 Salvar Alterações"
5. As mudanças são aplicadas instantaneamente

## 📊 **Monitoramento**

### **Logs Disponíveis**
- **Lambda:** CloudWatch Logs `/aws/lambda/chatbot-auth`
- **API Gateway:** CloudWatch Logs
- **CloudFront:** Access Logs

### **Métricas**
- Usuários totais e ativos
- Requests por minuto
- Tempo de resposta da API
- Erros e exceções

## 🔧 **Manutenção**

### **Backup do Banco**
```bash
mysqldump -h glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com \
  -u select_admin -p glpi_select > backup.sql
```

### **Atualização do Frontend**
```bash
aws s3 sync frontend/ s3://prisma-admin-selectsolucoes/
aws cloudfront create-invalidation --distribution-id E1SAZUX6DR5QF3 --paths "/*"
```

### **Atualização do Backend**
```bash
zip -r lambda-package.zip lambda_function.py dependencies/
aws lambda update-function-code --function-name chatbot-auth --zip-file fileb://lambda-package.zip
```

## 🐛 **Troubleshooting**

### **Problemas Comuns**

**1. Login não funciona**
- Verificar logs do Lambda
- Confirmar conexão com RDS
- Validar credenciais do banco

**2. Customização não persiste**
- Verificar endpoint `/visual-config`
- Confirmar permissões de escrita no RDS
- Limpar cache do CloudFront

**3. Chat não responde**
- Verificar permissões do Bedrock
- Confirmar região (us-east-1)
- Validar modelo Claude disponível

## 📞 **Suporte**

Para suporte técnico:
- **Email:** suporte@selectsolucoes.com
- **Documentação:** Ver pasta `/docs`
- **Issues:** GitHub Issues

## 📄 **Licença**

Projeto proprietário - Select Soluções  
© 2025 Todos os direitos reservados

---

**Desenvolvido com ❤️ pela equipe Select Soluções**
