import json
import boto3
import botocore
from botocore.config import Config
import os
from datetime import datetime
import time

now = datetime.now() # current date and time
curr_time = now.strftime("%H%M%S%f")

def lambda_handler(event, context):
    print("Entering lambda_handler for dr-orchestrator-lambda-failover-RDS")
    print(f"event: {event}")
    print("Before RDS Client Connection")
    client = boto3.client('rds')

    try:
        response = client.promote_read_replica(
        DBInstanceIdentifier = event["RDSInstanceIdentifier"]
        )
        print("promote_read_replica response = ", response)

        # To avoid TypeError: Object of type datetime is not JSON serializable
        exclude_keys = ['InstanceCreateTime']
        response_final = response['DBInstance']
        [response_final.pop(key) for key in exclude_keys]
        print(f"Putting a wait for 60 seconds because RDS instance status does not change immediately")
        time.sleep(60)
        return {
            'statusCode' :200,
            'body' : json.dumps(response_final,default=str)
        }
    except botocore.exceptions.ClientError as error:
        print(f"Error occurred:", error)
        raise error 
