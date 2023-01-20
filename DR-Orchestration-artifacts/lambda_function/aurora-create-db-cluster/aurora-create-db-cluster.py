import json
import boto3
import botocore
from botocore.config import Config
import os

curr_session = boto3.session.Session()
curr_region = curr_session.region_name


def lambda_handler(event, context):
    print("Entering lambda_handler for dr-orchestrator-lambda-create-aurora-db-cluster")
    print("curr_region = ", curr_region)
    print(f"event: {event}")
    aws_account_id = context.invoked_function_arn.split(":")[4]
    client = boto3.client('rds')

    # Step #1 out of 3: Create Aurora Global Database 
    print("\n Step #1 of #3, Creating Aurora Global Database = ",event["GlobalClusterIdentifier"]," in SourceRegion=",event["SourceRegion"])
    client_global_db = boto3.client('rds',region_name = event["SourceRegion"])
    try:
        response = client.create_global_cluster(
        GlobalClusterIdentifier=event["GlobalClusterIdentifier"],
        SourceDBClusterIdentifier=event["SourceDBClusterIdentifier"]
        )    
    except botocore.exceptions.ClientError as error:
        print(f"Error occurred while creating Aurora Global Database", {error})
        raise error

    # Step #2 out of 3: Create Aurora Database Cluster
    print("\n Step #2 of #3, Creating Aurora DB Cluster = ",event["DBClusterName"],"in current region = ",curr_region," from SourceRegion=",event["SourceRegion"])
    try:
        response = client.create_db_cluster(
            DBClusterIdentifier=event["DBClusterName"],
            DBSubnetGroupName=event["DBSubnetGroupName"],
            VpcSecurityGroupIds=[event["VpcSecurityGroupIds"]],
            Engine=event["Engine"],
            EngineVersion=event["EngineVersion"],
            GlobalClusterIdentifier=event["GlobalClusterIdentifier"],
            SourceRegion=event["SourceRegion"],
            KmsKeyId=event["KmsKeyId"],
            StorageEncrypted=bool(event["StorageEncrypted"]),
            EnableIAMDatabaseAuthentication=bool(event["EnableIAMDatabaseAuthentication"]),
            DeletionProtection=bool(event["DeletionProtection"]),
            BackupRetentionPeriod=int(event["BackupRetentionPeriod"]),
            CopyTagsToSnapshot=bool(event["CopyTagsToSnapshot"]),
            Port=int(event["Port"])
        )
        print("response create_db_cluster = ",response)
        #To avoid TypeError: Object of type datetime is not JSON serializable
        exclude_keys = ['ClusterCreateTime']
        response_final = response['DBCluster']
        [response_final.pop(key) for key in exclude_keys]
        print("response response_final = ",response_final)

    except botocore.exceptions.ClientError as error:
        print(f"Error occurred while creating Aurora db cluster", {error})
        raise error

    # Step #3 out of 3: Create Aurora DB Instance Instance after running DB Cluster gets created
    print("\n Step #3 of #3, creating Aurora DB Instance = ",event["DBInstanceIdentifier"]," under DBClusterName = ",event["DBClusterName"])
    try:
        response = client.create_db_instance(
            DBInstanceIdentifier=event["DBInstanceIdentifier"],
            DBInstanceClass=event["DBInstanceClass"],
            Engine=event["Engine"],
            DBClusterIdentifier=event["DBClusterName"],
            MonitoringInterval=int(event["MonitoringInterval"]),
            MonitoringRoleArn= event["MonitoringRoleArn"],
            AutoMinorVersionUpgrade=bool(event["AutoMinorVersionUpgrade"])
        )

        print("response create_db_instance = ",response)
        return {
            'statusCode' :200,
            'body' : 'global database, db cluster and db2 instance created'
        }
    except botocore.exceptions.ClientError as error:
        print(f"Error occurred while creating DB Instance", {error})
        raise error