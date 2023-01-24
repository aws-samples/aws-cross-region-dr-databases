import json
import boto3
import botocore
from botocore.config import Config
import os

class InRegionReadReplicaNotAllowed(Exception):
    def __str__(self):
        return "SourceRegion cannot be same as the current region (" + curr_region +"). Please check the payload and try again!"

print("Entering lambda_handler for dr-orchestrator-lambda-create-read-replica 1")
curr_session = boto3.session.Session()
curr_region = curr_session.region_name
#AccountId = boto3.client("sts").get_caller_identity()["Account"]

def lambda_handler(event, context):
    print("Entering lambda_handler for dr-orchestrator-lambda-create-read-replica")
    aws_account_id = context.invoked_function_arn.split(":")[4]
    print("curr_region = ", curr_region)
    print("AccountId = ", aws_account_id)
    print(f"event: {event}")           
    client = boto3.client('rds')

    #Check and stop if read replica is being created in the same region.   
    if curr_region == event["SourceRegion"]:
        print('\n SourceRegion =', event["SourceRegion"],' cannot be same as the current region =',curr_region,'. Please correct the SourceRegion in the payload and try again')
        raise InRegionReadReplicaNotAllowed            
        
    SourceRDSInstanceArn = f'arn:aws:rds:{event["SourceRegion"]}:{aws_account_id}:db:{event["SourceRDSInstanceIdentifier"]}'
    print('\n SourceRDSInstanceArn = ',SourceRDSInstanceArn)
    print("\n Creating the new RDS Read replica = ",event["RDSInstanceIdentifier"]," from SourceRDSInstanceIdentifier=",event["SourceRDSInstanceIdentifier"]," and SourceRegion=", event["SourceRegion"])

    try:
        response = client.create_db_instance_read_replica(
            DBInstanceIdentifier=event["RDSInstanceIdentifier"],
            SourceDBInstanceIdentifier=SourceRDSInstanceArn,
            DBInstanceClass=event["DBInstanceClass"],
            MultiAZ=bool(event["MultiAZ"]),
            PubliclyAccessible=False,
            DBSubnetGroupName=event["DBSubnetGroup"],
            VpcSecurityGroupIds=[
                event["DBSecurityGroup"],
            ],
            KmsKeyId=event["KmsKeyId"],
            SourceRegion=event["SourceRegion"],
            AutoMinorVersionUpgrade=bool(event["AutoMinorVersionUpgrade"]),
            Port=int(event["Port"]),
            CopyTagsToSnapshot=bool(event["CopyTagsToSnapshot"]),
            MonitoringInterval=int(event["MonitoringInterval"]),
            MonitoringRoleArn=event["MonitoringRoleArn"],
            EnableIAMDatabaseAuthentication=bool(event["EnableIAMDatabaseAuthentication"])
        )         

        print("create_db_instance_read_replica response = ", response)
        return {
            'statusCode' :200,
            'body' : json.dumps(response)
        }  
    except botocore.exceptions.ClientError as error:
        print(f"Error occurred while creating Read Replica:", {error})
        raise error