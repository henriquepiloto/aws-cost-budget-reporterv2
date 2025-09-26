import boto3
import os
from datetime import datetime, timedelta

def collect_cost_data():
    ce = boto3.client('ce')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cost-reporter-cost-data')
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['BlendedCost']
    )
    
    for result in response['ResultsByTime']:
        table.put_item(
            Item={
                'date': result['TimePeriod']['Start'],
                'cost': float(result['Total']['BlendedCost']['Amount']),
                'currency': result['Total']['BlendedCost']['Unit']
            }
        )
    
    print(f"Collected cost data from {start_date} to {end_date}")

if __name__ == "__main__":
    collect_cost_data()
