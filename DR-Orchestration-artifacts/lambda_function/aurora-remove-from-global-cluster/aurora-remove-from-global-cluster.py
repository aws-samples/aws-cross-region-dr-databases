import json
import boto3
import botocore
import os
from botocore.config import Config
from datetime import datetime
import time

curr_session = boto3.session.Session()
curr_region = curr_session.region_name

class RemoveGlobalDBFromDiffRegionIsNotAllowed(Exception):
  def __str__(self):
    return "'Remove from Global Database operation should run from the same region where cluster exists. Please check the payload and try again!'"

def lambda_handler(event, context):
  print("Entering lambda_handler for dr-orchestrator-lambda-delete-aurora-db-cluster")
  print("curr_region = ", curr_region)
  print("event:",event)

  client = boto3.client('rds')

  if curr_region != event["ClusterRegion"]:
      print('\n Remove from Global Database operation should run from the same region. ClusterRegion =', event["ClusterRegion"],' and current region =',curr_region,'. Please check the payload and try again')
      raise RemoveGlobalDBFromDiffRegionIsNotAllowed

  try:
      response = client.remove_from_global_cluster(
                              GlobalClusterIdentifier=event["GlobalClusterIdentifier"],
                              DbClusterIdentifier=event["DBClusterIdentifier"]
                            )
      print("response = ", response)
      time.sleep(60)
      return {
          'statusCode' :200,
          'body' : json.dumps(response)
      }  
  except botocore.exceptions.ClientError as error:
      print(f"Error occurred while removing cluster from global database:", {error})
      raise error