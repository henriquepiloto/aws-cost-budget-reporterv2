# Storage resources using existing infrastructure

# Secrets Manager for Database Credentials (using existing RDS)
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "cost-reporter-db-credentials"
  description = "Database credentials for Cost Reporter (using existing RDS)"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    host     = "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com"
    username = "select_admin"
    password = "GR558AvfoYFz7NTZ1q8n"  # Using existing RDS password
    database = "cost_reporter"  # New database for cost reporter
  })
}
