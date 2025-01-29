import json
import requests
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    ########################
    ### Secrets Manager ####
    ########################
    def get_secret():
        secret_name = "<SECRET-NAME>"
        region_name = "us-east-1"
        
        session = boto3.session.Session()
        client = session.client("secretsmanager", region_name=region_name)
        
        try:
            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        
        return response['SecretString']
    
    ########################
    ### Find Dynamo User ###
    ########################
    def find_dynamo_user():
        print("Checking DynamoDB for user...")
        
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
    
    ##################################
    ### Find Team(s) & User Groups ###
    ##################################
    def find_dynamo_team():
        print("Checking DynamoDB for user's team...")
        
        client = boto3.client('dynamodb')
        response = client.get_item(
            TableName='TABLE-NAME',
            Key={'team': {'S': event["scope"]}}
        )
        
        if "Item" in response:
            print("Found team in table.")
            values = response['Item']['groupNames']['L']
            return [item['S'] for item in values]
        else:
            print("Team not found. Exiting...")
            exit(1)
    
    ##########################
    ### Update Dynamo User ###
    ##########################
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
    
    ###################
    ### Remove User ###
    ###################
    def identity_put_request(groupName, sso):
        print(f"Querying Identity Tool about {groupName}...")
        
        apikey = json.loads(get_secret())
        getUrl = f"<URL-ENDPOINT>?name={groupName}"
        
        resp = requests.get(getUrl, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        IDENTITY_groupname_results = resp.json()
        members_list = IDENTITY_groupname_results["members"]
        members_list.remove(sso)
        
        print(f"Running a Sanity Check: {members_list}")
        
        putUrl = f"<URL-ENDPOINT>?name={groupName}"
        putBody = {**IDENTITY_groupname_results, "members": members_list}
        
        requests.put(putUrl, json=putBody, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        print(f"User {sso} has been successfully offboarded from {groupName}!")
    
    ##########################
    ### Lookup Memberships ###
    ##########################
    def lookup_memberships(sso):
        print("User is now offboarding from all associated groups...")
        
        apikey = json.loads(get_secret())
        getUrl = f"<URL>?sso={sso}"
        
        resp = requests.get(getUrl, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        groups = [item['groupName'] for item in resp.json()]
        
        for group in groups:
            identity_put_request(group, sso)
    
    #############################
    ### Team Deletion Process ###
    #############################
    def team_deletion_process(groupNames, SSO):
        print("User is now offboarding from all associated groups...")
        
        apikey = json.loads(get_secret())
        getUrl = f"<URL>?sso={SSO}"
        
        resp = requests.get(getUrl, headers={'x-api-key': apikey['APIKEY'], 'Content-Type': 'application/json'})
        current_groups = [x['groupName'] for x in resp.json()]
        groups_to_remove = [g for g in groupNames if g in current_groups]
        
        print(f"User {SSO} needs removal from: {groups_to_remove}")
        for group in groups_to_remove:
            identity_put_request(group, SSO)
    
    ####################
    ### Sort Request ###
    ####################
    def verify_request():
        if event['action'] == 'offboard':
            find_dynamo_user()
            
            if event['scope'] == 'all':
                print("Started offboarding from ALL user groups...")
                lookup_memberships(event["sso"])
            else:
                print("Started offboarding from TEAM user groups...")
                userTeam = find_dynamo_team()
                team_deletion_process(userTeam, event["sso"])
            
            update_dynamo()
        else:
            print("Error: Incorrect action.")
            exit(1)
    
    verify_request()
    
    return {
        'statusCode': 200,
        'message': 'User offboarded successfully.'
    }
