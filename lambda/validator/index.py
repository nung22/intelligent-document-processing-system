import json
import boto3
import os
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
ALERTS_TOPIC_ARN = os.environ.get('ALERTS_TOPIC_ARN')
THRESHOLD = 1000.00

def lambda_handler(event, context):
    logger.info("Starting Invoice Validation...")
    
    try:
        for record in event['Records']:
            sns_message = record['Sns']['Message']
            invoice_data = json.loads(sns_message)
            
            total_amount = float(invoice_data.get('total', 0.0))
            invoice_id = invoice_data.get('invoiceId', 'Unknown')
            vendor = invoice_data.get('vendor', 'Unknown')
            
            logger.info(f"Validating Invoice {invoice_id}: Total ${total_amount}")
            
            if total_amount > THRESHOLD:
                logger.warning(f"HIGH VALUE INVOICE DETECTED: ${total_amount}")
                
                message_body = (
                    f"High Value Invoice Detected!\n\n"
                    f"Invoice ID: {invoice_id}\n"
                    f"Vendor: {vendor}\n"
                    f"Total: ${total_amount}\n\n"
                    f"Please review this invoice immediately."
                )
                
                sns.publish(
                    TopicArn=ALERTS_TOPIC_ARN,
                    Message=message_body,
                    Subject=f"Alert: High Invoice from {vendor}"
                )
                logger.info("Alert sent successfully.")
            else:
                logger.info("Invoice is within approved limits.")

        return {'statusCode': 200, 'body': 'Validation complete.'}

    except Exception as e:
        logger.error(f"Error validating invoice: {e}")
        raise e