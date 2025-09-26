.PHONY: deploy build test clean

# Variables
REGION := us-east-1
ACCOUNT_ID := 727706432228
CLUSTER := cost-reporter-cluster

# Deploy to AWS
deploy:
	@echo "🚀 Deploying to AWS..."
	./deploy-local.sh

# Build images locally
build:
	@echo "📦 Building Docker images..."
	@for service in data-collector api-service report-generator; do \
		echo "Building $$service..."; \
		cd cost-reporter/backend/$$service && docker build -t cost-reporter/$$service . && cd ../../..; \
	done

# Test API endpoints
test:
	@echo "🧪 Testing API endpoints..."
	@curl -s https://costcollector.selectsolucoes.com/health | jq .
	@curl -s https://costcollector.selectsolucoes.com/costs/overview | jq '.current_month'

# Test integration endpoints
integration-test:
	@echo "🔗 Testing integration endpoints..."
	@echo "Monthly costs:" && curl -s https://costcollector.selectsolucoes.com/costs/monthly | jq '.monthly_costs[0:2]'
	@echo "Budgets:" && curl -s https://costcollector.selectsolucoes.com/budgets | jq '.budgets[0]'

# Clean Docker images
clean:
	@echo "🧹 Cleaning Docker images..."
	@docker rmi -f $$(docker images "cost-reporter/*" -q) 2>/dev/null || true

# Infrastructure
infra-plan:
	@cd cost-reporter/infrastructure/terraform && terraform plan

infra-apply:
	@cd cost-reporter/infrastructure/terraform && terraform apply

# Logs
logs:
	@aws logs tail /ecs/cost-reporter/api-service --follow --region $(REGION)

# Status
status:
	@aws ecs describe-services --cluster $(CLUSTER) --services cost-reporter-api-service --region $(REGION) --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
