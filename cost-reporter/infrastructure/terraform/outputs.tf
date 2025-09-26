output "existing_vpc_id" {
  description = "ID of the existing VPC being used"
  value       = local.vpc_id
}

output "existing_vpc_cidr" {
  description = "CIDR of the existing VPC"
  value       = local.vpc_cidr
}

output "private_subnet_ids" {
  description = "IDs of the private subnets (existing + additional)"
  value       = local.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs of the public subnets (existing + additional)"
  value       = local.public_subnet_ids
}

output "existing_rds_endpoint" {
  description = "Endpoint of the existing RDS instance"
  value       = "glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com"
}

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "domain_name" {
  description = "Domain name for the application"
  value       = var.domain_name
}

output "ecr_repositories" {
  description = "ECR repository URLs"
  value = {
    data_collector = aws_ecr_repository.data_collector.repository_url
    api_service   = aws_ecr_repository.api_service.repository_url
  }
}

output "secrets_manager_secret_arn" {
  description = "ARN of the Secrets Manager secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    for k, v in aws_cloudwatch_log_group.ecs : k => v.name
  }
}

output "existing_lambda_function" {
  description = "Existing Lambda function that will coexist"
  value       = "chatbot-auth (preserved)"
}

output "integration_notes" {
  description = "Important notes about the integration"
  value = {
    vpc_shared = "Using existing VPC ${local.vpc_id} (workflow VPC)"
    rds_shared = "Using existing RDS glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com"
    lambda_preserved = "Existing Lambda functions are preserved"
    security_groups = "New security groups created with rules to communicate with existing resources"
    database_type = "MySQL instead of DynamoDB"
  }
}
