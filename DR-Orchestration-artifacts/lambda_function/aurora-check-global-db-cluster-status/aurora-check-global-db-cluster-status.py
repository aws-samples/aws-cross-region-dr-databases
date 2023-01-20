import boto3
import json
import botocore
from botocore.config import Config
import os

def lambda_handler(event, context):              
    print(event)
    client = boto3.client('rds')

    try:
      cluster = client.describe_global_clusters(GlobalClusterIdentifier = event["GlobalClusterIdentifier"])
      print("cluster response=",cluster)
      return {
          'status': cluster["GlobalClusters"][0]["Status"]
        }
    except client.exceptions.GlobalClusterNotFoundFault as exp:
        return {
        'status' : 'doesnotexist'
        }
    except botocore.exceptions.ClientError as error:
        raise error