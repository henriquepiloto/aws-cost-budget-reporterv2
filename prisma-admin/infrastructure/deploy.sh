#!/bin/bash

# Deploy script for Prisma Admin
# Usage: ./deploy.sh [frontend|backend|all]

set -e

COMPONENT=${1:-all}
AWS_REGION="us-east-1"
S3_BUCKET="prisma-admin-selectsolucoes"
LAMBDA_FUNCTION="chatbot-auth"
CLOUDFRONT_DISTRIBUTION="E1SAZUX6DR5QF3"

echo "🚀 Starting deployment for: $COMPONENT"

deploy_frontend() {
    echo "📦 Deploying frontend..."
    
    # Sync files to S3
    aws s3 sync ../frontend/ s3://$S3_BUCKET/ \
        --delete \
        --exclude "*.md" \
        --exclude "package.json"
    
    # Invalidate CloudFront cache
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text
    
    echo "✅ Frontend deployed successfully!"
}

deploy_backend() {
    echo "📦 Deploying backend..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd $TEMP_DIR
    
    # Copy Lambda function
    cp ../backend/lambda_function.py .
    
    # Install dependencies
    pip install -r ../backend/requirements.txt -t .
    
    # Create deployment package
    zip -r lambda-package.zip .
    
    # Update Lambda function
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION \
        --zip-file fileb://lambda-package.zip \
        --region $AWS_REGION
    
    # Cleanup
    cd - > /dev/null
    rm -rf $TEMP_DIR
    
    echo "✅ Backend deployed successfully!"
}

case $COMPONENT in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    all)
        deploy_backend
        deploy_frontend
        ;;
    *)
        echo "❌ Invalid component. Use: frontend, backend, or all"
        exit 1
        ;;
esac

echo "🎉 Deployment completed!"
echo "🌐 Access: https://prisma.selectsolucoes.com"
