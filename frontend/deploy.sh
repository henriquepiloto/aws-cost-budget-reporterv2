#!/bin/bash

# Build and deploy script for Cloudinho Frontend
set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="727706432228"
ECR_REPOSITORY="cost-reporter/frontend"
IMAGE_TAG="latest"

echo "🚀 Starting Cloudinho Frontend deployment..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t cloudinho-frontend .

# Tag for ECR
echo "🏷️  Tagging image for ECR..."
docker tag cloudinho-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Push to ECR
echo "⬆️  Pushing image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
    --cluster cost-reporter-cluster \
    --service cost-reporter-frontend-service \
    --force-new-deployment \
    --region $AWS_REGION

echo "✅ Deployment completed!"
echo "🌐 Frontend will be available at: https://cloudinho.selectsolucoes.com"
echo "⏳ Please wait 2-3 minutes for the deployment to complete."
