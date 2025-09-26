# This file replaces vpc.tf to use existing infrastructure
# We don't create new VPC/subnets, we use existing ones

# Create additional subnets only if needed
resource "aws_subnet" "additional_private" {
  count = length(local.private_subnet_ids) < 2 ? 2 - length(local.private_subnet_ids) : 0

  vpc_id            = local.vpc_id
  cidr_block        = cidrsubnet(local.vpc_cidr, 8, 20 + count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-additional-private-${count.index + 1}"
    Type = "private"
  })
}

resource "aws_subnet" "additional_public" {
  count = length(local.public_subnet_ids) < 2 ? 2 - length(local.public_subnet_ids) : 0

  vpc_id                  = local.vpc_id
  cidr_block              = cidrsubnet(local.vpc_cidr, 8, 30 + count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-additional-public-${count.index + 1}"
    Type = "public"
  })
}

# Get existing Internet Gateway
data "aws_internet_gateway" "existing" {
  filter {
    name   = "attachment.vpc-id"
    values = [local.vpc_id]
  }
}

# Create route table for additional subnets if needed
resource "aws_route_table" "additional_public" {
  count = length(aws_subnet.additional_public)

  vpc_id = local.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.existing.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-additional-public-rt"
  })
}

resource "aws_route_table_association" "additional_public" {
  count = length(aws_subnet.additional_public)

  subnet_id      = aws_subnet.additional_public[count.index].id
  route_table_id = aws_route_table.additional_public[0].id
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Final subnet lists combining existing and additional
locals {
  final_private_subnet_ids = concat(
    local.private_subnet_ids,
    aws_subnet.additional_private[*].id
  )
  
  final_public_subnet_ids = concat(
    local.public_subnet_ids,
    aws_subnet.additional_public[*].id
  )
}
