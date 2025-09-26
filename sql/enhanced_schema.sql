-- Enhanced Database Schema for AWS Cost Analytics
-- Fase 1: Estrutura de dados granular

-- Tabela principal de custos diários detalhados
CREATE TABLE IF NOT EXISTS daily_costs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) DEFAULT 'global',
    cost_date DATE NOT NULL,
    amount DECIMAL(12,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    usage_type VARCHAR(200),
    operation VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_daily_costs_main (cliente, account_id, cost_date),
    INDEX idx_daily_costs_service (service_name, cost_date),
    INDEX idx_daily_costs_date (cost_date),
    UNIQUE KEY unique_daily_cost (cliente, account_id, service_name, region, cost_date, usage_type, operation)
);

-- Tabela de custos mensais por serviço
CREATE TABLE IF NOT EXISTS monthly_service_costs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) DEFAULT 'global',
    year_month VARCHAR(7) NOT NULL, -- YYYY-MM
    total_cost DECIMAL(12,4) NOT NULL,
    avg_daily_cost DECIMAL(12,4),
    max_daily_cost DECIMAL(12,4),
    min_daily_cost DECIMAL(12,4),
    days_with_usage INT DEFAULT 0,
    growth_rate DECIMAL(8,4), -- % crescimento vs mês anterior
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_monthly_service_main (cliente, account_id, year_month),
    INDEX idx_monthly_service_name (service_name, year_month),
    UNIQUE KEY unique_monthly_service (cliente, account_id, service_name, region, year_month)
);

-- Tabela de métricas agregadas
CREATE TABLE IF NOT EXISTS cost_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    metric_type ENUM('total_monthly', 'top_service', 'fastest_growing', 'cost_trend', 'daily_avg') NOT NULL,
    metric_period VARCHAR(20) NOT NULL, -- YYYY-MM ou YYYY-MM-DD
    metric_value DECIMAL(12,4),
    metric_text VARCHAR(500), -- Para valores textuais como nome do serviço
    additional_data JSON, -- Dados extras em formato JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metrics_main (cliente, account_id, metric_type, metric_period),
    INDEX idx_metrics_period (metric_period, metric_type)
);

-- Tabela de tendências e alertas
CREATE TABLE IF NOT EXISTS cost_trends (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    service_name VARCHAR(100),
    trend_type ENUM('increasing', 'decreasing', 'stable', 'volatile') NOT NULL,
    trend_period VARCHAR(20) NOT NULL, -- Período analisado
    growth_percentage DECIMAL(8,4),
    confidence_score DECIMAL(5,2), -- 0-100
    alert_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trends_main (cliente, account_id, trend_type),
    INDEX idx_trends_alert (alert_level, created_at)
);

-- Tabela de dimensões de serviços (para normalização)
CREATE TABLE IF NOT EXISTS aws_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_code VARCHAR(50) UNIQUE NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    service_category VARCHAR(50), -- Compute, Storage, Database, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_services_category (service_category)
);

-- Views para análises comuns
CREATE OR REPLACE VIEW v_monthly_costs_summary AS
SELECT 
    cliente,
    account_id,
    year_month,
    SUM(total_cost) as total_monthly_cost,
    COUNT(DISTINCT service_name) as services_count,
    MAX(total_cost) as highest_service_cost,
    AVG(growth_rate) as avg_growth_rate
FROM monthly_service_costs 
GROUP BY cliente, account_id, year_month;

CREATE OR REPLACE VIEW v_top_services_by_cost AS
SELECT 
    cliente,
    account_id,
    service_name,
    year_month,
    total_cost,
    RANK() OVER (PARTITION BY cliente, account_id, year_month ORDER BY total_cost DESC) as cost_rank
FROM monthly_service_costs;

CREATE OR REPLACE VIEW v_cost_growth_analysis AS
SELECT 
    cliente,
    account_id,
    service_name,
    year_month,
    total_cost,
    growth_rate,
    CASE 
        WHEN growth_rate > 50 THEN 'High Growth'
        WHEN growth_rate > 20 THEN 'Medium Growth'
        WHEN growth_rate > 0 THEN 'Low Growth'
        WHEN growth_rate < -20 THEN 'Significant Decrease'
        ELSE 'Stable'
    END as growth_category
FROM monthly_service_costs
WHERE growth_rate IS NOT NULL;

-- Inserir serviços AWS principais
INSERT IGNORE INTO aws_services (service_code, service_name, service_category) VALUES
('AmazonEC2', 'Amazon Elastic Compute Cloud', 'Compute'),
('AmazonS3', 'Amazon Simple Storage Service', 'Storage'),
('AmazonRDS', 'Amazon Relational Database Service', 'Database'),
('AWSLambda', 'AWS Lambda', 'Compute'),
('AmazonCloudFront', 'Amazon CloudFront', 'Content Delivery'),
('AmazonVPC', 'Amazon Virtual Private Cloud', 'Networking'),
('AmazonRoute53', 'Amazon Route 53', 'Networking'),
('AmazonEBS', 'Amazon Elastic Block Store', 'Storage'),
('AmazonELB', 'Elastic Load Balancing', 'Networking'),
('AmazonCloudWatch', 'Amazon CloudWatch', 'Management'),
('AmazonEKS', 'Amazon Elastic Kubernetes Service', 'Compute'),
('AmazonECS', 'Amazon Elastic Container Service', 'Compute'),
('AmazonRedshift', 'Amazon Redshift', 'Database'),
('AmazonDynamoDB', 'Amazon DynamoDB', 'Database'),
('AmazonSNS', 'Amazon Simple Notification Service', 'Application Integration'),
('AmazonSQS', 'Amazon Simple Queue Service', 'Application Integration');
