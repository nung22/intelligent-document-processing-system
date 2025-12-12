import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { Construct } from 'constructs';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class IdpInfrastructureStack extends cdk.Stack {
  public readonly invoiceBucket: s3.Bucket;
  public readonly invoiceTable: dynamodb.Table;
  public readonly invoiceEventsTopic: sns.Topic;
  public readonly alertsTopic: sns.Topic;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for invoice uploads
    this.invoiceBucket = new s3.Bucket(this, 'InvoiceBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      cors: [{
        allowedMethods: [s3.HttpMethods.PUT, s3.HttpMethods.POST],
        allowedOrigins: ['*'],
        allowedHeaders: ['*'],
      }],
    });

    // DynamoDB Table for metadata persistence
    this.invoiceTable = new dynamodb.Table(this, 'InvoiceTable', {
      partitionKey: { name: 'invoiceId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // SNS Topic for fanout processing
    this.invoiceEventsTopic = new sns.Topic(this, 'InvoiceEventsTopic', {
      displayName: 'Invoice Processed Events',
    });

    // SNS Topic for high-value alerts
    this.alertsTopic = new sns.Topic(this, 'AlertsTopic', {
      displayName: 'High Value Invoice Alerts',
    });
    
    const email = process.env.NOTIFICATION_EMAIL;
    if (!email) throw new Error("Please set NOTIFICATION_EMAIL in your .env file");
    
    this.alertsTopic.addSubscription(new subscriptions.EmailSubscription(email));

    new cdk.CfnOutput(this, 'BucketName', { value: this.invoiceBucket.bucketName });
    new cdk.CfnOutput(this, 'TableName', { value: this.invoiceTable.tableName });
    new cdk.CfnOutput(this, 'TopicArn', { value: this.invoiceEventsTopic.topicArn });
    
    // Processor Lambda (Textract/Simulation)
    const processorFunction = new PythonFunction(this, 'ProcessorFunction', {
      entry: 'lambda/processor', 
      runtime: lambda.Runtime.PYTHON_3_12,
      index: 'index.py',
      handler: 'lambda_handler',
      timeout: cdk.Duration.seconds(30),
      environment: {
        TOPIC_ARN: this.invoiceEventsTopic.topicArn,
      },
    } as any);

    this.invoiceBucket.grantRead(processorFunction);
    this.invoiceEventsTopic.grantPublish(processorFunction);
    
    processorFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: ['textract:AnalyzeExpense'],
      resources: ['*'],
    }));

    this.invoiceBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(processorFunction)
    );

    // Persistor Lambda (DynamoDB Writer)
    const persistorFunction = new PythonFunction(this, 'PersistorFunction', {
      entry: 'lambda/persistor', 
      runtime: lambda.Runtime.PYTHON_3_12,
      index: 'index.py',
      handler: 'lambda_handler',
      timeout: cdk.Duration.seconds(10),
      environment: {
        TABLE_NAME: this.invoiceTable.tableName,
      },
    } as any);

    this.invoiceTable.grantWriteData(persistorFunction);
    this.invoiceEventsTopic.addSubscription(
      new subscriptions.LambdaSubscription(persistorFunction)
    );

    // Validator Lambda (Business Logic/Alerts)
    const validatorFunction = new PythonFunction(this, 'ValidatorFunction', {
      entry: 'lambda/validator', 
      runtime: lambda.Runtime.PYTHON_3_12,
      index: 'index.py',
      handler: 'lambda_handler',
      timeout: cdk.Duration.seconds(10), 
      environment: {
        ALERTS_TOPIC_ARN: this.alertsTopic.topicArn,
      },
    } as any);

    this.alertsTopic.grantPublish(validatorFunction);
    this.invoiceEventsTopic.addSubscription(
      new subscriptions.LambdaSubscription(validatorFunction)
    );

    // API Gateway Handler
    const apiFunction = new PythonFunction(this, 'ApiFunction', {
      entry: 'lambda/api',
      runtime: lambda.Runtime.PYTHON_3_12,
      index: 'index.py',
      handler: 'lambda_handler',
      environment: {
        TABLE_NAME: this.invoiceTable.tableName,
        BUCKET_NAME: this.invoiceBucket.bucketName,
      },
    });

    this.invoiceTable.grantReadData(apiFunction);
    this.invoiceBucket.grantPut(apiFunction);

    const api = new apigateway.LambdaRestApi(this, 'InvoiceApi', {
      handler: apiFunction,
      proxy: true,
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    new cdk.CfnOutput(this, 'ApiUrl', { 
      value: api.url,
      description: 'The URL for the frontend to fetch invoices',
    });
  }
}