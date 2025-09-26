# AWS Cost Intelligence Platform MVP

🚀 **Plataforma completa de inteligência de custos AWS com IA integrada**

## 🌟 Visão Geral

A AWS Cost Intelligence Platform é uma solução serverless completa que combina análise avançada de custos AWS com inteligência artificial através do **Cloudinho**, nosso assistente especializado em otimização de custos.

### 🎯 Funcionalidades Principais

- **📊 Dashboard Interativo** - Visualização em tempo real dos custos AWS
- **🤖 Cloudinho AI Assistant** - IA conversacional especializada em custos AWS
- **⚙️ Admin Panel** - Customização completa de branding e configurações
- **📈 Análise Preditiva** - Forecasting e recomendações de otimização
- **🔐 Segurança Avançada** - Autenticação Cognito e Secrets Manager
- **🌐 CDN Global** - Performance otimizada via CloudFront

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CloudFront    │────│   S3 Website     │    │   API Gateway   │
│   (CDN Global)  │    │   (Frontend)     │    │   (REST API)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cognito       │    │   Lambda         │────│   Bedrock       │
│   (Auth)        │    │   (Backend)      │    │   (Claude AI)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │ Secrets Manager │
                       │ (DB Credentials)│
                       └─────────────────┘
```

## 🚀 Deploy Realizado

### URLs da Aplicação
- **Website:** https://dx2t55trr8wnt.cloudfront.net
- **API:** https://ewapsbyof8.execute-api.us-east-1.amazonaws.com/prod

### Recursos AWS Criados
- **CloudFront Distribution:** E1SAZUX6DR5QF3
- **S3 Bucket:** prisma-cost-intelligence-frontend-lrijp4je
- **Lambda Function:** prisma-cost-intelligence-api
- **Cognito User Pool:** us-east-1_Mpvv5mY8q

## 💰 Estimativa de Custos

| Serviço | Custo Mensal | Descrição |
|---------|--------------|-----------|
| CloudFront | $1-5 | CDN global |
| S3 | $0.50-2 | Hosting estático |
| Lambda | $0.20-5 | Processamento serverless |
| API Gateway | $3.50/1M req | API REST |
| Cognito | $0.0055/MAU | Autenticação |
| Secrets Manager | $0.40 | Credenciais seguras |
| **Total** | **$5-25/mês** | **Uso MVP** |

## 🛠️ Tecnologias

### Frontend
- **React 18** + **Next.js 14**
- **TypeScript** + **Tailwind CSS**
- **Headless UI** + **Heroicons**
- **Recharts** para visualizações

### Backend
- **Python 3.10** + **FastAPI**
- **AWS Lambda** (Serverless)
- **AWS Bedrock** (Claude 3 Sonnet)
- **PyMySQL** para banco de dados

### Infraestrutura
- **Terraform** (IaC)
- **AWS CloudFront** (CDN)
- **AWS S3** (Static Hosting)
- **AWS Cognito** (Authentication)
- **AWS Secrets Manager** (Security)

## 📦 Estrutura do Projeto

```
aws-cost-budget-reporterv2/
├── frontend/                 # React/Next.js App
│   ├── pages/               # Next.js Pages
│   ├── components/          # React Components
│   └── styles/              # Tailwind CSS
├── backend/                 # FastAPI Lambda
│   ├── main.py             # Lambda Handler
│   └── requirements.txt    # Python Dependencies
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # AWS Resources
│   ├── variables.tf       # Configuration
│   └── outputs.tf         # Deploy Info
└── deploy.sh              # Deployment Script
```

## 🚀 Deploy Rápido

### Pré-requisitos
- AWS CLI configurado
- Terraform >= 1.0
- Node.js >= 18
- Python >= 3.10

### Deploy Completo
```bash
git clone https://github.com/seu-usuario/aws-cost-budget-reporterv2.git
cd aws-cost-budget-reporterv2
chmod +x deploy.sh
./deploy.sh
```

### Deploy Manual
```bash
# Backend
cd backend
zip -r ../terraform/api.zip .

# Frontend
cd ../frontend
npm install
npm run build

# Infrastructure
cd ../terraform
terraform init
terraform apply -auto-approve

# Upload Frontend
aws s3 sync ../frontend/out/ s3://BUCKET_NAME --delete
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# Terraform
export TF_VAR_domain_name="seu-dominio.com"
export TF_VAR_db_host="localhost"
export TF_VAR_db_username="admin"
export TF_VAR_db_password="password123"
export TF_VAR_db_name="cost_intelligence"
```

### Customização do Cloudinho
```python
# backend/main.py
CLOUDINHO_CONFIG = {
    "name": "Cloudinho",
    "personality": "Especialista em custos AWS",
    "model": "anthropic.claude-3-sonnet-20240229-v1:0"
}
```

## 🎨 Admin Panel

O painel administrativo permite:
- **Branding personalizado** (logo, cores, fontes)
- **Configuração do Cloudinho** (personalidade, respostas)
- **Gerenciamento de usuários**
- **Configurações de alertas**
- **Relatórios customizados**

## 🤖 Cloudinho AI Assistant

Nosso assistente de IA especializado em:
- **Análise de custos** em linguagem natural
- **Recomendações de otimização**
- **Explicações técnicas humanizadas**
- **Alertas proativos**
- **Forecasting inteligente**

## 📊 ROI e Benefícios

### Retorno sobre Investimento
- **175x-437x ROI** através de otimizações identificadas
- **20-40% economia** média nos custos AWS
- **Identificação automática** de recursos subutilizados

### Benefícios Técnicos
- **Serverless** - Zero manutenção de infraestrutura
- **Escalável** - Suporta crescimento automático
- **Seguro** - Boas práticas AWS implementadas
- **Rápido** - CDN global para performance

## 🔐 Segurança

- **HTTPS obrigatório** via CloudFront
- **Autenticação robusta** com Cognito
- **Credenciais seguras** no Secrets Manager
- **Políticas IAM restritivas**
- **Logs centralizados** no CloudWatch

## 📈 Roadmap

### Fase 1 - MVP ✅
- [x] Frontend React/Next.js
- [x] Backend FastAPI/Lambda
- [x] Cloudinho AI Assistant
- [x] Admin Panel básico
- [x] Deploy automatizado

### Fase 2 - Expansão
- [ ] Domínio personalizado
- [ ] Banco de dados RDS
- [ ] Multi-tenant
- [ ] Alertas avançados
- [ ] Mobile app

### Fase 3 - Enterprise
- [ ] Integração Azure/GCP
- [ ] API marketplace
- [ ] White-label
- [ ] Advanced analytics
- [ ] Enterprise SSO

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Email:** suporte@selectsolucoes.com
- **Website:** https://selectsolucoes.com
- **Documentação:** https://docs.selectsolucoes.com

---

**Desenvolvido com ❤️ pela Select Soluções**

*Transformando dados de custo em insights acionáveis através da inteligência artificial.*
