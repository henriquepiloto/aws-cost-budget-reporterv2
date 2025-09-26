# Guia de Instalação

## Pré-requisitos

### Sistema
- Ubuntu 20.04+
- Python 3.8+
- MySQL Client

### AWS
- AWS CLI configurado
- Perfil 'select' com permissões
- Assume role configurado para todas as contas

### Dependências Python
```bash
sudo apt update
sudo apt install python3-boto3 python3-pymysql mysql-client -y
```

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/aws-cost-budget-reporter.git
cd aws-cost-budget-reporter
```

### 2. Configure permissões
```bash
chmod +x scripts/*.sh
```

### 3. Configure variáveis
```bash
export AWS_PROFILE=select
export AWS_DEFAULT_REGION=us-east-1
```

### 4. Teste a conexão
```bash
# Teste AWS
aws sts get-caller-identity

# Teste MySQL
mysql -h glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com -u select_admin -p
```

### 5. Execute o primeiro relatório
```bash
./scripts/run_full_report.sh
```

## Configuração do Cron

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 8 * * 6 /caminho/para/aws-cost-budget-reporter/scripts/run_full_report.sh
```

## Troubleshooting

### Erro de conexão RDS
- Verificar se está na mesma VPC
- Verificar Security Groups
- Testar conectividade: `telnet host 3306`

### Erro de assume role
- Verificar permissões IAM
- Verificar trust policy
- Testar: `aws sts assume-role --role-arn arn:aws:iam::ACCOUNT:role/ROLE --role-session-name test`

### Erro de budget API
- Verificar permissões budgets:*
- Verificar se budgets existem na conta
