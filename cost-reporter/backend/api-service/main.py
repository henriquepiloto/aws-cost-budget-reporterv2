from fastapi import FastAPI
import boto3
from boto3.dynamodb.conditions import Key

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Cost Reporter API"}

@app.get("/costs")
def get_costs():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cost-reporter-cost-data')
    
    response = table.scan()
    return {"costs": response['Items']}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
