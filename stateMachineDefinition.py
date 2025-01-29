state_machine_definition = {
    "Comment": "A description of my state machine",
    "StartAt": "Employment Verification",
    "States": {
        "Employment Verification": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
                "Payload.$": "$",
                "FunctionName": "INSERT-ARN"
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 1,
                    "MaxAttempts": 3,
                    "BackoffRate": 2
                }
            ],
            "Next": "Action Type?",
            "Comment": "This function helps to verify if the user in the request has a valid SSO or not. "
                       "If valid, it will then check if user is a current employee, ex-employee or contractor."
        },
        "Action Type?": {
            "Type": "Choice",
            "Choices": [
                {
                    "Variable": "$.action",
                    "StringMatches": "audit",
                    "Next": "Audit User"
                },
                {
                    "Variable": "$.action",
                    "StringMatches": "offboard",
                    "Next": "Offboard User"
                },
                {
                    "Variable": "$.action",
                    "StringMatches": "onboard",
                    "Next": "Onboard User"
                }
            ],
            "Default": "Fail",
            "Comment": "This choice state determines which action is tied to the request. "
                       "Based on the condition, it will send the request to the right function for processing."
        },
        "Onboard User": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
                "Payload.$": "$",
                "FunctionName": "INSERT-ARN"
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 1,
                    "MaxAttempts": 3,
                    "BackoffRate": 2
                }
            ],
            "Comment": "Function to process all onboarding requests.",
            "End": True
        },
        "Audit User": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
                "Payload.$": "$",
                "FunctionName": "INSERT-ARN"
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 1,
                    "MaxAttempts": 3,
                    "BackoffRate": 2
                }
            ],
            "Comment": "Function to process all auditing requests.",
            "End": True
        },
        "Offboard User": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
                "Payload.$": "$",
                "FunctionName": "INSERT-ARN"
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 1,
                    "MaxAttempts": 3,
                    "BackoffRate": 2
                }
            ],
            "Comment": "Function to process all offboarding requests.",
            "End": True
        },
        "Fail": {
            "Type": "Fail"
        }
    }
}

import json

# Pretty print the state machine JSON
print(json.dumps(state_machine_definition, indent=4))
