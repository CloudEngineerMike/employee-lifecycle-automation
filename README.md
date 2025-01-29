# OnBoarding Pipeline

![Image](https://github.com/user-attachments/assets/d81e9a59-be23-4d6a-a213-7fa2032ea010)

## Use Case & Solution

Your manager has just hired a new employee and you've been given the daunting task to onboard them!  
Onboarding (as you know it) takes priceless moments of your life, and there are so many other important tasks that you could be busy with. However, you recognize its importance in integrating new employees into a company.

The **OnBoarding Pipeline** is an automated onboarding solution! It not only gives you back your freedom, but also gives new hires the permissions they need to officially become a part of the team!  As a bonus, OnBoarding Pipeline can also assist with employee RBAC audits and offboarding as well. Read the section below to see how it works!

---

## How Does It Work?

The workflow will follow a series of steps:

### 1. Employment Verification
This function helps to verify if the request has all the fields that are needed in order to be processed.  
It verifies the following:
- If `SSO` field is present and has the correct length of characters
- If the `SSO` is valid and returns employee data
- If `action` field is present
- If `scope` field is present

If all goes well, the function will find and append the `employeeType` and `name` of the user to the response.  
This data will be used in the proceeding steps.

### 2. Action Type? (Choice State)
During this step, the choice state will read the response from the previous step and locate the `action` field.  
This action will either be `onboard`, `audit`, or `offboard`.  
Based on its value, it will be funneled to the appropriate function for delivering the request.

### 3. Onboard Function
Function to process all onboarding requests.

### 4. Audit Function
Function to process all auditing requests.

### 5. Offboard Function
Function to process all offboarding requests.

### 6. Succeed State
Your request has been processed successfully.

### 7. Fail State
Something is wrong with your request. See logs.

---

## Onboard

### Input:
```json
{
  "sso": "<SSO>",
  "action": "onboard",
  "scope": "<TEAM_NAME>"
}
```
