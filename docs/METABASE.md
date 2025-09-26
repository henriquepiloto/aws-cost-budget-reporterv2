# Configuração do Metabase

## Conexão com MySQL

### Configurações
- **Database type**: MySQL
- **Host**: glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com
- **Port**: 3306
- **Database name**: aws_costs
- **Username**: select_admin
- **Password**: GR558AvfoYFz7NTZ1q8n

## Dashboards Sugeridos

### 1. Overview de Custos
**Métricas principais:**
- Total de clientes: 58
- Total de contas: 163
- Projeção mensal: $696,862.02
- Budgets configurados: 190

### 2. Top 10 Clientes por Custo
```sql
SELECT cliente, SUM(projecao) as total_projetado
FROM cost_reports 
WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
GROUP BY cliente
ORDER BY total_projetado DESC LIMIT 10;
```

### 3. Alertas de Budget
```sql
SELECT cliente, account_id, budget_name, budget_limit, actual_spend, percentage_used
FROM budget_alerts 
WHERE alert_triggered = 1 AND data_coleta = CURDATE()
ORDER BY percentage_used DESC;
```

### 4. Evolução Mensal
```sql
SELECT mes_referencia, SUM(projecao) as total_mes
FROM cost_reports 
WHERE mes_referencia >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 12 MONTH), '%Y-%m')
GROUP BY mes_referencia
ORDER BY mes_referencia;
```

### 5. Budget vs Custo Real
```sql
SELECT 
    b.cliente,
    SUM(b.budget_limit) as total_budget,
    SUM(c.projecao) as total_custo,
    (SUM(c.projecao) - SUM(b.budget_limit)) as diferenca,
    ROUND(((SUM(c.projecao) - SUM(b.budget_limit)) / SUM(b.budget_limit) * 100), 2) as percentual_variacao
FROM budget_alerts b
LEFT JOIN cost_reports c ON b.cliente = c.cliente AND b.account_id = c.account_id
WHERE b.data_coleta = CURDATE()
  AND c.mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
GROUP BY b.cliente
ORDER BY diferenca DESC;
```

## Alertas Automáticos

### Configurar Alertas
1. **Budget Excedido**: `percentage_used > 90`
2. **Custo Alto**: `projecao > budget_limit * 1.1`
3. **Crescimento Anômalo**: `(projecao - mes_anterior) / mes_anterior > 0.5`

### Notificações
- Email para equipe financeira
- Slack para equipe técnica
- Dashboard de alertas

## Filtros Úteis

- **Por Cliente**: Dropdown com todos os clientes
- **Por Período**: Date range picker
- **Por Conta**: Multi-select de contas
- **Alertas Ativos**: Boolean filter

## Visualizações

### Gráficos Recomendados
1. **Line Chart**: Evolução mensal de custos
2. **Bar Chart**: Top clientes por custo
3. **Pie Chart**: Distribuição de custos por cliente
4. **Table**: Lista de alertas ativos
5. **Number**: KPIs principais
6. **Gauge**: Utilização de budget

### Cores Sugeridas
- 🟢 Verde: Budget OK (< 70%)
- 🟡 Amarelo: Atenção (70-90%)
- 🔴 Vermelho: Alerta (> 90%)
