# DR Orchestrator Framework Overview

The <b>DR Orchestrator Framework</b> automates the manual steps which are followed during the cross-region disaster recovery (DR) of your databases on AWS. It provides an approach with a centralized manifest-driven payload to trigger a single-click cross-region DR within the same account. The decision to perform a failover would still need human intervention and is out of scope for the automation.

With [disaster recovery strategy for databases on AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-database-disaster-recovery/welcome.html),  you could implement your DR solution for AWS databases in your organization. This solution can be automated by enabling event driven architecture which will perform the failover of the database instances. This approach has benefits like reducing  human errors due to manual coordination, providing the shortest possible RTO (recovery time objective) in some cases and facilitating repeatable testing of your DR solution.  Without automation, in the event of an outage in your primary AWS region, resources in your organization would need to manually execute steps in a run-book which include multiple processes like promoting Amazon RDS Read Replicas in the secondary AWS Region to serve as the new primary. AWS provides boto3 APIs to these actions which can form the building blocks of an automated solution for your organizations needs. 

Detailed documentation of <b>DR Orchestrator Framework</b> solution is available on [Automate your DR Solution for Databases on AWS](https://apg-library.amazonaws.com/content/d246ab63-9f04-4f98-b5ad-efa34d559323)  <Needs to be update this link>


## 1) Deploy DR Orchestrator Framework

<b>DR Orchestrator Framework </b> contains the resources like <i>AWS Step Functions</i> and <i>AWS Lambda Functions</i> which are needed to be deployed in order to Automate the Failover and Failback of AWS databases.

Follow the instructions mentioned below in order to deploy DR Orchestrator Framework:

Clone the git repository to your local directory

 ```bash 
git clone https://github.com/aws-samples/aws-cross-region-dr-databases.git
```

### Prerequisite

1. Create the archive files for Lambda Functions (e.g. lambda_function.zip or dependencies.zip) 
    - go to <b>../DR-Orchestration-artifacts</b> and run the below script to do so:-

      ```bash
      cd <YOUR-LOCAL-GIT-FOLDER>/DR-Orchestration-artifacts
      ```

      ```bash
      bash scripts/deploy-orchestrator-sh.sh
      ```

2. Create two S3 buckets in both Primary (us-east-1)as well in the Secondary (us-west-2) regions:
    - dr-orchestrator-xxxxxx-us-east-1
    - dr-orchestrator-xxxxxx-us-west-2

    Note: Replace xxxxxx with the unique name. Update <b>TemplateStoreS3BucketName</b> value accordingly in the parameter files. 

3. Create two subnets to hold Lambda Functions in your VPC in both Primary (us-east-1)as well in the Secondary (us-west-2) regions:
    - subnet-XXXXXXX
    - subnet-YYYYYYY

4. Create a Security Group in your VPC in both Primary (us-east-1)as well in the Secondary (us-west-2) regions:
    - sg-XXXXXXXXXXXX
 
5. Upload <b>DR-Orchestration-artifacts</b> directory including all files to S3 buckets in both regions.
6. Ensure that you are using subnet Ids, Security Group, vpcId from the same VPC where you have deployed AWS databases (RDS, Aurora and ElastiCache). Otherwise you have to add the Subnet Ids in the Interface Endpoints created the DR Orchestrator.
7. Ensure AWS database are available in the same AWS region

#### 1.1) Deploy DR Orchestrator resources in Primary Region (US-EAST-1)

- Modify <b>Orchestrator-Deployer-parameters-us-east-1.json</b> file and update the following parameters as per you VPC: 

  - TemplateStoreS3BucketName

- Go the <i>DR-Orchestration-artifacts/cloudformation</i> directory and run the below command:-

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/DR-Orchestration-artifacts/cloudformation
  ```

  ```bash
  aws cloudformation deploy --region us-east-1 --stack-name dr-orchestrator --template-file Orchestrator-Deployer.yaml --parameter-overrides file://Orchestrator-Deployer-parameters-us-east-1.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

#### 1.2) Deploy DR Orchestrator resources in Secondary Region (US-WEST-2)

<b>US-WEST-2 (Secondary region)</b>

- Modify <b>../Orchestrator-Deployer-parameters-us-west-2.json</b> file and update the following parameters as per you VPC: 

  - TemplateStoreS3BucketName

- Go the <i>../DR-Orchestration-artifacts/cloudformation</i> directory and run the below command:-

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/DR-Orchestration-artifacts/cloudformation
  ```

  ```bash
  aws cloudformation deploy --region us-west-2 --stack-name dr-orchestrator --template-file Orchestrator-Deployer.yaml --parameter-overrides file://Orchestrator-Deployer-parameters-us-west-2.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

## Testing 

### Test Case #1: Perform Switchover (managed planned failover) for Amazon Aurora global databases(MySQL)
By using switchover, you can change the Region of you primary cluster on a routine basis. This approach is intended for controlled scenarios, such as operational maintenance and other planned operational procedures. Refer https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html for more information. 

To test <b>Planned Switchover or Failover </b>, follow the steps given below:

- Go to the DR region (let's say, us-west-2)
- Start execution of <b>dr-orchestrator-stepfunction-FAILOVER</b> Step Function
- Use below payload as <b>Input</b>

```json
{
  "StatePayload": [
    {
      "layer": 1,
      "resources": [
        {
          "resourceType": "PlannedFailoverAurora",
          "resourceName": "Switchover (planned failover) of Amazon Aurora global databases (MySQL)",
          "parameters": {
            "GlobalClusterIdentifier": "!Import dr-globaldb-cluster-mysql-global-identifier",
            "DBClusterIdentifier": "!Import dr-globaldb-cluster-mysql-cluster-identifier" 
          }
        }
      ]
    }
  ]
}
```
<b>Note:</b> In case Amazon Aurora global database was not deployed using the <b>App-Stack</b> CFT. You can provide the <i>parameter's value</i> directly as mentioned below:

```json
{
  "StatePayload": [
    {
      "layer": 1,
      "resources": [
        {
          "resourceType": "PlannedFailoverAurora",
          "resourceName": "Switchover (planned failover) of Amazon Aurora global databases (MySQL)",
          "parameters": {
            "GlobalClusterIdentifier": "dr-globaldb-cluster-mysql",
            "DBClusterIdentifier": "arn:aws:rds:us-west-2:xxxxxxxxxxx:cluster:dbcluster-02"
          }
        }
      ]
    }
  ]
}
```

### Test Case #2: Perform manual unplanned failover ("detach and promote") for Amazon Aurora global databases(MySQL) - unplanned outage
On very rare occasions, your Aurora global database might experience an unexpected outage in its primary AWS Region. If this happens, your primary Aurora DB cluster and its writer node aren't available, and the replication between the primary and secondary DB clusters stops. Refer https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html for more information. 

To perform <b>Manual unplanned failover</b>, follow the steps given below:

- Go to the DR region (let's say, us-west-2)
- Start execution of <b>dr-orchestrator-stepfunction-FAILOVER</b> Step Function
- Use below payload as <b>Input</b>

```json
{
  "StatePayload": [
    {
      "layer": 1,
      "resources": [
        {
          "resourceType": "UnPlannedFailoverAurora",
          "resourceName": "Performing unplanned failover for Amazon Aurora global databases (MySQL)",
          "parameters": {
            "GlobalClusterIdentifier": "!Import dr-globaldb-cluster-mysql-global-identifier",
            "DBClusterIdentifier": "!Import dr-globaldb-cluster-mysql-cluster-identifier",
            "ClusterRegion": "!Import dr-globaldb-cluster-mysql-cluster-region"
          }
        }
      ]
    }
  ]
}
```

### Test Case #3: Perform Failback [Create Secondary cluser] for Amazon Aurora global databases(MySQL)
After the original topology is restored post an very rare unplanned outage. You may want to create the Secondary cluster back in the original primary region. 

To perform <b>Create Secondary cluser</b>, follow the steps given below:

- Go to the original Primary Region (let's say, us-east-1)
- Start execution of <b>dr-orchestrator-stepfunction-FAILBACK</b> Step Function
- Use below payload as <b>Input</b>

```json
{
  "StatePayload": [
    {
      "layer": 1,
      "resources": [
        {
          "resourceType": "CreateAuroraSecondaryDBCluster",
          "resourceName": "To create secondary Aurora MySQL Global Database Cluster",
          "parameters": {
            "GlobalClusterIdentifier": "!Import dr-globaldb-cluster-mysql-global-identifier",
            "DBClusterIdentifier": "!Import dr-globaldb-cluster-mysql-cluster-identifier",
            "DBClusterName": "!Import dr-globaldb-cluster-mysql-cluster-name",
            "SourceDBClusterIdentifier": "!Import dr-globaldb-cluster-mysql-source-cluster-identifier",
            "DBInstanceIdentifier": "!Import dr-globaldb-cluster-mysql-instance-identifier",
            "Port": "!Import dr-globaldb-cluster-mysql-port",
            "DBInstanceClass": "!Import dr-globaldb-cluster-mysql-instance-class",
            "DBSubnetGroupName": "!Import dr-globaldb-cluster-mysql-subnet-group-name",
            "VpcSecurityGroupIds": "!Import dr-globaldb-cluster-mysql-vps-security-group-ids",
            "Engine": "!Import dr-globaldb-cluster-mysql-engine",
            "EngineVersion": "!Import dr-globaldb-cluster-mysql-engine-version",
            "KmsKeyId": "!Import dr-globaldb-cluster-mysql-KmsKeyId",
            "SourceRegion": "!Import dr-globaldb-cluster-mysql-source-region",
            "ClusterRegion": "!Import dr-globaldb-cluster-mysql-cluster-region",
            "BackupRetentionPeriod": "7",
            "MonitoringInterval": "60",
            "StorageEncrypted": "True",
            "EnableIAMDatabaseAuthentication": "True",
            "DeletionProtection": "True",
            "CopyTagsToSnapshot": "True",
            "AutoMinorVersionUpgrade": "True",
            "MonitoringRoleArn": "!Import rds-mysql-instance-RDSMonitoringRole"
          }
        }
      ]
    }
  ]
}

```

Once the secondary cluster has created and if you want to fail back your global database to the original primary Region. You can perform a switchover operation when it makes the most sense for your business and workload, follow steps mentioned under <b>Test Case #1</b>


### Test Case #4: Perform cross-region failover for 1) Amazon RDS for MySQL Read Replica and 2) Amazon ElastiCache for Redis Cluster together

```json
{
  "StatePayload": [
    {
      "layer": 1,
      "resources": [
        {
          "resourceType": "PromoteRDSReadReplica",
          "resourceName": "Promote RDS for MySQL Read Replica",
          "parameters": {
            "RDSInstanceIdentifier": "!Import rds-mysql-instance-identifier",
            "TargetClusterIdentifier": "!Import rds-mysql-instance-global-arn"
          }
        },
        {
          "resourceType": "FailoverElastiCacheCluster",
          "resourceName": "Failover ElastiCache Cluster",
          "parameters": {
            "GlobalReplicationGroupId": "!Import demo-redis-cluster-global-replication-group-id",
            "TargetRegion": "!Import demo-redis-cluster-target-region",
            "TargetReplicationGroupId": "!Import demo-redis-cluster-target-replication-group-id"
          }
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Issue #1: Error while deploying DR Orchestrator
Resource handler returned message: "Error occurred while GetObject. S3 Error Code: NoSuchKey. S3 Error Message: The specified key does not exist. (Service: Lambda, Status Code: 400, Request ID: 3f96c885-ba1b-4453-96b9-a625d0a30221)" (RequestToken: a52bba65-ee8c-9488-cf6c-709717b9a279, HandlerErrorCode: InvalidRequest)

### Solution: Make sure you have followed all the steps mentioned in the Prerequisite section

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.