#!/bin/bash

set -e

echo "🚀 Starting local deployment..."

# Variables
REGION="us-east-1"
ACCOUNT_ID="727706432228"
CLUSTER="cost-reporter-cluster"

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push images
echo "📦 Building and pushing images..."

services=("data-collector" "api-service" "report-generator")

for service in "${services[@]}"; do
    echo "Building $service..."
    cd cost-reporter/backend/$service
    docker build -t cost-reporter/$service .
    docker tag cost-reporter/$service:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/$service:latest
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/$service:latest
    cd ../../..
done

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service --cluster $CLUSTER --service cost-reporter-api-service --force-new-deployment --region $REGION

echo "✅ Deployment completed!"
echo "🌐 Check status at: https://costcollector.selectsolucoes.com/health"
