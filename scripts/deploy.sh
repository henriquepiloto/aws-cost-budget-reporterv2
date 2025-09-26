#!/bin/bash

# Prisma Cost Intelligence Platform - Deploy Script
# Deploys complete MVP to AWS using Terraform

set -e

echo "🚀 Iniciando deploy da Plataforma Prisma Cost Intelligence..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="prisma-cost-intelligence"
DOMAIN_NAME="prisma.selectsolucoes.com"
AWS_REGION="us-east-1"
ENVIRONMENT="prod"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Verificando pré-requisitos..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI não encontrado. Instale: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform não encontrado. Instale: https://terraform.io/downloads"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js não encontrado. Instale: https://nodejs.org/"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não encontrado."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "Credenciais AWS não configuradas. Execute: aws configure"
        exit 1
    fi
    
    print_success "Todos os pré-requisitos atendidos!"
}

# Build backend Lambda package
build_backend() {
    print_status "Construindo backend Lambda..."
    
    cd backend
    
    # Create deployment package
    rm -rf dist
    mkdir -p dist
    
    # Copy Python files
    cp main.py dist/
    
    # Install dependencies
    pip3 install -r requirements.txt -t dist/
    
    # Create ZIP package
    cd dist
    zip -r ../api.zip .
    cd ..
    
    # Move to terraform directory
    mv api.zip ../terraform/
    
    cd ..
    
    print_success "Backend construído com sucesso!"
}

# Build frontend
build_frontend() {
    print_status "Construindo frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    
    # Build for production
    npm run build
    
    cd ..
    
    print_success "Frontend construído com sucesso!"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status "Implantando infraestrutura AWS..."
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan \
        -var="aws_region=${AWS_REGION}" \
        -var="environment=${ENVIRONMENT}" \
        -var="project_name=${PROJECT_NAME}" \
        -var="domain_name=${DOMAIN_NAME}" \
        -out=tfplan
    
    # Apply deployment
    print_status "Aplicando mudanças na infraestrutura..."
    terraform apply tfplan
    
    # Get outputs
    S3_BUCKET=$(terraform output -raw s3_bucket_name)
    CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
    API_URL=$(terraform output -raw api_url)
    WEBSITE_URL=$(terraform output -raw website_url)
    
    cd ..
    
    print_success "Infraestrutura implantada com sucesso!"
    print_status "S3 Bucket: ${S3_BUCKET}"
    print_status "CloudFront ID: ${CLOUDFRONT_ID}"
    print_status "API URL: ${API_URL}"
    print_status "Website URL: ${WEBSITE_URL}"
}

# Deploy frontend to S3
deploy_frontend() {
    print_status "Fazendo deploy do frontend para S3..."
    
    cd frontend
    
    # Sync to S3
    aws s3 sync out/ s3://${S3_BUCKET} --delete
    
    # Invalidate CloudFront cache
    print_status "Invalidando cache do CloudFront..."
    aws cloudfront create-invalidation \
        --distribution-id ${CLOUDFRONT_ID} \
        --paths "/*"
    
    cd ..
    
    print_success "Frontend implantado com sucesso!"
}

# Setup database schema
setup_database() {
    print_status "Configurando schema do banco de dados..."
    
    # Check if database is accessible
    python3 -c "
import pymysql
import json
import boto3

try:
    # Get database credentials
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='glpidatabaseadmin')
    secret = json.loads(response['SecretString'])
    
    # Test connection
    conn = pymysql.connect(
        host=secret['host'],
        user=secret['username'],
        password=secret['password'],
        database='aws_costs',
        port=secret.get('port', 3306)
    )
    
    print('✓ Conexão com banco de dados estabelecida')
    conn.close()
    
except Exception as e:
    print(f'✗ Erro na conexão com banco: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Banco de dados acessível!"
    else
        print_error "Falha na conexão com banco de dados"
        exit 1
    fi
}

