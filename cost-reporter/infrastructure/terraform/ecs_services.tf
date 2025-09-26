# ECS Services using existing infrastructure

# API Service
resource "aws_ecs_service" "api_service" {
  name            = "${local.project_name}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api_service.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = local.final_private_subnet_ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_service.arn
    container_name   = "api-service"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.https]

  tags = local.common_tags
}

# Auto Scaling for API Service
resource "aws_appautoscaling_target" "api_service" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_service_cpu" {
  name               = "${local.project_name}-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api_service.resource_id
  scalable_dimension = aws_appautoscaling_target.api_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api_service.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# EventBridge Rule for Data Collector (runs daily)
resource "aws_cloudwatch_event_rule" "data_collector_schedule" {
  name                = "${local.project_name}-data-collector-schedule"
  description         = "Trigger data collector daily"
  schedule_expression = "cron(0 6 * * ? *)"  # 6 AM UTC daily

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "data_collector" {
  rule      = aws_cloudwatch_event_rule.data_collector_schedule.name
  target_id = "DataCollectorTarget"
  arn       = aws_ecs_cluster.main.arn
  role_arn  = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.data_collector.arn
    launch_type         = "FARGATE"

    network_configuration {
      security_groups  = [aws_security_group.ecs.id]
      subnets          = local.final_private_subnet_ids
      assign_public_ip = false
    }
  }
}

# EventBridge Rule for Report Generator (runs weekly)
resource "aws_cloudwatch_event_rule" "report_generator_schedule" {
  name                = "${local.project_name}-report-generator-schedule"
  description         = "Trigger report generator weekly"
  schedule_expression = "cron(0 8 ? * MON *)"  # 8 AM UTC every Monday

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "report_generator" {
  rule      = aws_cloudwatch_event_rule.report_generator_schedule.name
  target_id = "ReportGeneratorTarget"
  arn       = aws_ecs_cluster.main.arn
  role_arn  = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.report_generator.arn
    launch_type         = "FARGATE"

    network_configuration {
      security_groups  = [aws_security_group.ecs.id]
      subnets          = local.final_private_subnet_ids
      assign_public_ip = false
    }
  }
}

# IAM Role for EventBridge to run ECS tasks
resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "${local.project_name}-eventbridge-ecs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "${local.project_name}-eventbridge-ecs-policy"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = [
          aws_ecs_task_definition.data_collector.arn,
          aws_ecs_task_definition.report_generator.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      }
    ]
  })
}
