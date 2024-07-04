import json
import boto3
import base64

s3_client = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'

def lambda_handler(event, context):
    try:
        # Log the event for debugging purposes
        print("Received event:", json.dumps(event))
        
        # Check if the body is base64 encoded
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode('utf-8')
        print("Body length:", len(body))
        
        # Parse the content type
        content_type = event['headers'].get('Content-Type', 'application/octet-stream')
        print("Content type:", content_type)
        
        # Extract the file name from the query string parameters
        key = event['queryStringParameters']['file_name']
        print("File name:", key)
        
        # Upload the file to S3
        response = s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType=content_type
        )
        print("S3 Response:", response)
        
        # Generate the presigned URL for the uploaded file
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=604800  # URL valid for 7 days (maximum allowed)
        )
        print("Presigned URL:", presigned_url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, x-api-key',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'message': 'File uploaded successfully', 'file_url': presigned_url})
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, x-api-key',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'message': 'File upload failed', 'error': str(e)})
        }

