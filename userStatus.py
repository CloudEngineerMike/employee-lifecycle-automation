import json
import requests
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    AWS Lambda function to retrieve employment data based on SSO input,
    utilizing AWS Secrets Manager for API key management.
    """
    
    # Function to retrieve API key from AWS Secrets Manager
    def get_secret():
        secret_name = "<SECRET_NAME>"
        region_name = "REGION"
        
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        
        return get_secret_value_response['SecretString']
    
    # Function to fetch employment data
    def employment_data():
        apikey = json.loads(get_secret())
        url = f"<URL_ENDPOINT>?sso={event['sso']}"
        response = requests.get(url, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        return response.json()
    
    # Validate input and process request
    if 'sso' in event:
        if len(event['sso']) == 9:
            if 'action' in event:
                if 'scope' in event:
                    resp = employment_data()
                    
                    if 'employeeType' in resp:
                        response = {
                            'statusCode': 200,
                            'sso': event['sso'],
                            'action': event['action'],
                            'scope': event['scope'],
                            'employeeType': resp['employeeType'],
                            'name': resp.get('cn', 'Unknown')
                        }
                    else:
                        response = {
                            'statusCode': 400,
                            'message': 'Invalid SSO. Does not exist.',
                            'employeeType': None
                        }
                else:
                    response = {'statusCode': 400, 'message': 'Error: Key for scope is missing.'}
            else:
                response = {'statusCode': 400, 'message': 'Error: Key for action is missing.'}
        else:
            response = {'statusCode': 400, 'message': 'Invalid SSO: Must be 9 characters.'}
    else:
        response = {'statusCode': 400, 'message': 'Error: Key for sso is missing.'}
    
    return response
