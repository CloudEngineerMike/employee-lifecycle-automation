import json
import requests
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    AWS Lambda function to onboard users via DynamoDB and Identity Tool.
    """
    def get_secret():
        """Retrieve API key from AWS Secrets Manager."""
        secret_name = "SECRET-NAME"
        region_name = "us-east-1"

        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)

        try:
            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e

        return response['SecretString']

    def find_dynamo_user():
        """Find user in DynamoDB or create if not exists."""
        client = boto3.client('dynamodb')
        response = client.get_item(
            TableName='TABLE-NAME',
            Key={'sso': {'N': event["sso"]}}
        )

        if "Item" in response:
            print("Found user in table.")
        else:
            print("User not found. Creating item...")
            client.put_item(
                TableName='TABLE-NAME',
                Item={
                    'sso': {'N': event["sso"]},
                    'action': {'S': event["action"]},
                    'scope': {'L': [{'S': event["scope"]}]},
                    'employeeType': {'S': event["employeeType"]},
                    'name': {'S': event["name"]}
                }
            )
            print("User created successfully.")

    def find_dynamo_team():
        """Retrieve user team from DynamoDB."""
        print("Checking DynamoDB for user's team...")
        client = boto3.client('dynamodb')
        response = client.get_item(
            TableName='TABLE-NAME',
            Key={'team': {'S': event["scope"]}}
        )

        values = response['Item']['groupNames']['L']
        groups = [y for item in values for x, y in item.items()]
        return groups

    def identity_put_request(identity_group_name, sso):
        """Perform an Identity Tool PUT request."""
        print(f"Querying Identity Tool about {identity_group_name}...")
        apikey = json.loads(get_secret())

        get_url = f"<URL>?name={identity_group_name}"
        response = requests.get(get_url, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        identity_results = response.json()

        print(f"Sanity Check - Current members in {identity_group_name}: ", identity_results["members"])
        appended_members_list = identity_results["members"] + [sso]

        put_url = f"<URL>?name={identity_group_name}"
        put_body = {
            "identity_group_Id": identity_results["identity_group_Id"],
            ...
        }

        requests.put(put_url, json=put_body, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        print(f"User {sso} has been successfully onboarded to {identity_group_name}!")

    def verify_request():
        """Sort and process the request."""
        if event['action'] == 'onboard':
            if event['scope']:
                print("Checking DynamoDB for user...")
                find_dynamo_user()
                print("You are now onboarding...")
                user_teams = find_dynamo_team()
                for identity_group_name in user_teams:
                    identity_put_request(identity_group_name, event["sso"])
            else:
                print("Scope doesn't exist. Exiting.")
                exit(1)
        else:
            print("Error: Incorrect action.")
            exit(1)

    verify_request()
    return {'statusCode': 200, 'message': 'User onboarded successfully.'}
