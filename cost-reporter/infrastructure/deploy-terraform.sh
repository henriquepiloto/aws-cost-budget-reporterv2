#!/bin/bash

# Terraform deployment script for Cost Reporter ECS infrastructure
# Usage: ./deploy-terraform.sh [plan|apply|destroy]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"
ACTION=${1:-plan}

echo "🏗️  Cost Reporter ECS Infrastructure Deployment"
echo "=============================================="
echo "Action: $ACTION"
echo "Directory: $TERRAFORM_DIR"
echo ""

cd "$TERRAFORM_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  terraform.tfvars not found. Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "📝 Please edit terraform.tfvars with your specific values"
    echo "   Especially update:"
    echo "   - domain_name"
    echo "   - rds_instance_endpoint"
    echo "   - container resources if needed"
    echo ""
    read -p "Press Enter to continue after editing terraform.tfvars..."
fi

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

case $ACTION in
    plan)
        echo "📋 Creating Terraform plan..."
        terraform plan -out=tfplan
        echo ""
        echo "📊 Plan created successfully!"
        echo "   Review the plan above and run './deploy-terraform.sh apply' to deploy"
        ;;
    
    apply)
        echo "🚀 Applying Terraform configuration..."
        if [ -f "tfplan" ]; then
            terraform apply tfplan
            rm -f tfplan
        else
            terraform apply
        fi
        echo ""
        echo "✅ Infrastructure deployed successfully!"
        echo ""
        echo "📊 Outputs:"
        terraform output
        echo ""
        echo "🎯 Next steps:"
        echo "1. Build and push Docker images to ECR"
        echo "2. Update ECS services to use new images"
        echo "3. Configure DNS (if not using Route53)"
        echo "4. Test the endpoints"
        ;;
    
    destroy)
        echo "🗑️  Destroying Terraform infrastructure..."
        echo "⚠️  This will destroy ALL resources!"
        read -p "Are you sure? Type 'yes' to continue: " confirm
        if [ "$confirm" = "yes" ]; then
            terraform destroy
            echo "✅ Infrastructure destroyed successfully!"
        else
            echo "❌ Destruction cancelled"
        fi
        ;;
    
    output)
        echo "📊 Terraform outputs:"
        terraform output
        ;;
    
    *)
        echo "❌ Invalid action. Use: plan, apply, destroy, or output"
        exit 1
        ;;
esac

echo ""
echo "🎉 Terraform deployment script completed!"
