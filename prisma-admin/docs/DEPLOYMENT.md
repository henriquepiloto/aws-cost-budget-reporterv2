# 🚀 Guia de Deploy - Prisma Admin

Este guia detalha como fazer o deploy completo do sistema Prisma Admin na AWS.

## 📋 **Pré-requisitos**

### **Ferramentas Necessárias**
- AWS CLI configurado
- Conta AWS com permissões administrativas
- Domínio registrado (opcional)
- MySQL client para configurar banco

### **Recursos AWS Necessários**
- Amazon RDS (MySQL)
- AWS Lambda
- API Gateway
- Amazon S3
- CloudFront
- Certificate Manager (para SSL)
- Route53 (para domínio)

## 🗄️ **1. Configurar Banco de Dados**

### **Criar Instância RDS**
```bash
aws rds create-db-instance \
  --db-instance-identifier prisma-database \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password SuaSenhaSegura123 \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --storage-encrypted
```

### **Configurar Tabelas**
```sql
-- Conectar ao banco
mysql -h prisma-database.xxxxxxxxx.us-east-1.rds.amazonaws.com -u admin -p

-- Criar database
CREATE DATABASE prisma_admin;
USE prisma_admin;

-- Tabela de usuários
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

-- Tabela de configurações por usuário
CREATE TABLE chatbot_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    config_key VARCHAR(100),
    config_value TEXT,
    FOREIGN KEY (user_id) REFERENCES chatbot_users(id)
);

-- Tabela de configurações visuais globais
CREATE TABLE chatbot_visual_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE,
    config_value LONGTEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Criar usuário admin padrão
INSERT INTO chatbot_users (username, password, email, role, permissions) 
VALUES ('admin', SHA2('admin123', 256), 'admin@selectsolucoes.com', 'admin', 'all');
```

## ⚡ **2. Configurar Backend (Lambda)**

### **Preparar Dependências**
```bash
# Criar diretório do projeto
mkdir lambda-package && cd lambda-package

# Instalar dependências Python
pip install pymysql PyJWT -t .

# Copiar código da função
cp ../backend/lambda_function.py .
```

### **Criar Função Lambda**
```bash
# Criar pacote
zip -r lambda-package.zip .

# Criar função
aws lambda create-function \
  --function-name prisma-admin \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-package.zip \
  --timeout 30 \
  --memory-size 256
```

### **Configurar VPC (se necessário)**
```bash
aws lambda update-function-configuration \
  --function-name prisma-admin \
  --vpc-config SubnetIds=subnet-xxxxx,subnet-yyyyy,SecurityGroupIds=sg-zzzzz
```

## 🌐 **3. Configurar API Gateway**

### **Criar API**
```bash
# Criar REST API
API_ID=$(aws apigateway create-rest-api \
  --name prisma-admin-api \
  --query 'id' --output text)

# Obter resource root
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' --output text)
```

### **Criar Recursos e Métodos**
```bash
# Criar recursos
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part login

aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part chat

aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part users

aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part config

aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part visual-config
```

### **Configurar CORS**
```bash
# Para cada recurso, adicionar OPTIONS method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

# Configurar integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}'
```

### **Deploy da API**
```bash
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

## 🌍 **4. Configurar Frontend (S3 + CloudFront)**

### **Criar Bucket S3**
```bash
# Criar bucket
aws s3 mb s3://prisma-admin-frontend

# Configurar para website estático
aws s3 website s3://prisma-admin-frontend \
  --index-document index.html \
  --error-document index.html

# Upload dos arquivos
aws s3 sync frontend/ s3://prisma-admin-frontend/
```

### **Configurar CloudFront**
```json
{
  "CallerReference": "prisma-admin-2025",
  "Comment": "Prisma Admin Distribution",
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-prisma-admin-frontend",
        "DomainName": "prisma-admin-frontend.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-prisma-admin-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Enabled": true
}
```

```bash
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

## 🔒 **5. Configurar SSL e Domínio**

### **Solicitar Certificado SSL**
```bash
aws acm request-certificate \
  --domain-name prisma.seudominio.com \
  --validation-method DNS \
  --region us-east-1
```

### **Configurar Route53**
```bash
# Criar hosted zone
aws route53 create-hosted-zone \
  --name seudominio.com \
  --caller-reference $(date +%s)

# Criar record para CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://route53-change.json
```

## 🔧 **6. Configurações Finais**

### **Variáveis de Ambiente Lambda**
```bash
aws lambda update-function-configuration \
  --function-name prisma-admin \
  --environment Variables='{
    "DB_HOST":"prisma-database.xxxxxxxxx.us-east-1.rds.amazonaws.com",
    "DB_USER":"admin",
    "DB_PASSWORD":"SuaSenhaSegura123",
    "DB_NAME":"prisma_admin",
    "JWT_SECRET":"sua-chave-secreta-jwt"
  }'
```

### **Permissões IAM**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    }
  ]
}
```

## ✅ **7. Verificação do Deploy**

### **Testes de Funcionalidade**
```bash
# Testar API
curl -X POST https://api.seudominio.com/prod/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Testar frontend
curl -I https://prisma.seudominio.com

# Testar visual config (público)
curl https://api.seudominio.com/prod/visual-config
```

### **Monitoramento**
- CloudWatch Logs para Lambda
- CloudWatch Metrics para API Gateway
- CloudFront Access Logs
- RDS Performance Insights

## 🔄 **8. Atualizações**

### **Atualizar Frontend**
```bash
aws s3 sync frontend/ s3://prisma-admin-frontend/
aws cloudfront create-invalidation \
  --distribution-id E123456789 \
  --paths "/*"
```

### **Atualizar Backend**
```bash
zip -r lambda-package.zip .
aws lambda update-function-code \
  --function-name prisma-admin \
  --zip-file fileb://lambda-package.zip
```

## 🚨 **Troubleshooting**

### **Problemas Comuns**

**1. CORS Errors**
- Verificar configuração OPTIONS em todos os recursos
- Confirmar headers CORS na Lambda

**2. Database Connection**
- Verificar security groups
- Confirmar VPC configuration da Lambda
- Testar conectividade do RDS

**3. SSL Certificate**
- Certificado deve estar em us-east-1 para CloudFront
- Validação DNS deve estar completa

**4. Lambda Timeout**
- Aumentar timeout para 30 segundos
- Verificar cold start do Bedrock

### **Logs Úteis**
```bash
# Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/prisma-admin

# API Gateway logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs

# CloudFront logs (se habilitado)
aws s3 ls s3://cloudfront-logs-bucket/
```

## 📊 **Custos Estimados**

| Serviço | Custo Mensal (USD) |
|---------|-------------------|
| RDS t3.micro | ~$15 |
| Lambda (1M requests) | ~$0.20 |
| API Gateway | ~$3.50 |
| S3 + CloudFront | ~$1.00 |
| Route53 | ~$0.50 |
| **Total** | **~$20.20** |

*Custos podem variar baseado no uso real*
