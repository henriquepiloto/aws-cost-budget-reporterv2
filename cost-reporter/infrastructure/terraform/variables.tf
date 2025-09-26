variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "container_cpu" {
  description = "CPU units for containers"
  type        = map(number)
  default = {
    data_collector    = 256
    api_service      = 512
    report_generator = 1024
  }
}

variable "container_memory" {
  description = "Memory for containers"
  type        = map(number)
  default = {
    data_collector    = 512
    api_service      = 1024
    report_generator = 2048
  }
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "costs.selectsolucoes.com"
}

# Remove VPC and RDS variables since we use existing ones
# The existing resources are discovered via data sources
