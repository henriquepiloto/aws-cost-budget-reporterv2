#!/bin/bash

# Integrated deployment script for AWS Cost Budget Reporter v2
# Usage: ./deploy.sh [prisma-admin|cost-reporter|all] [frontend|backend|all]

set -e

PROJECT=${1:-all}
COMPONENT=${2:-all}

echo "🚀 AWS Cost Budget Reporter v2 - Deployment"
echo "Project: $PROJECT | Component: $COMPONENT"
echo "=========================================="

deploy_prisma_admin() {
    echo "🔐 Deploying Prisma Admin..."
    cd prisma-admin/
    
    if [[ $COMPONENT == "all" || $COMPONENT == "backend" ]]; then
        echo "📦 Deploying Prisma Admin backend..."
        ./infrastructure/deploy.sh backend
    fi
    
    if [[ $COMPONENT == "all" || $COMPONENT == "frontend" ]]; then
        echo "📦 Deploying Prisma Admin frontend..."
        ./infrastructure/deploy.sh frontend
    fi
    
    cd ..
    echo "✅ Prisma Admin deployed successfully!"
}

deploy_cost_reporter() {
    echo "📊 Deploying Cost Reporter..."
    echo "🚧 Cost Reporter deployment not implemented yet"
    echo "   This will be available in future versions"
}

case $PROJECT in
    prisma-admin)
        deploy_prisma_admin
        ;;
    cost-reporter)
        deploy_cost_reporter
        ;;
    all)
        deploy_prisma_admin
        deploy_cost_reporter
        ;;
    *)
        echo "❌ Invalid project. Use: prisma-admin, cost-reporter, or all"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Project Status:"
echo "- Prisma Admin: ✅ Production (https://prisma.selectsolucoes.com)"
echo "- Cost Reporter: 🚧 Development"
echo ""
echo "📚 Documentation:"
echo "- Prisma Admin: ./prisma-admin/docs/"
echo "- Cost Reporter: ./cost-reporter/docs/ (coming soon)"
