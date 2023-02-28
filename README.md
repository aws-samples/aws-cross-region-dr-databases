## Automate Cross Region DR Solution for AWS Databases (Amazon RDS, Amazon Aurora and Amazon ElastiCache)

This solution includes the CloudFormation templates and shell script to deploy AWS databases and DR Orchestrator Framework. This document will describe how to use this solution. 

Detailed documentation of this solution is published as a <i> AWS Prescriptive Guidance Library</i> guide and available on https://apg-library.amazonaws.com/content-viewer/author/d246ab63-9f04-4f98-b5ad-efa34d559323  <Need to update the link>


## Set up

Follow the instructions mentioned below in order to deploy AWS Databases (Amazon RDS MySQL, Amazon Aurora MySQL and Amazon ElastiCache Global Datastore for Redis)

In order to create the application resource. First, clone the git repository to your local directory

 ```bash 
git clone https://github.com/aws-samples/aws-cross-region-dr-databases.git
```

### Prerequisite

1. Create <b>rds-monitoring-role</b> IAM role, if it does not already exist. Follow the instructions https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.Enabling.html#USER_Monitoring.OS.Enabling.Prerequisites.creating-role-manually  
    
2. Make sure <b>SubnetIds</b> and <b>DBSecurityGroup</b> have been created for RDS/Aurora. 

3. In this solution, <b>US-EAST-1</b> is being used as the <b>Primary Region</b> and <b>US-WEST-2</b> as the <b>Secondary Region</b>. But, you can modify the parameters files as per your DR requirements. Make sure that the AWS Services are supported on those regions.

4. Make sure subnet Ids, security group and vpcId belongs to the same VPC.

5. Port number used for Amazon Aurora, Amazon RDS, and Amazon ElastiCache have been randomized to 3787, 3788 and 3789 respectively. You can change it as per your requirements. 

### 1) Create Amazon Aurora MySQL Global Database
Deploy the resources using the <b>CloudFormation Template</b> from <b>AWS CLI</b>. Alternatively, you can use <b>AWS Console</b>. The Primary Region's resource should be created first (before the Secondary Region's resources).

#### 1.1) Deploy Aurora MySQL resources in Primary Region (US-EAST-1)

- Go to the local directory where you have cloned the git repository

   ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with your <b>VPC settings</b> like <i>SubnetIds</i>, <i>DBSecurityGroup</i>, <i>GlobalClusterIdentifier</i>, <i>DBClusterName</i>, <i>InitialDatabaseName</i> etc.

  - Aurora-MySQL-parameter-us-east-1.json
  - Aurora-MySQL-parameter-us-west-2.json

- Run the below command:

  ```bash
  aws cloudformation deploy --region us-east-1 --stack-name aurora-mysql-app-stack --template-file Aurora-MySQL-Primary.yaml --parameter-overrides file://Aurora-MySQL-parameter-us-east-1.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

#### 1.2) Deploy Aurora MySQL resources in Secondary Region (US-WEST-2)

- Modify <b>Aurora-MySQL-parameter-us-west-2.json</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> 
with the value of <b>AuroraKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation 

- Once the resource are created in the Primary Region. Run the below command to deploy the resources in the Secondary Region:

  ```bash
  aws cloudformation deploy --region us-west-2 --stack-name aurora-mysql-app-stack --template-file Aurora-MySQL-DR.yaml --parameter-overrides file://Aurora-MySQL-parameter-us-west-2.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

### 2) Create Amazon RDS for MySQL DB Instance

#### 2.1) Deploy RDS MySQL resources in Primary Region (US-EAST-1)

- Go the directory where you have cloned the git repository.

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with the <b>VPC settings</b> like SubnetIds, DBSecurityGroup, MySqlGlobalIdentifier etc.
  
  - RDS-MySQL-parameter-us-east-1.json
  - RDS-MySQL-parameter-us-west-2.json

- Run the below command:

  ```bash
  aws cloudformation deploy --region us-east-1 --stack-name rds-mysql-app-stack --template-file RDS-MySQL-Primary.yaml --parameter-overrides file://RDS-MySQL-parameter-us-east-1.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

#### 2.2) Deploy RDS MySQL resources in Secondary Region (US-WEST-2)

- Once the resource are created in Primary Region. Run the below command to deploy the resources in Secondary Region:

- Modify <b>RDS-MySQL-parameter-us-west-2.json</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> with the value of <b>MySQLKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation. 

- Run the below command to create the RDS Read Replica in us-west-2 region:

  ```bash
  aws cloudformation deploy --region us-west-2 --stack-name rds-mysql-app-stack --template-file RDS-MySQL-DR.yaml --parameter-overrides file://RDS-MySQL-parameter-us-west-2.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```


### 3) Create ElastiCache Global Datastore

#### 3.1) Deploy ElastiCache resources in Primary Region (US-EAST-1)

- Go the <b>../App-Stack </b> directory where you have cloned the git repository.

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with the <b>VPC settings</b> like CacheNodeType, DBSecurityGroup, SubnetIds, EngineVersion, GlobalReplicationGroupIdSuffix, ReplicationGroupId

  - ElastiCache-parameter-us-east-1.json
  - ElastiCache-parameter-us-east-1.json

- Run the below command:

  ```bash
  aws cloudformation deploy --region us-east-1 --stack-name elasticache-ds-app-stack --template-file ElastiCache-Primary.yaml --parameter-overrides file://ElastiCache-parameter-us-east-1.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

#### 3.2) Deploy ElastiCache resources in Secondary Region (US-WEST-2)

- Once the resource are created in Primary Region. Run the below command to deploy the resources in Secondary Region:

- Modify <b>ElastiCache-parameter-us-west-2</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> with the value of <b>ElastiCacheKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation. 

- Run the below command to create the RDS Read Replica in us-west-2 region:

  ```bash
  aws cloudformation deploy --region us-west-2 --stack-name elasticache-ds-app-stack --template-file ElastiCache-DR.yaml --parameter-overrides file://ElastiCache-parameter-us-west-2.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```


### 4) Deploy DR Orchestrator Framework
<b>DR Orchestrator Framework </b> contains the resources like <i>AWS Step Functions</i> and <i>AWS Lambda Functions</i> which are needed to be deployed in order to Automate the Failover and Fallback of AWS databases. Follow the steps mentioned below to deploy the DR Orchestrator Framework:

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

3. Upload <b>DR-Orchestration-artifacts</b> directory inlcluding all filex to S3 buckets in both regions.
4. Ensure that you are using subnet Ids, Security Group, vpcId from the same VPC where you have deployed AWS databases (RDS, Aurora and ElastiCache). Otherwise you have to add the Subnet Ids in the Interface Endpoints created the DR Orchestrator.

#### 4.1) Deploy DR Orchestrator resources in Primary Region (US-EAST-1)

- Modify <b>Orchestrator-Deployer-parameters-us-east-1.json</b> file and update the following parameters as per you VPC: 

  - TemplateStoreS3BucketName

- Go the <i>DR-Orchestration-artifacts/cloudformation</i> directory and run the below command:-

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/DR-Orchestration-artifacts/cloudformation
  ```

  ```bash
  aws cloudformation deploy --region us-east-1 --stack-name dr-orchestrator --template-file Orchestrator-Deployer.yaml --parameter-overrides file://Orchestrator-Deployer-parameters-us-east-1.json --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM --disable-rollback
  ```

#### 4.2) Deploy DR Orchestrator resources in Secondary Region (US-WEST-2)

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

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.