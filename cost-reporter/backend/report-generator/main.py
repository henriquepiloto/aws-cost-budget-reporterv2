import boto3
from datetime import datetime

def generate_report():
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    
    table = dynamodb.Table('cost-reporter-cost-data')
    response = table.scan()
    
    total_cost = sum(float(item['cost']) for item in response['Items'])
    
    report = f"""
    AWS Cost Report - {datetime.now().strftime('%Y-%m-%d')}
    
    Total Cost: ${total_cost:.2f}
    Items: {len(response['Items'])}
    """
    
    s3.put_object(
        Bucket='cost-reporter-reports-5phlwom2',
        Key=f"reports/cost-report-{datetime.now().strftime('%Y-%m-%d')}.txt",
        Body=report
    )
    
    print(f"Report generated with total cost: ${total_cost:.2f}")

if __name__ == "__main__":
    generate_report()
