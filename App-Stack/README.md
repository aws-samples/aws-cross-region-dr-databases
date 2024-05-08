# Overview
The purpose of this document is set up sample AWS databases which would be used to demonstrate the capabilities of DR Orchestrator Framework

## Set up

Follow the instructions mentioned below in order to deploy AWS Databases (Amazon RDS MySQL, Amazon Aurora MySQL and Amazon ElastiCache Global Datastore for Redis)

Clone the git repository to your local directory

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
  aws cloudformation deploy \
  --region us-east-1 \
  --stack-name aurora-mysql-app-stack \
  --template-file Aurora-MySQL-Primary.yaml \
  --parameter-overrides file://Aurora-MySQL-parameter-us-east-1.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

#### 1.2) Deploy Aurora MySQL resources in Secondary Region (US-WEST-2)

- Modify <b>Aurora-MySQL-parameter-us-west-2.json</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> 
with the value of <b>AuroraKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation 

- Once the resource are created in the Primary Region. Run the below command to deploy the resources in the Secondary Region:

  ```bash
  aws cloudformation deploy \
  --region us-west-2 \
  --stack-name aurora-mysql-app-stack \
  --template-file Aurora-MySQL-DR.yaml \
  --parameter-overrides file://Aurora-MySQL-parameter-us-west-2.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

### 2) Create Amazon Aurora PostgreSQL Global Database
Deploy the resources using the <b>CloudFormation Template</b> from <b>AWS CLI</b>. Alternatively, you can use <b>AWS Console</b>. The Primary Region's resource should be created first (before the Secondary Region's resources).

#### 2.1) Deploy Aurora PostgreSQL resources in Primary Region (US-EAST-1)

- Go to the local directory where you have cloned the git repository

   ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with your <b>VPC settings</b> like <i>SubnetIds</i>, <i>DBSecurityGroup</i>, <i>GlobalClusterIdentifier</i>, <i>DBClusterName</i>, <i>InitialDatabaseName</i> etc.

  - Aurora-PostgreSQL-parameter-us-east-1.json
  - Aurora-PostgreSQL-parameter-us-west-2.json

- Run the below command:

  ```bash
  aws cloudformation deploy \
  --region us-east-1 \
  --stack-name aurora-postgres-app-stack \
  --template-file Aurora-PostgreSQL-Primary.yaml \
  --parameter-overrides file://Aurora-PostgreSQL-parameter-us-east-1.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

#### 2.2) Deploy Aurora PostgreSQL resources in Secondary Region (US-WEST-2)

- Modify <b>Aurora-PostgreSQL-parameter-us-west-2.json</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> 
with the value of <b>AuroraKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation 

- Once the resource are created in the Primary Region. Run the below command to deploy the resources in the Secondary Region:

  ```bash
  aws cloudformation deploy \
  --region us-west-2 \
  --stack-name aurora-postgres-app-stack \
  --template-file Aurora-PostgreSQL-DR.yaml \
  --parameter-overrides file://Aurora-PostgreSQL-parameter-us-west-2.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

### 3) Create Amazon RDS for MySQL DB Instance

#### 3.1) Deploy RDS MySQL resources in Primary Region (US-EAST-1)

- Go the directory where you have cloned the git repository.

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with the <b>VPC settings</b> like SubnetIds, DBSecurityGroup, MySqlGlobalIdentifier etc.
  
  - RDS-MySQL-parameter-us-east-1.json
  - RDS-MySQL-parameter-us-west-2.json

- Run the below command:

  ```bash
  aws cloudformation deploy \
  --region us-east-1 \
  --stack-name rds-mysql-app-stack \
  --template-file RDS-MySQL-Primary.yaml \
  --parameter-overrides file://RDS-MySQL-parameter-us-east-1.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

#### 3.2) Deploy RDS MySQL resources in Secondary Region (US-WEST-2)

- Once the resource are created in Primary Region. Run the below command to deploy the resources in Secondary Region:

- Modify <b>RDS-MySQL-parameter-us-west-2.json</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> with the value of <b>MySQLKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation. 

- Run the below command to create the RDS Read Replica in us-west-2 region:

  ```bash
  aws cloudformation deploy \
  --region us-west-2 \
  --stack-name rds-mysql-app-stack \
  --template-file RDS-MySQL-DR.yaml \
  --parameter-overrides file://RDS-MySQL-parameter-us-west-2.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```


### 4) Create ElastiCache Global Datastore

#### 4.1) Deploy ElastiCache resources in Primary Region (US-EAST-1)

- Go the <b>../App-Stack </b> directory where you have cloned the git repository.

  ```bash
  cd <YOUR-LOCAL-GIT-FOLDER>/App-Stack
  ```

- Modify the parameters files to match with the <b>VPC settings</b> like CacheNodeType, DBSecurityGroup, SubnetIds, EngineVersion, GlobalReplicationGroupIdSuffix, ReplicationGroupId

  - ElastiCache-parameter-us-east-1.json
  - ElastiCache-parameter-us-east-1.json

- Run the below command:

  ```bash
  aws cloudformation deploy \
  --region us-east-1 \
  --stack-name elasticache-ds-app-stack \
  --template-file ElastiCache-Primary.yaml \
  --parameter-overrides file://ElastiCache-parameter-us-east-1.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```

#### 4.2) Deploy ElastiCache resources in Secondary Region (US-WEST-2)

- Once the resource are created in Primary Region. Run the below command to deploy the resources in Secondary Region:

- Modify <b>ElastiCache-parameter-us-west-2</b> file and update the value of <b>PrimaryRegionKMSKeyArn</b> with the value of <b>ElastiCacheKmsKeyId</b> from the <b>Outputs</b> section of CloudFormation. 

- Run the below command to create the RDS Read Replica in us-west-2 region:

  ```bash
  aws cloudformation deploy \
  --region us-west-2 \
  --stack-name elasticache-ds-app-stack \
  --template-file ElastiCache-DR.yaml \
  --parameter-overrides file://ElastiCache-parameter-us-west-2.json \
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
  --disable-rollback
  ```


## Troubleshooting

### Issue #1: Error while deploying DR Orchestrator
Resource handler returned message: "Error occurred while GetObject. S3 Error Code: NoSuchKey. S3 Error Message: The specified key does not exist. (Service: Lambda, Status Code: 400, Request ID: 3f96c885-ba1b-4453-96b9-a625d0a30221)" (RequestToken: a52bba65-ee8c-9488-cf6c-709717b9a279, HandlerErrorCode: InvalidRequest)

### Solution: Make sure you have followed all the steps mentioned in the Prerequisite section

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.