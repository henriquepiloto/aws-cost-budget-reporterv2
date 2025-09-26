# AWS Secrets Manager - Configuração de Credenciais do Banco

## 📋 Visão Geral

A versão 2 do AWS Cost Budget Reporter utiliza o AWS Secrets Manager para armazenar credenciais do banco de dados de forma segura, eliminando a necessidade de hardcoded credentials nos scripts.

## 🔧 Configuração do Secret

### Secret Name: `glpidatabaseadmin`

O secret deve conter as seguintes chaves no formato JSON:

```json
{
  "username": "select_admin",
  "password": "sua_senha_segura",
  "host": "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com",
  "port": 3306,
  "dbname": "aws_costs"
}
```

## 🚀 Criação do Secret

### Via AWS CLI

```bash
# Criar o secret
aws secretsmanager create-secret \
    --name glpidatabaseadmin \
    --description "Credenciais do banco de dados para AWS Cost Reporter" \
    --secret-string '{
        "username": "select_admin",
        "password": "GR558AvfoYFz7NTZ1q8n",
        "host": "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com",
        "port": 3306,
        "dbname": "aws_costs"
    }' \
    --region us-east-1
```

### Via Console AWS

1. Acesse **AWS Secrets Manager** no console
2. Clique em **Store a new secret**
3. Selecione **Other type of secret**
4. Adicione as chaves:
   - `username`: select_admin
   - `password`: sua_senha
   - `host`: glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com
   - `port`: 3306
   - `dbname`: aws_costs
5. Nome do secret: `glpidatabaseadmin`
6. Descrição: "Credenciais do banco de dados para AWS Cost Reporter"

## 🔒 Permissões IAM

### Para a EC2/Role que executa os scripts:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT-ID:secret:glpidatabaseadmin-*"
    }
  ]
}
```

### Policy Completa (S3 + Secrets + STS):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::seu-bucket/roles.json"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT-ID:secret:glpidatabaseadmin-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sts:AssumeRole"
      ],
      "Resource": "arn:aws:iam::*:role/CrossAccountRole"
    }
  ]
}
```

## 🔄 Rotação de Credenciais

### Configurar Rotação Automática

```bash
aws secretsmanager rotate-secret \
    --secret-id glpidatabaseadmin \
    --rotation-rules AutomaticallyAfterDays=30 \
    --region us-east-1
```

### Rotação Manual

```bash
# Atualizar senha
aws secretsmanager update-secret \
    --secret-id glpidatabaseadmin \
    --secret-string '{
        "username": "select_admin",
        "password": "nova_senha_segura",
        "host": "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com",
        "port": 3306,
        "dbname": "aws_costs"
    }' \
    --region us-east-1
```

## 🔍 Verificação e Testes

### Testar Acesso ao Secret

```bash
# Verificar se o secret existe
aws secretsmanager describe-secret --secret-id glpidatabaseadmin --region us-east-1

# Recuperar valor do secret (cuidado com logs!)
aws secretsmanager get-secret-value --secret-id glpidatabaseadmin --region us-east-1
```

### Teste de Conexão Python

```python
import boto3
import json

def test_secret_access():
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId='glpidatabaseadmin')
        secret = json.loads(response['SecretString'])
        print("✓ Secret acessado com sucesso")
        print(f"Host: {secret['host']}")
        print(f"Username: {secret['username']}")
        return True
    except Exception as e:
        print(f"✗ Erro ao acessar secret: {e}")
        return False

test_secret_access()
```

## 📊 Monitoramento

### CloudWatch Metrics

- `secretsmanager:GetSecretValue` - Chamadas de recuperação
- Erros de acesso ao secret
- Tentativas de rotação

### CloudTrail Events

```json
{
  "eventName": "GetSecretValue",
  "sourceIPAddress": "10.0.1.100",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
    "arn": "arn:aws:sts::123456789012:assumed-role/EC2-Role/i-1234567890abcdef0"
  },
  "resources": [
    {
      "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:glpidatabaseadmin-AbCdEf"
    }
  ]
}
```

## 🚨 Troubleshooting

### Erro: "Secrets Manager can't find the specified secret"

```bash
# Verificar se o secret existe na região correta
aws secretsmanager list-secrets --region us-east-1 | grep glpidatabaseadmin
```

### Erro: "Access Denied"

1. Verificar permissões IAM da EC2/Role
2. Confirmar ARN do secret na policy
3. Verificar se a região está correta

### Erro: "Invalid JSON in secret"

```bash
# Validar JSON do secret
aws secretsmanager get-secret-value --secret-id glpidatabaseadmin --region us-east-1 --query SecretString --output text | jq .
```

## 🔐 Boas Práticas de Segurança

### 1. Princípio do Menor Privilégio
- Conceder apenas `secretsmanager:GetSecretValue`
- Restringir a ARN específica do secret

### 2. Rotação Regular
- Configurar rotação automática (30-90 dias)
- Testar rotação em ambiente de desenvolvimento

### 3. Monitoramento
- Alertas CloudWatch para falhas de acesso
- Logs CloudTrail para auditoria

### 4. Backup e Recuperação
- Replicação cross-region do secret
- Backup das configurações

## ✅ Vantagens do Secrets Manager

- 🔒 **Criptografia**: Dados criptografados em repouso e trânsito
- 🔄 **Rotação Automática**: Rotação programada de credenciais
- 📊 **Auditoria**: Logs completos de acesso via CloudTrail
- 🌍 **Multi-Region**: Replicação automática entre regiões
- 🔐 **IAM Integration**: Controle granular de acesso
- 💰 **Cost-Effective**: Pagamento por uso

## 📝 Migração da v1 para v2

### Antes (v1)
```python
rds_user = 'select_admin'
rds_password = 'GR558AvfoYFz7NTZ1q8n'  # ❌ Hardcoded
```

### Depois (v2)
```python
db_config = get_database_credentials()  # ✅ Secrets Manager
```

## 📞 Suporte

Para dúvidas sobre configuração do Secrets Manager, consulte:
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- Abra uma issue no GitHub do projeto
