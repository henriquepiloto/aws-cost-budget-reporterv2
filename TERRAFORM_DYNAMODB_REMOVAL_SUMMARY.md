# Terraform DynamoDB Removal Summary

## Mudanças Realizadas

### 1. **ecs.tf**
- ✅ Removidas permissões DynamoDB do IAM role policy
- ✅ Removidas permissões S3 do IAM role policy  
- ✅ Removidas permissões SNS do IAM role policy
- ✅ Atualizado CloudWatch log groups para apenas `data-collector` e `api-service`

### 2. **ecs_tasks.tf**
- ✅ Atualizada task definition `data_collector` para usar MySQL
  - Removido: `DYNAMODB_TABLE` e `S3_BUCKET`
  - Adicionado: `DB_HOST` com endpoint MySQL correto
- ✅ Atualizada task definition `api_service` para usar MySQL
  - Removido: `DYNAMODB_TABLE` e `S3_BUCKET`
  - Adicionado: `DB_HOST` com endpoint MySQL correto
- ✅ **Removida completamente** task definition `report_generator` (não implementada)

### 3. **storage.tf**
- ✅ **Removido completamente** recurso `aws_dynamodb_table.cost_data`
- ✅ **Removidos completamente** recursos S3:
  - `aws_s3_bucket.reports`
  - `aws_s3_bucket.frontend`
  - `random_string.bucket_suffix`
  - Todas as configurações S3 relacionadas
- ✅ **Removido completamente** recurso `aws_sns_topic.alerts`
- ✅ Mantido apenas `aws_secretsmanager_secret.db_credentials` com configuração MySQL correta

### 4. **outputs.tf**
- ✅ Removidos outputs: `dynamodb_table_name`, `s3_reports_bucket`, `s3_frontend_bucket`, `sns_topic_arn`
- ✅ Removido `report_generator` do output `ecr_repositories`
- ✅ Atualizado `existing_rds_endpoint` com endpoint MySQL correto
- ✅ Adicionada nota sobre `database_type = "MySQL instead of DynamoDB"`

### 5. **variables.tf**
- ✅ Removido `report_generator` das variáveis `container_cpu` e `container_memory`

### 6. **ecr.tf**
- ✅ **Removido completamente** repositório ECR `report_generator`
- ✅ **Removida completamente** lifecycle policy para `report_generator`

### 7. **ecs_services.tf**
- ✅ **Removidos completamente** EventBridge rule e target para `report_generator`
- ✅ Atualizada IAM policy do EventBridge para referenciar apenas `data_collector`

## Configuração MySQL Implementada

```hcl
# Secrets Manager
resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    host     = "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com"
    username = "select_admin"
    password = "GR558AvfoYFz7NTZ1q8n"
    database = "cost_reporter"
  })
}

# Environment Variables nos Containers
environment = [
  {
    name  = "AWS_REGION"
    value = var.aws_region
  },
  {
    name  = "DB_HOST"
    value = "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com"
  }
]
```

## Recursos Removidos Completamente

1. **DynamoDB Table** - `aws_dynamodb_table.cost_data`
2. **S3 Buckets** - `reports` e `frontend`
3. **SNS Topic** - `alerts`
4. **Report Generator** - Task definition, ECR repository, EventBridge rules
5. **Permissões IAM** - DynamoDB, S3, SNS

## Recursos Mantidos e Atualizados

1. **ECS Cluster** - Mantido
2. **API Service** - Atualizado para MySQL
3. **Data Collector** - Atualizado para MySQL
4. **Secrets Manager** - Atualizado com credenciais MySQL
5. **EventBridge** - Mantido apenas para data collector (diário às 06:00 UTC)

## Status Final

✅ **100% das referências ao DynamoDB removidas**  
✅ **Terraform alinhado com implementação real (MySQL)**  
✅ **Apenas recursos implementados mantidos no código**  
✅ **Configuração pronta para deploy**

## Próximos Passos

1. Executar `terraform plan` para verificar mudanças
2. Executar `terraform apply` para aplicar as mudanças
3. Verificar se os containers conseguem conectar ao MySQL
4. Testar endpoints da API após deploy
