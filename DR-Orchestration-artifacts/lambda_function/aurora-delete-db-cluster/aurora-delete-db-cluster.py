import json
import boto3
import botocore
import os
from botocore.config import Config
from datetime import datetime
import time

curr_session = boto3.session.Session()
curr_region = curr_session.region_name

class AuroraGobalClusterContainsMultipleMembers(Exception):
  def __str__(self):
    return "RDS Instane is NOT a stand-alon database!"    

class InRegionReadReplicaNotAllowed(Exception):
  def __str__(self):
    return "'ClusterRegion is different from the current region. Please check the payload and try again!'"

def detach_cluster_from_global_db(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
  try:
      response = client.remove_from_global_cluster(
                              GlobalClusterIdentifier=GlobalClusterIdentifier,
                              DbClusterIdentifier=DBClusterIdentifier
                            )
      print("response = ", response)
      return {
          'statusCode' :200,
          'body' : json.dumps(response)
      }  
  except botocore.exceptions.ClientError as error:
      print(f"Error occurred while detaching db cluster from global database:", {error})
      raise error

def check_db_instance_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
      cluster = client.describe_db_instances(DBInstanceIdentifier = DBInstanceIdentifier)
      print("check_db_instance_status response=",cluster)
      return cluster["DBInstances"][0]["DBInstanceStatus"]
    except client.exceptions.DBClusterNotFoundFault as exp:
        return 'doesnotexist'
    except botocore.exceptions.ClientError as error:
        raise error

def delete_db_instance(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
        resp_delete_db_instance = client.delete_db_instance(
            DBInstanceIdentifier= DBInstanceIdentifier,
            SkipFinalSnapshot=False,
            DeleteAutomatedBackups=False
          )
        print("delete_db_instance response = ",resp_delete_db_instance)
    except botocore.exceptions.ClientError as error:
        raise error

def check_db_cluster_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
      cluster = client.describe_db_clusters(DBClusterIdentifier = DBClusterIdentifier)
      print("check_db_cluster_status response = ",cluster)
      return cluster["DBClusters"][0]["Status"]
    except client.exceptions.DBClusterNotFoundFault as exp:
        return 'doesnotexist'
    except botocore.exceptions.ClientError as error:
        raise error

def delete_db_cluster(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
        resp_delete_db_clsuter = client.delete_db_cluster(
                                    DBClusterIdentifier=DBClusterIdentifier,
                                    SkipFinalSnapshot=True
                                )
        print("delete_db_cluster response = ",resp_delete_db_clsuter)
    except botocore.exceptions.ClientError as error:
        raise error

def check_global_db_cluster_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
      cluster = client.describe_global_clusters(GlobalClusterIdentifier = GlobalClusterIdentifier)
      print("check_global_db_cluster_status response = ",cluster)
      return cluster["GlobalClusters"][0]["Status"]
    except client.exceptions.GlobalClusterNotFoundFault as exp:
        return 'doesnotexist'
    except botocore.exceptions.ClientError as error:
        raise error
        
def delete_global_db_cluster(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client):
    try:
        resonse = client.delete_global_cluster(
                                    GlobalClusterIdentifier=GlobalClusterIdentifier
                                )
        print("delete_global_db_cluster response = ",resonse)
    except botocore.exceptions.ClientError as error:
        raise error

def lambda_handler(event, context):
  print("Entering lambda_handler for dr-orchestrator-lambda-delete-aurora-db-cluster")
  print("curr_region = ", curr_region)
  print("event:",event)

  GlobalClusterIdentifier = event["GlobalClusterIdentifier"]
  DBClusterIdentifier     = event["DBClusterIdentifier"]
  DBInstanceIdentifier    = event["DBInstanceIdentifier"]
  ClusterRegion           = event["ClusterRegion"]
  SourceRegion            = event["SourceRegion"]

  client = boto3.client('rds')

  # Aurora cluster DB Cluster should be delete from the same region. 
  if curr_region != ClusterRegion:
    print("\n Aurora DB Cluster should be deleted from the same region where it exists, current region = ",curr_region,". Please correct the payload and try again")
    raise InRegionReadReplicaNotAllowed

  else:  
    # Step #1 out of 4: Detach DB Cluster from Global Database 
    db_cluster_status = check_db_cluster_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
    if db_cluster_status == "available": 
        detach_db_cluster_status =  detach_cluster_from_global_db(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
        time.sleep(15)
    else:
        print("\n\n ******Skippinng Delete DB Cluster\n")

    # Step #2 out of 4: DELETE DB Instance after DELETE DB Cluster
    db_instance_status = check_db_instance_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
    if db_instance_status == "available":    
        print("\n\n ******Deleting DB Instance\n")
        delete_db_instance(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
        
    # Step #3 out of 4: DELETE DB Cluster immediately after DELETE INSTANCE
        print("\n\n ******Deleting DB Cluster\n")
        delete_db_cluster(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)        
    else:
        print("\n\n ******Skippinng Delete DB Instance\n")

    ## Step #4 out of 4: DELETE Global DB Cluster
    global_cluster_status = check_global_db_cluster_status(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
    if global_cluster_status == "available":    
        print("\n\n ******Deleting Global Database Cluster\n")
        delete_global_db_cluster(GlobalClusterIdentifier,DBClusterIdentifier,DBInstanceIdentifier,ClusterRegion,SourceRegion,client)
        time.sleep(15)
    else:
        print("\n\n ******Skippinng Delete Global DB Cluster\n")