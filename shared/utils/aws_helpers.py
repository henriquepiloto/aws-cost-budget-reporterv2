"""
Shared AWS utilities for both Prisma Admin and Cost Reporter
"""

import boto3
import json
from typing import Dict, Any, Optional

class AWSHelper:
    """Common AWS operations for both projects"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.session = boto3.Session(region_name=region)
    
    def get_lambda_client(self):
        """Get Lambda client"""
        return self.session.client('lambda')
    
    def get_s3_client(self):
        """Get S3 client"""
        return self.session.client('s3')
    
    def get_rds_client(self):
        """Get RDS client"""
        return self.session.client('rds')
    
    def get_cost_explorer_client(self):
        """Get Cost Explorer client"""
        return self.session.client('ce')
    
    def get_cloudfront_client(self):
        """Get CloudFront client"""
        return self.session.client('cloudfront')
    
    def invalidate_cloudfront(self, distribution_id: str, paths: list = ["/*"]) -> str:
        """Invalidate CloudFront distribution"""
        client = self.get_cloudfront_client()
        
        response = client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': f'invalidation-{int(time.time())}'
            }
        )
        
        return response['Invalidation']['Id']
    
    def upload_to_s3(self, bucket: str, key: str, content: str, content_type: str = 'text/html'):
        """Upload content to S3"""
        client = self.get_s3_client()
        
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType=content_type
        )
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Get secret from AWS Secrets Manager"""
        client = self.session.client('secretsmanager')
        
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])

# Common configurations
PRISMA_CONFIG = {
    'S3_BUCKET': 'prisma-admin-selectsolucoes',
    'CLOUDFRONT_DISTRIBUTION': 'E1SAZUX6DR5QF3',
    'LAMBDA_FUNCTION': 'chatbot-auth',
    'RDS_INSTANCE': 'glpi-database-instance-1',
    'DOMAIN': 'prisma.selectsolucoes.com'
}

COST_REPORTER_CONFIG = {
    # To be defined when Cost Reporter is implemented
    'S3_BUCKET': 'cost-reporter-selectsolucoes',
    'LAMBDA_FUNCTION': 'cost-reporter',
    'DOMAIN': 'costs.selectsolucoes.com'
}
