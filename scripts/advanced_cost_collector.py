#!/usr/bin/env python3
"""
Advanced Cost Collector - Fase 2
Coleta Reserved Instances, Rightsizing, Savings Plans e Anomalias
"""

import json
import boto3
import pymysql
from datetime import datetime, timedelta
import os
from decimal import Decimal

def get_database_credentials():
    """Recupera credenciais do banco de dados do AWS Secrets Manager"""
    secret_name = "glpidatabaseadmin"
    region_name = "us-east-1"
    
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        return {
            'host': secret.get('host'),
            'username': secret['username'],
            'password': secret['password'],
            'port': secret.get('port', 3306),
            'dbname': secret.get('dbname', 'aws_costs')
        }
    except Exception as e:
        print(f"✗ Erro ao carregar credenciais: {e}")
        raise

def load_roles_from_s3():
    """Carrega o arquivo roles.json diretamente do S3"""
    s3_roles_uri = os.environ.get('S3_ROLES_URI')
    if not s3_roles_uri:
        raise ValueError("Variável de ambiente S3_ROLES_URI não definida")
    
    uri_parts = s3_roles_uri[5:].split('/', 1)
    bucket_name = uri_parts[0]
    object_key = uri_parts[1] if len(uri_parts) > 1 else 'roles.json'
    
    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        roles_data = json.loads(response['Body'].read().decode('utf-8'))
        return roles_data
    except Exception as e:
        print(f"✗ Erro ao carregar roles do S3: {e}")
        raise

def assume_role(account_id, role_name):
    """Assume role para acessar conta AWS"""
    try:
        sts_client = boto3.client('sts', region_name='us-east-1')
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"advanced-cost-{account_id}")
        credentials = response['Credentials']
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
    except Exception as e:
        print(f"✗ Erro ao assumir role: {e}")
        return None

def collect_reserved_instances(session, cliente, account_id):
    """Coleta informações de Reserved Instances"""
    try:
        ec2_client = session.client('ec2', region_name='us-east-1')
        response = ec2_client.describe_reserved_instances()
        
        ri_data = []
        for ri in response['ReservedInstances']:
            ri_data.append({
                'cliente': cliente,
                'account_id': account_id,
                'ri_id': ri['ReservedInstancesId'],
                'instance_type': ri['InstanceType'],
                'availability_zone': ri.get('AvailabilityZone', ''),
                'platform': ri.get('ProductDescription', ''),
                'state': ri['State'],
                'start_date': ri['Start'].date(),
                'end_date': ri['End'].date(),
                'duration_months': ri['Duration'] // (30 * 24 * 3600),  # Convert seconds to months
                'instance_count': ri['InstanceCount'],
                'fixed_price': float(ri.get('FixedPrice', 0)),
                'usage_price': float(ri.get('UsagePrice', 0))
            })
        
        return ri_data
    except Exception as e:
        print(f"✗ Erro ao coletar RIs: {e}")
        return []

def collect_rightsizing_recommendations(session, cliente, account_id):
    """Coleta recomendações de rightsizing"""
    try:
        ce_client = session.client('ce', region_name='us-east-1')
        response = ce_client.get_rightsizing_recommendation(
            Service='AmazonEC2',
            Configuration={
                'BenefitsConsidered': True,
                'RecommendationTarget': 'SAME_INSTANCE_FAMILY'
            }
        )
        
        recommendations = []
        for rec in response.get('RightsizingRecommendations', []):
            current_instance = rec.get('CurrentInstance', {})
            modify_rec = rec.get('ModifyRecommendationDetail', {})
            
            if modify_rec:
                recommendations.append({
                    'cliente': cliente,
                    'account_id': account_id,
                    'resource_id': current_instance.get('ResourceId', ''),
                    'resource_type': 'EC2',
                    'current_instance_type': current_instance.get('InstanceType', ''),
                    'recommended_instance_type': modify_rec.get('TargetInstances', [{}])[0].get('InstanceType', ''),
                    'current_monthly_cost': float(current_instance.get('MonthlyCost', 0)),
                    'estimated_monthly_cost': float(modify_rec.get('TargetInstances', [{}])[0].get('EstimatedMonthlyCost', 0)),
                    'estimated_savings': float(modify_rec.get('TargetInstances', [{}])[0].get('EstimatedMonthlySavings', 0)),
                    'cpu_utilization': float(current_instance.get('ResourceUtilization', {}).get('EC2ResourceUtilization', {}).get('MaxCpuUtilizationPercentage', 0)),
                    'last_updated_date': datetime.now().date()
                })
        
        return recommendations
    except Exception as e:
        print(f"✗ Erro ao coletar rightsizing: {e}")
        return []

def collect_savings_plans(session, cliente, account_id):
    """Coleta informações de Savings Plans"""
    try:
        sp_client = session.client('savingsplans', region_name='us-east-1')
        response = sp_client.describe_savings_plans()
        
        sp_data = []
        for sp in response['savingsPlans']:
            sp_data.append({
                'cliente': cliente,
                'account_id': account_id,
                'savings_plan_id': sp['savingsPlanId'],
                'savings_plan_type': sp['savingsPlanType'],
                'payment_option': sp['paymentOption'],
                'plan_type': sp['planType'],
                'commitment': float(sp['commitment']),
                'hourly_commitment': float(sp['hourlyCommitment']),
                'start_date': sp['start'].date(),
                'end_date': sp['end'].date(),
                'state': sp['state']
            })
        
        return sp_data
    except Exception as e:
        print(f"✗ Erro ao coletar Savings Plans: {e}")
        return []

