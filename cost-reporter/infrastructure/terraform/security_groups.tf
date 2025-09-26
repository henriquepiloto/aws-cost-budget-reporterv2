# Security Groups for ECS using existing VPC

# ALB Security Group
resource "aws_security_group" "alb" {
  name_prefix = "${local.project_name}-alb-"
  vpc_id      = local.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-alb-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ECS Security Group
resource "aws_security_group" "ecs" {
  name_prefix = "${local.project_name}-ecs-"
  vpc_id      = local.vpc_id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description     = "API from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow communication with existing Lambda security group
  ingress {
    description     = "Communication with existing Lambda"
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [data.aws_security_group.existing_lambda_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ecs-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Add rule to existing Lambda security group to allow ECS communication
resource "aws_security_group_rule" "lambda_to_ecs" {
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs.id
  security_group_id        = data.aws_security_group.existing_lambda_sg.id
  description              = "Allow ECS to communicate with Lambda"
}

# RDS Security Group rule (add to existing RDS security group if needed)
resource "aws_security_group_rule" "rds_from_ecs" {
  type                     = "ingress"
  from_port                = 3306
  to_port                  = 3306
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs.id
  security_group_id        = data.aws_db_instance.existing.vpc_security_groups[0]
  description              = "Allow ECS to access RDS"
}
