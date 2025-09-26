# Storage resources using existing infrastructure

# DynamoDB Table for Cost Data
resource "aws_dynamodb_table" "cost_data" {
  name           = "${local.project_name}-cost-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "date"
  range_key      = "service"

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "service"
    type = "S"
  }

  attribute {
    name = "account_id"
    type = "S"
  }

  global_secondary_index {
    name     = "AccountIndex"
    hash_key = "account_id"
    range_key = "date"
  }

  tags = local.common_tags
}

# S3 Bucket for Reports
resource "aws_s3_bucket" "reports" {
  bucket = "${local.project_name}-reports-${random_string.bucket_suffix.result}"

  tags = local.common_tags
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket = aws_s3_bucket.reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket for Frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "${local.project_name}-frontend-${random_string.bucket_suffix.result}"

  tags = local.common_tags
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${local.project_name}-alerts"

  tags = local.common_tags
}

# Secrets Manager for Database Credentials (using existing RDS)
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${local.project_name}-db-credentials"
  description = "Database credentials for Cost Reporter (using existing RDS)"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    host     = local.rds_endpoint
    username = "select_admin"
    password = "GR558AvfoYFz7NTZ1q8n"  # Using existing RDS password
    database = "cost_reporter"  # New database for cost reporter
  })
}
