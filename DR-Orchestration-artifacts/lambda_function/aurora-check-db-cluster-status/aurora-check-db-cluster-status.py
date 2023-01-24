import boto3
import json
import botocore
from botocore.config import Config
import os

def lambda_handler(event, context):              
    print(event)
    client = boto3.client('rds')

    try:
      cluster = client.describe_db_clusters(DBClusterIdentifier = event["DBClusterIdentifier"])
      print("cluster response=",cluster)
      return {
          'status': cluster["DBClusters"][0]["Status"]
        }
    except client.exceptions.DBClusterNotFoundFault as exp:
        return {
        'status' : 'doesnotexist'
        }
    except botocore.exceptions.ClientError as error:
        raise error