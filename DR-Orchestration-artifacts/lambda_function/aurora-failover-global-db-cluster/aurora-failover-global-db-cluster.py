import json
import boto3
import botocore
from botocore.config import Config
import os          
from datetime import datetime
import time

def lambda_handler(event, context):
    print("Entering lambda_handler for dr-orchestrator-lambda-failover-Aurora-GlobalDatabase")
    print(f"event: {event}") 

    client = boto3.client('rds')

    try:
        response = client.failover_global_cluster(
            GlobalClusterIdentifier = event["GlobalClusterIdentifier"],
            TargetDbClusterIdentifier = event["DBClusterIdentifier"]
        )
        print("failover_global_cluster  response = ", response)
        time.sleep(60)
        return {
            'statusCode' :200,
            'body' : json.dumps(response)
        }
    except botocore.exceptions.ClientError as error:
        print(f"Error occurred:", error)
        raise error