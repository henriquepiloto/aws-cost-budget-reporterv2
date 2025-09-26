-- Phase 2 Schema Extensions
-- Reserved Instances, Rightsizing, Forecasting

-- Tabela de Reserved Instances
CREATE TABLE IF NOT EXISTS reserved_instances (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    ri_id VARCHAR(100) NOT NULL,
    instance_type VARCHAR(50),
    availability_zone VARCHAR(50),
    platform VARCHAR(50),
    tenancy VARCHAR(20),
    offering_class VARCHAR(20),
    offering_type VARCHAR(50),
    state VARCHAR(20),
    start_date DATE,
    end_date DATE,
    duration_months INT,
    instance_count INT,
    fixed_price DECIMAL(12,4),
    usage_price DECIMAL(12,4),
    currency_code VARCHAR(3) DEFAULT 'USD',
    utilization_percentage DECIMAL(5,2),
    savings_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ri_main (cliente, account_id, state),
    INDEX idx_ri_dates (start_date, end_date),
    UNIQUE KEY unique_ri (account_id, ri_id)
);

-- Tabela de Rightsizing Recommendations
CREATE TABLE IF NOT EXISTS rightsizing_recommendations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    resource_type ENUM('EC2', 'RDS', 'ElastiCache', 'Redshift') NOT NULL,
    current_instance_type VARCHAR(50),
    recommended_instance_type VARCHAR(50),
    current_monthly_cost DECIMAL(12,4),
    estimated_monthly_cost DECIMAL(12,4),
    estimated_savings DECIMAL(12,4),
    savings_percentage DECIMAL(5,2),
    cpu_utilization DECIMAL(5,2),
    memory_utilization DECIMAL(5,2),
    network_utilization DECIMAL(5,2),
    recommendation_reason TEXT,
    confidence_level ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    last_updated_date DATE,
    status ENUM('Active', 'Dismissed', 'Applied') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rightsizing_main (cliente, account_id, status),
    INDEX idx_rightsizing_savings (estimated_savings DESC),
    UNIQUE KEY unique_rightsizing (account_id, resource_id, last_updated_date)
);

-- Tabela de Cost Forecasting
CREATE TABLE IF NOT EXISTS cost_forecasts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    service_name VARCHAR(100),
    forecast_period VARCHAR(20) NOT NULL, -- YYYY-MM
    forecast_type ENUM('monthly', 'quarterly', 'annual') NOT NULL,
    predicted_cost DECIMAL(12,4) NOT NULL,
    confidence_interval_lower DECIMAL(12,4),
    confidence_interval_upper DECIMAL(12,4),
    prediction_accuracy DECIMAL(5,2),
    trend_direction ENUM('increasing', 'decreasing', 'stable') NOT NULL,
    seasonal_factor DECIMAL(8,4),
    growth_rate DECIMAL(8,4),
    model_used VARCHAR(50) DEFAULT 'linear_regression',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_forecasts_main (cliente, account_id, forecast_period),
    INDEX idx_forecasts_service (service_name, forecast_period),
    UNIQUE KEY unique_forecast (cliente, account_id, service_name, forecast_period, forecast_type)
);

-- Tabela de Savings Plans
CREATE TABLE IF NOT EXISTS savings_plans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    savings_plan_id VARCHAR(100) NOT NULL,
    savings_plan_type VARCHAR(50),
    payment_option VARCHAR(50),
    plan_type VARCHAR(50),
    commitment DECIMAL(12,4),
    hourly_commitment DECIMAL(12,4),
    currency_code VARCHAR(3) DEFAULT 'USD',
    start_date DATE,
    end_date DATE,
    state VARCHAR(20),
    utilization_percentage DECIMAL(5,2),
    savings_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sp_main (cliente, account_id, state),
    INDEX idx_sp_dates (start_date, end_date),
    UNIQUE KEY unique_sp (account_id, savings_plan_id)
);

-- Tabela de Cost Anomalies
CREATE TABLE IF NOT EXISTS cost_anomalies (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    anomaly_id VARCHAR(100),
    service_name VARCHAR(100),
    anomaly_date DATE NOT NULL,
    anomaly_score DECIMAL(8,4),
    impact_value DECIMAL(12,4),
    expected_value DECIMAL(12,4),
    actual_value DECIMAL(12,4),
    anomaly_type ENUM('cost_spike', 'usage_spike', 'new_service', 'service_change') NOT NULL,
    root_cause TEXT,
    status ENUM('detected', 'investigating', 'resolved', 'false_positive') DEFAULT 'detected',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    INDEX idx_anomalies_main (cliente, account_id, anomaly_date),
    INDEX idx_anomalies_score (anomaly_score DESC),
    INDEX idx_anomalies_status (status, created_at)
);

-- Views para análises avançadas
CREATE OR REPLACE VIEW v_ri_utilization_summary AS
SELECT 
    cliente,
    account_id,
    COUNT(*) as total_ris,
    AVG(utilization_percentage) as avg_utilization,
    SUM(CASE WHEN utilization_percentage < 80 THEN 1 ELSE 0 END) as underutilized_ris,
    SUM(fixed_price + (usage_price * instance_count * 24 * 30)) as monthly_ri_cost
FROM reserved_instances 
WHERE state = 'active'
GROUP BY cliente, account_id;

CREATE OR REPLACE VIEW v_rightsizing_opportunities AS
SELECT 
    cliente,
    account_id,
    resource_type,
    COUNT(*) as total_recommendations,
    SUM(estimated_savings) as total_potential_savings,
    AVG(savings_percentage) as avg_savings_percentage,
    SUM(CASE WHEN confidence_level = 'High' THEN estimated_savings ELSE 0 END) as high_confidence_savings
FROM rightsizing_recommendations 
WHERE status = 'Active'
GROUP BY cliente, account_id, resource_type;

CREATE OR REPLACE VIEW v_cost_forecast_summary AS
SELECT 
    cliente,
    account_id,
    forecast_period,
    SUM(predicted_cost) as total_predicted_cost,
    AVG(prediction_accuracy) as avg_accuracy,
    COUNT(DISTINCT service_name) as services_forecasted
FROM cost_forecasts 
WHERE forecast_type = 'monthly'
GROUP BY cliente, account_id, forecast_period;

CREATE OR REPLACE VIEW v_savings_opportunities AS
SELECT 
    r.cliente,
    r.account_id,
    'Rightsizing' as opportunity_type,
    SUM(r.estimated_savings) as potential_savings,
    COUNT(*) as opportunities_count
FROM rightsizing_recommendations r 
WHERE r.status = 'Active'
GROUP BY r.cliente, r.account_id

UNION ALL

SELECT 
    ri.cliente,
    ri.account_id,
    'RI Optimization' as opportunity_type,
    SUM(ri.fixed_price * (100 - ri.utilization_percentage) / 100) as potential_savings,
    COUNT(*) as opportunities_count
FROM reserved_instances ri 
WHERE ri.state = 'active' AND ri.utilization_percentage < 80
GROUP BY ri.cliente, ri.account_id;

-- Índices adicionais para performance
CREATE INDEX idx_daily_costs_service_date ON daily_costs(service_name, cost_date);
CREATE INDEX idx_monthly_service_growth ON monthly_service_costs(growth_rate DESC);
CREATE INDEX idx_cost_trends_alert_date ON cost_trends(alert_level, created_at DESC);
