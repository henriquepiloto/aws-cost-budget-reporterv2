# AWS Configuration
aws_region = "us-east-1"
environment = "prod"

# Container Configuration
container_cpu = {
  data_collector    = 256
  api_service      = 512
  report_generator = 1024
}

container_memory = {
  data_collector    = 512
  api_service      = 1024
  report_generator = 2048
}

# Domain Configuration
domain_name = "costcollector.selectsolucoes.com"

# Note: VPC and RDS configurations are automatically discovered from existing resources
# - VPC: vpc-04c0a089dd691442c (workflow VPC)
# - RDS: glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com
# - Route53: selectsolucoes.com zone
