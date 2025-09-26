# 📊 AWS Cost Budget Reporter v2 + Prisma Admin

Repositório integrado contendo duas soluções AWS complementares:

## 🏗️ **Projetos Incluídos**

### 📊 **1. AWS Cost Budget Reporter**
Sistema de relatórios e monitoramento de custos AWS.

**Status:** 🚧 Em desenvolvimento  
**Localização:** `/cost-reporter/`

### 🔐 **2. Prisma Admin - Painel Administrativo Cloudinho**
Sistema completo de administração para chatbot IA com interface web, autenticação, gerenciamento de usuários e customização visual.

**Status:** ✅ Produção  
**URL:** https://prisma.selectsolucoes.com  
**Localização:** `/prisma-admin/`

## 🌐 **Acesso aos Sistemas**

### Prisma Admin
- **URL:** https://prisma.selectsolucoes.com
- **Credenciais Admin:** `admin` / `admin123`
- **Funcionalidades:**
  - 🔐 Sistema de autenticação completo
  - 💬 Chat com IA (Amazon Bedrock)
  - 👥 Gerenciamento de usuários
  - 🎨 Customização visual completa
  - ⚙️ Configurações do sistema

### Cost Reporter
- **Status:** Em desenvolvimento
- **Funcionalidades planejadas:**
  - 📊 Relatórios de custos AWS
  - 📈 Análise de tendências
  - 🚨 Alertas de orçamento
  - 📧 Notificações automáticas

## 📁 **Estrutura do Repositório**

```
aws-cost-budget-reporterv2/
├── 📂 prisma-admin/           # Painel Admin Cloudinho
│   ├── 📂 frontend/           # Interface web (HTML/CSS/JS)
│   ├── 📂 backend/            # Lambda functions (Python)
│   ├── 📂 docs/               # Documentação completa
│   └── 📂 infrastructure/     # Scripts de deploy
├── 📂 cost-reporter/          # Sistema de custos AWS
│   ├── 📂 frontend/           # Dashboard de custos
│   ├── 📂 backend/            # APIs de relatórios
│   ├── 📂 docs/               # Documentação
│   └── 📂 infrastructure/     # Terraform/CloudFormation
├── 📂 shared/                 # Recursos compartilhados
│   ├── 📂 utils/              # Utilitários comuns
│   └── 📂 configs/            # Configurações globais
└── README.md                  # Este arquivo
```

## 🚀 **Deploy e Configuração**

### Prisma Admin (Produção)
```bash
cd prisma-admin/
./infrastructure/deploy.sh all
```

### Cost Reporter (Em desenvolvimento)
```bash
cd cost-reporter/
# Scripts de deploy em desenvolvimento
```

## 📚 **Documentação Detalhada**

### Prisma Admin
- [📡 API Documentation](prisma-admin/docs/API.md)
- [🚀 Deployment Guide](prisma-admin/docs/DEPLOYMENT.md)
- [🎨 Customization Guide](prisma-admin/docs/CUSTOMIZATION.md)
- [📝 Changelog](prisma-admin/CHANGELOG.md)

### Cost Reporter
- 🚧 Documentação em desenvolvimento

## 🏗️ **Arquitetura AWS**

### Prisma Admin
- **Frontend:** S3 + CloudFront
- **Backend:** Lambda + API Gateway
- **Banco:** RDS MySQL
- **IA:** Amazon Bedrock (Claude)
- **Domínio:** prisma.selectsolucoes.com

### Cost Reporter (Planejado)
- **Frontend:** S3 + CloudFront
- **Backend:** Lambda + API Gateway
- **Dados:** Cost Explorer API + S3
- **Notificações:** SNS + SES

## 🔧 **Desenvolvimento**

### Pré-requisitos
- AWS CLI configurado
- Python 3.9+
- Node.js (para ferramentas de build)
- Acesso às contas AWS necessárias

### Configuração Local
```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/aws-cost-budget-reporterv2.git
cd aws-cost-budget-reporterv2

# Configurar Prisma Admin
cd prisma-admin/backend
pip install -r requirements.txt

# Configurar Cost Reporter (quando disponível)
cd ../cost-reporter/backend
# Instruções em desenvolvimento
```

## 🤝 **Contribuição**

### Prisma Admin
- Sistema em produção
- Melhorias e correções bem-vindas
- Seguir padrões estabelecidos

### Cost Reporter
- Sistema em desenvolvimento
- Contribuições para arquitetura inicial
- Definição de requisitos

## 📊 **Status dos Projetos**

| Projeto | Status | Versão | Última Atualização |
|---------|--------|--------|--------------------|
| Prisma Admin | ✅ Produção | v1.0.0 | 2025-09-26 |
| Cost Reporter | 🚧 Desenvolvimento | v0.1.0 | TBD |

## 🎯 **Roadmap**

### Prisma Admin v1.1.0
- [ ] Histórico de conversas persistente
- [ ] Dashboard com analytics
- [ ] Tema escuro/claro
- [ ] Múltiplos idiomas

### Cost Reporter v1.0.0
- [ ] Definir arquitetura base
- [ ] Implementar coleta de dados
- [ ] Criar dashboard inicial
- [ ] Sistema de alertas

## 📞 **Suporte**

- **Email:** suporte@selectsolucoes.com
- **Issues:** GitHub Issues
- **Documentação:** Ver pastas `/docs` de cada projeto

## 📄 **Licença**

Projeto proprietário - Select Soluções  
© 2025 Todos os direitos reservados

---

**Desenvolvido com ❤️ pela equipe Select Soluções**