# Test deployment
test_deployment() {
    print_status "Testando deployment..."
    
    # Test API health
    print_status "Testando API..."
    if curl -f -s "${API_URL}/health" > /dev/null; then
        print_success "API respondendo corretamente!"
    else
        print_warning "API pode não estar respondendo ainda (pode levar alguns minutos)"
    fi
    
    # Test website
    print_status "Testando website..."
    if curl -f -s "${WEBSITE_URL}" > /dev/null; then
        print_success "Website acessível!"
    else
        print_warning "Website pode não estar acessível ainda (propagação DNS)"
    fi
}

# Create admin user
create_admin_user() {
    print_status "Configurando usuário administrador..."
    
    # This would typically create an admin user in Cognito
    # For MVP, we'll just output the Cognito details
    cd terraform
    
    USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
    CLIENT_ID=$(terraform output -raw cognito_client_id)
    
    print_status "Cognito User Pool ID: ${USER_POOL_ID}"
    print_status "Cognito Client ID: ${CLIENT_ID}"
    
    print_warning "Configure o primeiro usuário admin através do console AWS Cognito"
    
    cd ..
}

# Generate deployment report
generate_report() {
    print_status "Gerando relatório de deployment..."
    
    cat > deployment_report.md << EOF
# Prisma Cost Intelligence Platform - Deployment Report

## 🚀 Deployment Successful!

**Data:** $(date)
**Ambiente:** ${ENVIRONMENT}
**Região:** ${AWS_REGION}

## 📊 URLs de Acesso

- **Website Principal:** ${WEBSITE_URL}
- **API Endpoint:** ${API_URL}
- **Painel Admin:** ${WEBSITE_URL}/admin

## 🔧 Recursos Criados

- **S3 Bucket:** ${S3_BUCKET}
- **CloudFront Distribution:** ${CLOUDFRONT_ID}
- **Lambda Function:** ${PROJECT_NAME}-api
- **API Gateway:** ${PROJECT_NAME}-api
- **Cognito User Pool:** ${USER_POOL_ID}

## 🤖 Cloudinho Assistant

O assistente Cloudinho está configurado e pronto para uso!
- Acesse o chat através do ícone no canto inferior direito
- Faça perguntas sobre custos AWS em linguagem natural
- Personalize através do painel administrativo

## 🎨 Personalização

1. Acesse: ${WEBSITE_URL}/admin
2. Configure cores, logo e branding
3. Personalize o avatar do Cloudinho
4. Salve as configurações

## 🔐 Próximos Passos

1. **Configurar DNS:** Aponte ${DOMAIN_NAME} para o CloudFront
2. **Criar Admin:** Configure usuário admin no Cognito
3. **Testar Funcionalidades:** Verifique chat e dashboards
4. **Configurar Monitoramento:** CloudWatch e alertas

## 💰 Custos Estimados

- **Mensal:** ~\$25 (MVP)
- **Com escala:** ~\$400-700 (produção)

## 📞 Suporte

Para suporte técnico, consulte a documentação em:
${WEBSITE_URL}/docs

---
**Deployment ID:** $(date +%Y%m%d_%H%M%S)
EOF

    print_success "Relatório gerado: deployment_report.md"
}

# Main deployment flow
main() {
    echo "🎯 Prisma Cost Intelligence Platform"
    echo "🏢 Select Soluções"
    echo "🌐 Domain: ${DOMAIN_NAME}"
    echo ""
    
    check_prerequisites
    
    print_status "Iniciando processo de deployment..."
    
    # Build components
    build_backend
    build_frontend
    
    # Deploy to AWS
    deploy_infrastructure
    deploy_frontend
    
    # Setup and test
    setup_database
    test_deployment
    create_admin_user
    
    # Generate report
    generate_report
    
    echo ""
    print_success "🎉 Deployment concluído com sucesso!"
    echo ""
    echo "📊 Acesse sua plataforma em: ${WEBSITE_URL}"
    echo "🤖 Chat com Cloudinho disponível!"
    echo "⚙️  Painel admin em: ${WEBSITE_URL}/admin"
    echo ""
    echo "📋 Consulte o deployment_report.md para detalhes completos"
}

# Handle script interruption
trap 'print_error "Deployment interrompido pelo usuário"; exit 1' INT

# Run main function
main "$@"
