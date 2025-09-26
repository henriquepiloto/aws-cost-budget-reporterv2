# Configuração S3 para Roles.json

## 📋 Visão Geral

A versão 2 do AWS Cost Budget Reporter agora carrega o arquivo `roles.json` diretamente do S3, aumentando a segurança ao evitar expor dados sensíveis na EC2.

## 🔧 Configuração

### 1. Criar Bucket S3

```bash
aws s3 mb s3://meu-bucket-cost-reporter --region us-east-1
```

### 2. Upload do roles.json

```bash
aws s3 cp roles.json s3://meu-bucket-cost-reporter/roles.json
```

### 3. Configurar Variável de Ambiente

```bash
export S3_ROLES_URI="s3://meu-bucket-cost-reporter/roles.json"
```

## 📄 Formato do roles.json

```json
[
  {
    "cliente": "Cliente A",
    "account_id": "123456789012", 
    "role_name": "CrossAccountRole"
  },
  {
    "cliente": "Cliente B",
    "account_id": "123456789013",
    "role_name": "CrossAccountRole"
  },
  {
    "cliente": "Cliente C",
    "account_id": "123456789014",
    "role_name": "CostReportRole"
  }
]
```

## 🔒 Permissões IAM

### Para a EC2/Role que executa o script:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::meu-bucket-cost-reporter/roles.json"
    }
  ]
}
```

### Para Cross-Account Roles:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "budgets:DescribeBudgets"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🚀 Exemplos de Uso

### Estrutura Simples
```bash
export S3_ROLES_URI="s3://cost-reports/roles.json"
```

### Com Subdiretórios
```bash
export S3_ROLES_URI="s3://company-configs/cost-reporter/prod/roles.json"
```

### Por Ambiente
```bash
# Produção
export S3_ROLES_URI="s3://configs/prod/roles.json"

# Desenvolvimento  
export S3_ROLES_URI="s3://configs/dev/roles.json"
```

## 🔍 Troubleshooting

### Erro: "S3_ROLES_URI não definida"
```bash
# Verificar se a variável está definida
echo $S3_ROLES_URI

# Definir a variável
export S3_ROLES_URI="s3://seu-bucket/roles.json"
```

### Erro: "Access Denied"
- Verificar permissões IAM da EC2/Role
- Confirmar se o bucket e objeto existem
- Verificar se a região está correta

### Erro: "Bucket não encontrado"
```bash
# Listar buckets
aws s3 ls

# Verificar se o arquivo existe
aws s3 ls s3://seu-bucket/roles.json
```

## 🔄 Migração da v1 para v2

### 1. Backup do arquivo atual
```bash
cp /home/ubuntu/script_cost/roles.json ~/backup_roles.json
```

### 2. Upload para S3
```bash
aws s3 cp ~/backup_roles.json s3://seu-bucket/roles.json
```

### 3. Atualizar scripts
- Baixar a versão v2
- Configurar S3_ROLES_URI
- Testar execução

### 4. Remover arquivo local (opcional)
```bash
rm /home/ubuntu/script_cost/roles.json
```

## ✅ Vantagens da Nova Abordagem

- **Segurança**: Dados não ficam expostos na EC2
- **Controle de Acesso**: IAM policies granulares
- **Versionamento**: S3 versioning automático
- **Backup**: Replicação cross-region
- **Auditoria**: CloudTrail logs de acesso
- **Flexibilidade**: Múltiplos ambientes/configurações

## 📝 Logs e Monitoramento

### CloudTrail Events
- `s3:GetObject` - Acesso ao roles.json
- `sts:AssumeRole` - Assume roles das contas

### CloudWatch Metrics
- S3 request metrics
- Lambda execution metrics (se aplicável)

## 🔧 Automação

### Script de Deploy
```bash
#!/bin/bash
BUCKET="meu-bucket-cost-reporter"
REGION="us-east-1"

# Criar bucket se não existir
aws s3 mb s3://$BUCKET --region $REGION 2>/dev/null || true

# Upload roles.json
aws s3 cp roles.json s3://$BUCKET/roles.json

# Configurar variável
echo "export S3_ROLES_URI=\"s3://$BUCKET/roles.json\"" >> ~/.bashrc

echo "✅ Configuração S3 concluída!"
```

## 📞 Suporte

Para dúvidas sobre a configuração S3, abra uma issue no GitHub.
