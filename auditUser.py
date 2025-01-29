import json
import requests
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    AWS Lambda function to audit and update user information in DynamoDB
    and make identity-related API requests.
    """

    # Secrets Manager | Pull API KEY
    def get_secret():
        secret_name = "<SECRET-NAME>"
        region_name = "us-east-1"
        
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        
        return get_secret_value_response['SecretString']

    # Find User in Database
    def find_dynamo_user():
        print("Checking DynamoDB for user...")
        client = boto3.client('dynamodb')
        
        response = client.get_item(
            TableName='<TABLE-NAME>',
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

    # Find Team(s) & User Groups
    def find_dynamo_team():
        print("Checking DynamoDB for user's team...")
        client = boto3.client('dynamodb')
        
        response = client.get_item(
            TableName='TABLE-NAME',
            Key={'team': {'S': event["scope"]}}
        )
        
        if "Item" in response:
            print("Found team in table.")
            groups = [item['S'] for item in response['Item']['groupNames']['L']]
            return groups
        else:
            print("Team not found. Exiting...")
            exit(1)
    
    # Update DynamoDB User
    def update_dynamo():
        print("Updating DynamoDB...")
        client = boto3.client('dynamodb')
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
        print("User action updated successfully.")

    # IDENTITY Request
    def IDENTITY_put_request(groupName, SSO):
        print(f"Querying <IDENTITY-TOOL> about {groupName}...")
        apikey = json.loads(get_secret())
        
        getUrl = f"<URL-ENDPOINT>?name={groupName}"
        response = requests.get(getUrl, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        
        IDENTITY_groupname_results = response.json()
        print(f"Sanity check for {groupName}:", IDENTITY_groupname_results["members"])
        
        appended_members_list = IDENTITY_groupname_results["members"] + [SSO]
        putUrl = f"API_ENDPOINT?name={groupName}"
        
         putBody={
            "groupId": IDENTITY_groupname_results["groupId"],
           ...
        }
        
        requests.put(putUrl, json=putBody, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        print(f"{SSO} has been added to {groupName}!")
    
    # Audit Activity
    def audit_processing(groupNames, SSO):
        print("You are now auditing...")
        apikey = json.loads(get_secret())
        
        getUrl = f"<URL-ENDPOINT>?sso={SSO}"
        resp = requests.get(getUrl, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        
        user_data = resp.json()
        current_user_groups = [x['groupName'] for x in user_data]
        
        missing_groups = set(groupNames) - set(current_user_groups)
        
        if not missing_groups:
            print(f"User {SSO} already has the needed distribution lists for: {event['scope']}.")
        else:
            print(f"User {SSO} is missing: {missing_groups}")
            for group in missing_groups:
                IDENTITY_put_request(group, SSO)
    
    # Sort Request
    def verifyRequest():
        if event['action'] == 'audit' and event['scope']:
            userTeam = find_dynamo_team()
            find_dynamo_user()
            audit_processing(userTeam, event["sso"])
            update_dynamo()
        else:
            print("Error: Incorrect action or missing scope.")
            exit(1)
    
    verifyRequest()
    
    return {'statusCode': 200, 'message': 'User audited successfully.'}
