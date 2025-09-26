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
	@echo "🧪 Testing implemented endpoints..."
	@echo "Health check:" && curl -s https://costcollector.selectsolucoes.com/health | jq .
	@echo "Cost overview:" && curl -s https://costcollector.selectsolucoes.com/costs/overview | jq '.current_month'
	@echo "Chat test:" && curl -s -X POST https://costcollector.selectsolucoes.com/chat -H "Content-Type: application/json" -d '{"message": "Status dos custos"}' | jq '.response'

# Test integration endpoints
integration-test:
	@echo "🔗 Testing integration endpoints..."
	@echo "API info:" && curl -s https://costcollector.selectsolucoes.com/ | jq '.features'
	@echo "Health status:" && curl -s https://costcollector.selectsolucoes.com/health | jq '.finops_chat'

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
