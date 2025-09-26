# Estrutura do Banco de Dados

## Database: aws_costs

### Tabela: cost_reports

```sql
CREATE TABLE cost_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100),
    account_id VARCHAR(20),
    mes_anterior DECIMAL(10,2),
    atual_mtd DECIMAL(10,2),
    projecao DECIMAL(10,2),
    data_relatorio DATE,
    mes_referencia VARCHAR(7),
    ano_mes_anterior VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Índices:**
- `idx_cost_reports_mes_referencia` ON (mes_referencia)
- `idx_cost_reports_cliente_data` ON (cliente, data_relatorio)

### Tabela: budget_alerts

```sql
CREATE TABLE budget_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100),
    account_id VARCHAR(20),
    budget_name VARCHAR(200),
    budget_limit DECIMAL(10,2),
    actual_spend DECIMAL(10,2),
    forecasted_spend DECIMAL(10,2),
    percentage_used DECIMAL(5,2),
    alert_threshold DECIMAL(5,2),
    alert_triggered BOOLEAN,
    time_period VARCHAR(20),
    data_coleta DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Índices:**
- `idx_budget_cliente` ON (cliente)
- `idx_budget_data` ON (data_coleta)

## Relacionamentos

```sql
-- Custos e Budgets por cliente/conta
SELECT c.*, b.budget_limit
FROM cost_reports c
LEFT JOIN budget_alerts b ON c.cliente = b.cliente AND c.account_id = b.account_id
```

## Dados de Exemplo

### cost_reports
| cliente | account_id | mes_anterior | atual_mtd | projecao |
|---------|------------|--------------|-----------|----------|
| 2ABRASIL | 431102210488 | 451.56 | 269.73 | 425.88 |
| BEE4 | 975050187372 | 11766.36 | 6881.16 | 10865.00 |

### budget_alerts
| cliente | account_id | budget_name | budget_limit | actual_spend |
|---------|------------|-------------|--------------|--------------|
| 2ABRASIL | 431102210488 | 2abrasil-account-monthly | 560.00 | 0.00 |
