# Data sources for existing infrastructure
# This ensures we use existing resources instead of creating new ones

# Existing VPC (workflow VPC used by chatbot-auth Lambda)
data "aws_vpc" "existing" {
  id = "vpc-04c0a089dd691442c"  # workflow VPC
}

# Existing subnets from the workflow VPC
data "aws_subnets" "existing_private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Type"
    values = ["private"]
  }
}

data "aws_subnets" "existing_public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
  
  filter {
    name   = "tag:Type"
    values = ["public"]
  }
}

# If no tagged subnets exist, get all subnets and use first two
data "aws_subnets" "all_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }
}

data "aws_subnet" "existing_subnets" {
  count = min(2, length(data.aws_subnets.all_subnets.ids))
  id    = data.aws_subnets.all_subnets.ids[count.index]
}

# Existing RDS instance
data "aws_db_instance" "existing" {
  db_instance_identifier = "glpi-database-instance-1"
}

# Existing security group used by Lambda
data "aws_security_group" "existing_lambda_sg" {
  id = "sg-0df74898d34cbea3d"
}

# Existing Route53 zone
data "aws_route53_zone" "existing" {
  name         = "selectsolucoes.com"
  private_zone = false
}

# Local values using existing resources
locals {
  # Use existing VPC
  vpc_id = data.aws_vpc.existing.id
  vpc_cidr = data.aws_vpc.existing.cidr_block
  
  # Use existing subnets or create new ones if needed
  private_subnet_ids = length(data.aws_subnets.existing_private.ids) > 0 ? 
    slice(data.aws_subnets.existing_private.ids, 0, min(2, length(data.aws_subnets.existing_private.ids))) :
    slice(data.aws_subnets.all_subnets.ids, 0, min(2, length(data.aws_subnets.all_subnets.ids)))
  
  public_subnet_ids = length(data.aws_subnets.existing_public.ids) > 0 ? 
    slice(data.aws_subnets.existing_public.ids, 0, min(2, length(data.aws_subnets.existing_public.ids))) :
    slice(data.aws_subnets.all_subnets.ids, 0, min(2, length(data.aws_subnets.all_subnets.ids)))
  
  # Use existing RDS endpoint
  rds_endpoint = data.aws_db_instance.existing.endpoint
}
