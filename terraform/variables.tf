# Variables for Prisma Cost Intelligence Platform

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "prisma-cost-intelligence"
}

variable "project_owner" {
  description = "Project owner tag"
  type        = string
  default     = "Select Soluções"
}

variable "domain_name" {
  description = "Custom domain name"
  type        = string
  default     = "prisma.selectsolucoes.com"
}

variable "api_domain_name" {
  description = "API domain name"
  type        = string
  default     = "api.prisma.selectsolucoes.com"
}

# Customization variables for admin panel
variable "default_brand_config" {
  description = "Default branding configuration"
  type = object({
    company_name    = string
    logo_url       = string
    primary_color  = string
    secondary_color = string
    accent_color   = string
    font_family    = string
  })
  default = {
    company_name    = "Select Soluções"
    logo_url       = "https://prisma.selectsolucoes.com/assets/logo.png"
    primary_color  = "#1f2937"
    secondary_color = "#3b82f6"
    accent_color   = "#10b981"
    font_family    = "Inter, sans-serif"
  }
}

variable "cloudinho_config" {
  description = "Cloudinho AI assistant configuration"
  type = object({
    name           = string
    personality    = string
    greeting       = string
    avatar_url     = string
    response_style = string
  })
  default = {
    name           = "Cloudinho"
    personality    = "Sou o Cloudinho, seu assistente especialista em custos AWS! 😊 Estou aqui para ajudar você a entender e otimizar seus gastos na nuvem de forma simples e humanizada."
    greeting       = "Olá! Eu sou o Cloudinho 👋 Como posso ajudar você hoje com seus custos AWS?"
    avatar_url     = "https://prisma.selectsolucoes.com/assets/cloudinho-avatar.png"
    response_style = "friendly_professional"
  }
}

variable "database_config" {
  description = "Database configuration"
  type = object({
    secret_name = string
    region     = string
  })
  default = {
    secret_name = "glpidatabaseadmin"
    region     = "us-east-1"
  }
}

variable "s3_roles_config" {
  description = "S3 roles configuration"
  type = object({
    bucket_name = string
    object_key  = string
  })
  default = {
    bucket_name = "select-aws-configs"
    object_key  = "roles.json"
  }
}

variable "bedrock_config" {
  description = "Bedrock model configuration"
  type = object({
    model_id           = string
    max_tokens         = number
    temperature        = number
    top_p             = number
  })
  default = {
    model_id           = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens         = 4000
    temperature        = 0.7
    top_p             = 0.9
  }
}

variable "admin_users" {
  description = "List of admin users for the platform"
  type = list(object({
    email      = string
    first_name = string
    last_name  = string
    role       = string
  }))
  default = [
    {
      email      = "admin@selectsolucoes.com"
      first_name = "Admin"
      last_name  = "Select"
      role       = "super_admin"
    }
  ]
}

variable "feature_flags" {
  description = "Feature flags for the platform"
  type = object({
    enable_multi_tenant    = bool
    enable_custom_branding = bool
    enable_api_rate_limit  = bool
    enable_audit_logs      = bool
    enable_cost_alerts     = bool
    enable_forecasting     = bool
  })
  default = {
    enable_multi_tenant    = true
    enable_custom_branding = true
    enable_api_rate_limit  = true
    enable_audit_logs      = true
    enable_cost_alerts     = true
    enable_forecasting     = true
  }
}

# Database connection variables
variable "db_host" {
  description = "Database host"
  type        = string
  default     = "localhost"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "password123"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "cost_intelligence"
}
