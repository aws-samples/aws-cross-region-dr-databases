import boto3
import json
import botocore
from botocore.config import Config
import os

def lambda_handler(event, context):              
    print(event)
    client = boto3.client('rds')
    try:
        cluster = client.describe_db_instances(DBInstanceIdentifier = event["DBInstanceIdentifier"])
        return {
            'status': cluster["DBInstances"][0]["DBInstanceStatus"]
        }                  
    except client.exceptions.DBInstanceNotFoundFault as exp:
        return {
        'status' : 'doesnotexist'
        }
    except botocore.exceptions.ClientError as error:
        raise error