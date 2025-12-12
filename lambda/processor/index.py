import json
import boto3
import os
import logging
import random
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# textract = boto3.client('textract') # Comment out if Textract subscription is not activated
sns = boto3.client('sns')
TOPIC_ARN = os.environ.get('TOPIC_ARN')


def lambda_handler(event, context):
    logger.info("Starting Invoice Processing (SIMULATION MODE)...")

    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        logger.info(
            f"Processing file: {object_key} from bucket: {bucket_name}")

        # # --- IMPLEMENTATION BLOCK START (Textract MUST be active) ---
        # # 2. Call Amazon Textract (Real API Call)
        # # We use 'analyze_expense' which is specialized for invoices
        # response = textract.analyze_expense(
        #     Document={
        #         'S3Object': {
        #             'Bucket': bucket_name,
        #             'Name': object_key
        #         }
        #     }
        # )

        # # 3. Parse the Textract Response
        # # We use a helper function to dig through the complex JSON response
        # extracted_data = parse_textract_response(response)
        # # --- IMPLEMENTATION BLOCK END ---

        # --- SIMULATION BLOCK START ---
        logger.warning(
            "Textract subscription missing. Generating simulated data.")

        # Simulating Textract analysis for demonstration purposes
        if 'high' in object_key.lower():
            simulated_total = 1500.00
            simulated_vendor = "Luxury Corp (Simulated)"
        elif 'low' in object_key.lower():
            simulated_total = 50.00
            simulated_vendor = "Cheap Mart (Simulated)"
        else:
            simulated_total = round(random.uniform(10.0, 1200.0), 2)
            simulated_vendor = "Random Vendor Inc."

        extracted_data = {
            'vendor': simulated_vendor,
            'total': simulated_total
        }
        # --- SIMULATION BLOCK END ---

        # Add metadata
        extracted_data['invoiceId'] = object_key
        extracted_data['bucket'] = bucket_name

        logger.info(f"Extracted Data: {json.dumps(extracted_data)}")

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(extracted_data),
            Subject='Invoice Processed'
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Invoice processed and event published.')
        }
    except ClientError as e:
        logger.error(f"AWS ClientError: {e}")
        raise e
    except Exception as e:
        logger.error(f"General Error: {e}")
        raise e


def parse_textract_response(response):
    """
    Parses the AnalyzeExpense response to find the VENDOR_NAME and TOTAL.
    """
    vendor_name = "Unknown Vendor"
    total_amount = 0.0

    for doc in response.get('ExpenseDocuments', []):
        for field in doc.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text')
            field_value = field.get('ValueDetection', {}).get('Text')

            if field_type == 'VENDOR_NAME':
                vendor_name = field_value

            elif field_type == 'TOTAL':
                try:
                    clean_value = field_value.replace(
                        '$', '').replace(',', '').strip()
                    total_amount = float(clean_value)
                except ValueError:
                    logger.warning(
                        f"Could not parse total amount: {field_value}")

    return {
        'vendor': vendor_name,
        'total': total_amount
    }
