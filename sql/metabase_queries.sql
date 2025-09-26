-- Queries para Metabase - MySQL

-- 1. Dados mais recentes por mês
SELECT 
    cliente,
    account_id,
    mes_anterior,
    atual_mtd,
    projecao,
    mes_referencia,
    data_relatorio
FROM cost_reports 
WHERE data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports cr2 
    WHERE cr2.mes_referencia = cost_reports.mes_referencia
)
ORDER BY cliente, account_id;

-- 2. Evolução mensal por cliente
SELECT 
    cliente,
    mes_referencia,
    SUM(mes_anterior) as total_mes_anterior,
    SUM(atual_mtd) as total_atual_mtd,
    SUM(projecao) as total_projecao
FROM cost_reports 
WHERE data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports cr2 
    WHERE cr2.mes_referencia = cost_reports.mes_referencia
)
GROUP BY cliente, mes_referencia
ORDER BY cliente, mes_referencia;

-- 3. Comparação mês a mês (últimos 6 meses)
SELECT 
    mes_referencia,
    SUM(projecao) as total_projetado,
    COUNT(DISTINCT cliente) as total_clientes,
    COUNT(*) as total_contas
FROM cost_reports 
WHERE mes_referencia >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 6 MONTH), '%Y-%m')
  AND data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports cr2 
    WHERE cr2.mes_referencia = cost_reports.mes_referencia
  )
GROUP BY mes_referencia
ORDER BY mes_referencia;

-- 4. Top 10 clientes por custo atual
SELECT 
    cliente,
    SUM(projecao) as total_projetado,
    COUNT(*) as num_contas
FROM cost_reports 
WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  AND data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports 
    WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  )
GROUP BY cliente
ORDER BY total_projetado DESC
LIMIT 10;

-- 5. Histórico completo para dashboard
SELECT 
    data_relatorio,
    mes_referencia,
    cliente,
    account_id,
    mes_anterior,
    atual_mtd,
    projecao,
    (projecao - mes_anterior) as diferenca,
    CASE 
        WHEN mes_anterior > 0 THEN ROUND(((projecao - mes_anterior) / mes_anterior * 100), 2)
        ELSE 0 
    END as percentual_variacao
FROM cost_reports
ORDER BY data_relatorio DESC, cliente, account_id;

-- 6. Resumo geral atual
SELECT 
    COUNT(DISTINCT cliente) as total_clientes,
    COUNT(*) as total_contas,
    SUM(mes_anterior) as total_mes_anterior,
    SUM(atual_mtd) as total_atual_mtd,
    SUM(projecao) as total_projecao,
    ROUND(((SUM(projecao) - SUM(mes_anterior)) / SUM(mes_anterior) * 100), 2) as variacao_percentual
FROM cost_reports 
WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  AND data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports 
    WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  );

-- 7. Contas com maior variação (crescimento)
SELECT 
    cliente,
    account_id,
    mes_anterior,
    projecao,
    (projecao - mes_anterior) as diferenca,
    ROUND(((projecao - mes_anterior) / mes_anterior * 100), 2) as percentual_variacao
FROM cost_reports 
WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  AND data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports 
    WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  )
  AND mes_anterior > 0
ORDER BY percentual_variacao DESC
LIMIT 10;

-- 8. Evolução mensal - últimos 12 meses
SELECT 
    mes_referencia,
    SUM(projecao) as total_mes
FROM cost_reports 
WHERE mes_referencia >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 12 MONTH), '%Y-%m')
  AND data_relatorio = (
    SELECT MAX(data_relatorio) 
    FROM cost_reports cr2 
    WHERE cr2.mes_referencia = cost_reports.mes_referencia
  )
GROUP BY mes_referencia
ORDER BY mes_referencia;

-- QUERIES DE BUDGET PARA METABASE

-- 9. Resumo de budgets por cliente
SELECT 
    cliente,
    COUNT(*) as total_budgets,
    SUM(budget_limit) as total_limit,
    SUM(actual_spend) as total_actual,
    SUM(forecasted_spend) as total_forecasted,
    AVG(percentage_used) as avg_percentage,
    SUM(CASE WHEN alert_triggered = 1 THEN 1 ELSE 0 END) as alerts_triggered
FROM budget_alerts 
WHERE data_coleta = CURDATE()
GROUP BY cliente
ORDER BY total_limit DESC;

-- 10. Budgets com alertas disparados
SELECT 
    cliente,
    account_id,
    budget_name,
    budget_limit,
    actual_spend,
    percentage_used,
    alert_threshold
FROM budget_alerts 
WHERE alert_triggered = 1 AND data_coleta = CURDATE()
ORDER BY percentage_used DESC;

-- 11. Top budgets por utilização
SELECT 
    cliente,
    account_id,
    budget_name,
    budget_limit,
    actual_spend,
    forecasted_spend,
    percentage_used
FROM budget_alerts 
WHERE data_coleta = CURDATE()
ORDER BY percentage_used DESC
LIMIT 20;

-- 12. Comparação budget vs custo real
SELECT 
    b.cliente,
    b.account_id,
    b.budget_limit,
    b.actual_spend as budget_actual,
    b.forecasted_spend,
    c.projecao as cost_projection,
    (c.projecao - b.budget_limit) as budget_variance
FROM budget_alerts b
LEFT JOIN cost_reports c ON b.cliente = c.cliente AND b.account_id = c.account_id
WHERE b.data_coleta = CURDATE() 
  AND c.mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m')
  AND c.data_relatorio = (SELECT MAX(data_relatorio) FROM cost_reports WHERE mes_referencia = DATE_FORMAT(CURDATE(), '%Y-%m'))
ORDER BY budget_variance DESC;