def collect_cost_anomalies(session, cliente, account_id):
    """Coleta anomalias de custo"""
    try:
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Últimos 30 dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        response = ce_client.get_anomalies(
            DateInterval={
                'StartDate': start_date.strftime('%Y-%m-%d'),
                'EndDate': end_date.strftime('%Y-%m-%d')
            }
        )
        
        anomalies = []
        for anomaly in response.get('Anomalies', []):
            anomalies.append({
                'cliente': cliente,
                'account_id': account_id,
                'anomaly_id': anomaly['AnomalyId'],
                'anomaly_date': datetime.strptime(anomaly['AnomalyStartDate'], '%Y-%m-%d').date(),
                'anomaly_score': float(anomaly['AnomalyScore']['MaxScore']),
                'impact_value': float(anomaly['Impact']['MaxImpact']),
                'anomaly_type': 'cost_spike'  # Simplificado
            })
        
        return anomalies
    except Exception as e:
        print(f"✗ Erro ao coletar anomalias: {e}")
        return []

def save_advanced_data(data_type, data, db_config):
    """Salva dados avançados no banco"""
    if not data:
        return
    
    conn = pymysql.connect(
        host=db_config['host'], 
        user=db_config['username'], 
        password=db_config['password'], 
        database='aws_costs', 
        port=db_config['port'],
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    if data_type == 'reserved_instances':
        for record in data:
            cursor.execute("""
                INSERT INTO reserved_instances 
                (cliente, account_id, ri_id, instance_type, availability_zone, platform, 
                 state, start_date, end_date, duration_months, instance_count, fixed_price, usage_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    state = VALUES(state),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                record['cliente'], record['account_id'], record['ri_id'],
                record['instance_type'], record['availability_zone'], record['platform'],
                record['state'], record['start_date'], record['end_date'],
                record['duration_months'], record['instance_count'],
                record['fixed_price'], record['usage_price']
            ))
    
    elif data_type == 'rightsizing':
        for record in data:
            cursor.execute("""
                INSERT INTO rightsizing_recommendations 
                (cliente, account_id, resource_id, resource_type, current_instance_type,
                 recommended_instance_type, current_monthly_cost, estimated_monthly_cost,
                 estimated_savings, cpu_utilization, last_updated_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    recommended_instance_type = VALUES(recommended_instance_type),
                    estimated_monthly_cost = VALUES(estimated_monthly_cost),
                    estimated_savings = VALUES(estimated_savings),
                    cpu_utilization = VALUES(cpu_utilization)
            """, (
                record['cliente'], record['account_id'], record['resource_id'],
                record['resource_type'], record['current_instance_type'],
                record['recommended_instance_type'], record['current_monthly_cost'],
                record['estimated_monthly_cost'], record['estimated_savings'],
                record['cpu_utilization'], record['last_updated_date']
            ))
    
    elif data_type == 'savings_plans':
        for record in data:
            cursor.execute("""
                INSERT INTO savings_plans 
                (cliente, account_id, savings_plan_id, savings_plan_type, payment_option,
                 plan_type, commitment, hourly_commitment, start_date, end_date, state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    state = VALUES(state),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                record['cliente'], record['account_id'], record['savings_plan_id'],
                record['savings_plan_type'], record['payment_option'], record['plan_type'],
                record['commitment'], record['hourly_commitment'],
                record['start_date'], record['end_date'], record['state']
            ))
    
    elif data_type == 'anomalies':
        for record in data:
            cursor.execute("""
                INSERT IGNORE INTO cost_anomalies 
                (cliente, account_id, anomaly_id, anomaly_date, anomaly_score, impact_value, anomaly_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                record['cliente'], record['account_id'], record['anomaly_id'],
                record['anomaly_date'], record['anomaly_score'],
                record['impact_value'], record['anomaly_type']
            ))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    """Função principal"""
    print("🔬 Iniciando coleta avançada de dados AWS...")
    
    db_config = get_database_credentials()
    roles_data = load_roles_from_s3()
    
    # Contadores
    total_ris = 0
    total_rightsizing = 0
    total_savings_plans = 0
    total_anomalies = 0
    
    for role in roles_data:
        print(f"🔄 Processando {role['cliente']} - {role['account_id']}")
        
        session = assume_role(role['account_id'], role['role_name'])
        if not session:
            continue
        
        # Coletar Reserved Instances
        ri_data = collect_reserved_instances(session, role['cliente'], role['account_id'])
        if ri_data:
            save_advanced_data('reserved_instances', ri_data, db_config)
            total_ris += len(ri_data)
        
        # Coletar Rightsizing
        rightsizing_data = collect_rightsizing_recommendations(session, role['cliente'], role['account_id'])
        if rightsizing_data:
            save_advanced_data('rightsizing', rightsizing_data, db_config)
            total_rightsizing += len(rightsizing_data)
        
        # Coletar Savings Plans
        sp_data = collect_savings_plans(session, role['cliente'], role['account_id'])
        if sp_data:
            save_advanced_data('savings_plans', sp_data, db_config)
            total_savings_plans += len(sp_data)
        
        # Coletar Anomalias
        anomaly_data = collect_cost_anomalies(session, role['cliente'], role['account_id'])
        if anomaly_data:
            save_advanced_data('anomalies', anomaly_data, db_config)
            total_anomalies += len(anomaly_data)
        
        print(f"✓ RIs: {len(ri_data)}, Rightsizing: {len(rightsizing_data)}, SPs: {len(sp_data)}, Anomalias: {len(anomaly_data)}")
    
    print(f"\n✅ Coleta avançada concluída:")
    print(f"  📊 Reserved Instances: {total_ris}")
    print(f"  🎯 Rightsizing Recs: {total_rightsizing}")
    print(f"  💰 Savings Plans: {total_savings_plans}")
    print(f"  🚨 Anomalias: {total_anomalies}")

if __name__ == "__main__":
    main()
