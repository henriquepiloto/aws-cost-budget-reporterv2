#!/bin/bash

set -e

echo -e "\033[0;34m[INFO]\033[0m Iniciando deploy da AWS Cost Intelligence Platform..."

# Build backend
echo -e "\033[0;34m[INFO]\033[0m Construindo backend..."
cd backend
zip -r ../terraform/api.zip . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

# Build frontend
echo -e "\033[0;34m[INFO]\033[0m Construindo frontend..."
cd frontend
npm install
npm run build
cd ..

# Deploy infrastructure
echo -e "\033[0;34m[INFO]\033[0m Fazendo deploy da infraestrutura..."
cd terraform
terraform init
terraform plan -var="domain_name=prisma.selectsolucoes.com"
terraform apply -var="domain_name=prisma.selectsolucoes.com" -auto-approve

echo -e "\033[0;32m[SUCCESS]\033[0m Deploy concluído com sucesso!"
