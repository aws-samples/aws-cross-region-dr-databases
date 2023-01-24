import json
import boto3
import botocore
import os
from botocore.config import Config
from datetime import datetime

curr_session = boto3.session.Session()
curr_region = curr_session.region_name
now = datetime.now() # current date and time
curr_time = now.strftime("%Y%m%d%H%M%S%f")

class RDSInstanceIsNotStandAloneDB(Exception):
  def __str__(self):
    return "RDS Instane is NOT a stand-alon database!"    

class InRegionReadReplicaNotAllowed(Exception):
  def __str__(self):
    return "SourceRegion cannot be same as the current region (" + curr_region +"). Please check the payload and try again!"

def lambda_handler(event, context):
  print("Entering lambda_handler for dr-orchestrator-lambda-delete-stand-alone-rds-instance")
  print("curr_region = ", curr_region)
  print("event:",event)

  client = boto3.client('rds')

  #Check and stop if read replica is being created in the same region.   
  if curr_region == event["SourceRegion"]:
      print('\n SourceRegion =', event["SourceRegion"],' cannot be same as the current region =',curr_region,'. Please correct the SourceRegion and try again')
      raise InRegionReadReplicaNotAllowed
    
  #Check whether RDSInstanceIdentifier exist, if Yes, then proceed to next step. Otherwise exit with success.
  try:
    print(f"Check whether RDS Instance exist, if Yes, proceed to next step")
    response_rr = client.describe_db_instances(DBInstanceIdentifier = event["RDSInstanceIdentifier"])
  except client.exceptions.DBInstanceNotFoundFault as exp:
    print("Warning :: Target RDS Instance = [",event["RDSInstanceIdentifier"],"] does not exist")
    print("\n Details= " ,exp)
    return {
      'statusCode' :200,
      'body' : json.dumps('RDS Instance DOES NOT exist. Exiting with success!')
    }    
  else:
    print('describe_db_instances respons = ', response_rr)
    target_instance_status = response_rr["DBInstances"][0]["DBInstanceStatus"]
    print("target_instance_status=", target_instance_status)

    #Check whether RDSInstanceIdentifier exist as a standalone database, if Yes, then delete it. Otherwise, raise RDSInstanceIsNotStandAloneDB.
    print(f"Check whether RDS Instance Identifier exist as a standalone database, if Yes, then delete it else exit with error")
    resp_read_replica = response_rr["DBInstances"][0]
    print('\n resp_read_replica resonse = ',resp_read_replica)
    read_replica_ins = resp_read_replica['ReadReplicaDBInstanceIdentifiers']
    print('\n read_replica_ins =',read_replica_ins)
    
    #ReadReplicaSourceDBInstanceIdentifier contains the identifier of the source DB instance if this DB instance is a read replica for RDS MySQL
    #While ReadReplicaDBInstanceIdentifiers contains the identifier of the source DB instance if this DB instance is a read replica for RDS PostgreSQL

    if 'ReadReplicaSourceDBInstanceIdentifier' in resp_read_replica.keys():
      read_replica_src_ins = resp_read_replica['ReadReplicaSourceDBInstanceIdentifier']
      print('\n ReadReplicaSourceDBInstanceIdentifier exist.')
    else: 
      read_replica_src_ins = ''
      print('\n ReadReplicaSourceDBInstanceIdentifier does not exist.')
  
    print('\n read_replica_src_ins =',read_replica_src_ins)    

    #Check read_replica_ins and read_replica_src_ins are empty. 
    if len(read_replica_ins) > 0 or len(read_replica_src_ins)>0 :
      print(f"RDS Instance is NOT a stand-alone database. Existing...")
      raise RDSInstanceIsNotStandAloneDB
    else:
      print('RDS Instance is a stand-alone database. Proceeding to DELETE the instance.')

    #Check the RDS Instance before DELETING it. It should be in available state. 
    if target_instance_status == "available":
      print("deleting the target stand-alone rds instance = [", event["RDSInstanceIdentifier"],"]")
      FinalDBSnapshotIdentifier='backup-'+event["RDSInstanceIdentifier"]+curr_time
      print('\n FinalDBSnapshotIdentifier = ', FinalDBSnapshotIdentifier)

      try:
        delete_rsd_res = client.delete_db_instance(
            DBInstanceIdentifier= event["RDSInstanceIdentifier"],
            SkipFinalSnapshot=False,
            FinalDBSnapshotIdentifier=FinalDBSnapshotIdentifier,
            DeleteAutomatedBackups=False
          )
        print('\n delete_rsd_res=', delete_rsd_res)
        #To avoid TypeError: Object of type datetime is not JSON serializable
        exclude_keys = ['InstanceCreateTime','LatestRestorableTime']
        response_final = delete_rsd_res['DBInstance']
        [response_final.pop(key) for key in exclude_keys]      
        return {
          'statusCode' :200,
          'body' : json.dumps(response_final)
        }
      except botocore.exceptions.ClientError as error:
        print(f"Error occurred: {error}")
        raise error

    else:
      print(f"RDS Instance to be deleted is not in available state")
      return {
        'statusCode' :400,
        'status': json.dumps(target_instance_status),
        'body' : json.dumps('RDS Instance to be deleted is not in available state')
      }   