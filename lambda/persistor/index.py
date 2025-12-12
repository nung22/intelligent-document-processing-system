import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    logger.info("Starting Invoice Persistence...")
    
    try:
        for record in event['Records']:
            sns_message = record['Sns']['Message']
            logger.info(f"Received SNS Message: {sns_message}")
            
            invoice_data = json.loads(sns_message)
            
            # Convert float to Decimal for DynamoDB compatibility
            if 'total' in invoice_data:
                invoice_data['total'] = Decimal(str(invoice_data['total']))
            
            table.put_item(Item=invoice_data)
            
            logger.info(f"Successfully saved invoice {invoice_data.get('invoiceId')} to DynamoDB")

        return {
            'statusCode': 200,
            'body': json.dumps('Invoice data persisted successfully.')
        }

    except ClientError as e:
        logger.error(f"DynamoDB ClientError: {e}")
        raise e
    except Exception as e:
        logger.error(f"General Error: {e}")
        raise e