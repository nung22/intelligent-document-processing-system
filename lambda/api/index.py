import json
import boto3
import os
import logging
import uuid
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = os.environ.get('TABLE_NAME')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
table = dynamodb.Table(TABLE_NAME)

class DecimalEncoder(json.JSONEncoder):
    """Helper to convert DynamoDB Decimals to floats."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def response(status, body):
    """Generates CORS-enabled response."""
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def lambda_handler(event, context):
    logger.info(f"API Request: {event.get('path')} {event.get('httpMethod')}")
    
    try:
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        
        # Route: Get Pre-signed Upload URL
        if path == '/upload-url' and http_method == 'GET':
            query_params = event.get('queryStringParameters', {}) or {}
            file_name = query_params.get('filename')
            content_type = query_params.get('contentType', 'image/jpeg') 
            
            if not file_name:
                return response(400, {'error': 'filename parameter is required'})
            
            unique_name = f"{uuid.uuid4()}-{file_name}"
            
            presigned_url = s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': BUCKET_NAME, 
                    'Key': unique_name, 
                    'ContentType': content_type
                },
                ExpiresIn=300
            )
            
            return response(200, {'uploadUrl': presigned_url, 'key': unique_name})

        # Route: List Invoices
        else:
            scan_response = table.scan()
            items = scan_response.get('Items', [])
            return response(200, items)

    except Exception as e:
        logger.error(f"API Error: {e}", exc_info=True)
        return response(500, {'error': str(e)})