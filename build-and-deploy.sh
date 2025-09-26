#!/bin/bash

set -e

REGION="us-east-1"
ACCOUNT_ID="727706432228"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push data-collector
echo "Building data-collector..."
cd cost-reporter/backend/data-collector
docker build -t cost-reporter/data-collector .
docker tag cost-reporter/data-collector:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/data-collector:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/data-collector:latest

# Build and push api-service
echo "Building api-service..."
cd ../api-service
docker build -t cost-reporter/api-service .
docker tag cost-reporter/api-service:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/api-service:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/api-service:latest

# Build and push report-generator
echo "Building report-generator..."
cd ../report-generator
docker build -t cost-reporter/report-generator .
docker tag cost-reporter/report-generator:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/report-generator:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cost-reporter/report-generator:latest

echo "All images built and pushed successfully!"

# Force ECS service update
cd ../../../
echo "Updating ECS services..."
aws ecs update-service --cluster cost-reporter-cluster --service cost-reporter-api-service --force-new-deployment --region $REGION

echo "Deployment complete!"
