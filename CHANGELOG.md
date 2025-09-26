# Changelog - AWS Cost Budget Reporter

## [3.0.0] - 2025-09-26

### 🎯 Complete Analytics Release

#### Added
- **Monthly costs tracking**: Last 6 months historical data
- **Current month monitoring**: Daily cost tracking with month-to-date
- **Cost forecasting**: AWS Cost Explorer forecast integration
- **Budget monitoring**: AWS Budgets API integration with usage percentages
- **Alert tracking**: Daily cost alerts count per month
- **Advanced endpoints**: `/costs/overview`, `/costs/monthly`, `/budgets`, `/alerts`
- **MySQL database**: Complete migration from DynamoDB to MySQL RDS
- **Comprehensive data collection**: Multiple AWS APIs integration

#### Changed
- **Database**: Migrated from DynamoDB to MySQL RDS for better relational data
- **API version**: Upgraded to v3.0 with complete analytics features
- **Data collector**: Enhanced with forecast, budgets, and alerts collection
- **Collection frequency**: Optimized for comprehensive monthly and daily data
- **Task count**: Reduced to 1 task for cost optimization

#### Technical Improvements
- **python-dateutil**: Added for advanced date calculations
- **Error handling**: Improved error handling for AWS API calls
- **Data structure**: Normalized database schema for analytics
- **Performance**: Optimized queries and data collection

## [2.0.0] - 2025-09-26

### 🔧 Advanced Service Breakdown

#### Added
- **Service-level breakdown**: Detailed cost analysis per AWS service
- **Usage type tracking**: Multiple usage types per service
- **Resource identification**: EC2 instances and resource-level data
- **Enhanced API endpoints**: `/costs/detailed`, `/costs/by-service`, `/costs/resources`
- **Advanced data collection**: GroupBy service and usage type

#### Changed
- **Data granularity**: From simple daily totals to detailed service breakdown
- **Collection period**: Focused on last 7 days for detailed analysis
- **API responses**: Rich data with service names, usage types, and costs

## [1.0.0] - 2025-09-26

### 🚀 Initial ECS Migration

#### Added
- **ECS Fargate architecture**: Migrated from Lambda to containerized solution
- **Docker containers**: data-collector, api-service, report-generator
- **Application Load Balancer**: SSL termination with ACM certificate
- **Domain configuration**: costcollector.selectsolucoes.com
- **EventBridge scheduling**: Daily automated data collection at 06:00 UTC
- **MySQL integration**: Connection to existing RDS instance
- **Secrets Manager**: Secure credential management
- **ECR repositories**: Container image storage
- **CloudWatch logging**: Comprehensive logging for all services

#### Infrastructure
- **Terraform IaC**: Complete infrastructure as code
- **VPC integration**: Existing VPC (vpc-04c0a089dd691442c)
- **Security groups**: ECS to RDS communication
- **Auto scaling**: ECS service auto scaling configuration
- **Health checks**: ALB health checks for high availability

#### Deployment
- **Local deployment**: deploy-local.sh script
- **Makefile**: Organized commands for development
- **Docker optimization**: Multi-stage builds
- **Cost optimization**: Single task deployment, Fargate Spot instances

---

**Migration Journey**: Lambda → ECS Basic → Service Breakdown → Complete Analytics
