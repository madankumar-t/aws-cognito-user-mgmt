# IAM Roles and Trust Policies
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Lambda Execution Role

### 1.1 Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 1.2 Execution Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Sid": "STSAssumeRole",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CognitoManagementRole"
    },
    {
      "Sid": "CloudWatchMetrics",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "CognitoManagement"
        }
      }
    }
  ]
}
```

---

## 2. Cross-Account Role (CognitoManagementRole)

### 2.1 Trust Policy (in Target Accounts)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<LAMBDA_ACCOUNT_ID>:role/CognitoManagementLambdaRole"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<OPTIONAL_EXTERNAL_ID>"
        }
      }
    }
  ]
}
```

**Note**: Replace `<LAMBDA_ACCOUNT_ID>` with the AWS account ID where Lambda function is deployed.

### 2.2 Permissions Policy (in Target Accounts)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CognitoUserPoolRead",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:ListUserPools",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:ListUsers",
        "cognito-idp:AdminGetUser",
        "cognito-idp:ListUsersInGroup"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CognitoUserManagement",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminUpdateUserAttributes",
        "cognito-idp:AdminDeleteUser",
        "cognito-idp:AdminEnableUser",
        "cognito-idp:AdminDisableUser",
        "cognito-idp:AdminSetUserPassword",
        "cognito-idp:AdminResetUserPassword",
        "cognito-idp:AdminSetUserMFAPreference",
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminListGroupsForUser"
      ],
      "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
    }
  ]
}
```

### 2.3 Least Privilege Policy (Recommended)

For better security, restrict to specific User Pools:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CognitoUserPoolList",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:ListUserPools"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CognitoUserPoolRead",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:DescribeUserPool",
        "cognito-idp:ListUsers",
        "cognito-idp:AdminGetUser"
      ],
      "Resource": [
        "arn:aws:cognito-idp:us-east-1:*:userpool/us-east-1_ABC123",
        "arn:aws:cognito-idp:us-west-2:*:userpool/us-west-2_XYZ789"
      ]
    },
    {
      "Sid": "CognitoUserManagement",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminUpdateUserAttributes",
        "cognito-idp:AdminDeleteUser",
        "cognito-idp:AdminEnableUser",
        "cognito-idp:AdminDisableUser",
        "cognito-idp:AdminSetUserPassword",
        "cognito-idp:AdminResetUserPassword"
      ],
      "Resource": [
        "arn:aws:cognito-idp:us-east-1:*:userpool/us-east-1_ABC123",
        "arn:aws:cognito-idp:us-west-2:*:userpool/us-west-2_XYZ789"
      ]
    }
  ]
}
```

---

## 3. Developer Role (Read-Only)

### 3.1 Trust Policy (Same as Admin)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<LAMBDA_ACCOUNT_ID>:role/CognitoManagementLambdaRole"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 3.2 Read-Only Permissions Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CognitoReadOnly",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:ListUserPools",
        "cognito-idp:DescribeUserPool",
        "cognito-idp:ListUsers",
        "cognito-idp:AdminGetUser",
        "cognito-idp:ListUsersInGroup"
      ],
      "Resource": "*"
    }
  ]
}
```

**Note**: This role would be assumed based on user's application role (Developer vs Admin).

---

## 4. AWS SAM Template IAM Configuration

### 4.1 Lambda Execution Role

```yaml
# sam-template.yaml

Resources:
  CognitoManagementLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: CognitoManagementPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - sts:AssumeRole
                Resource: !Sub "arn:aws:iam::*:role/${AccountRoleName}"
              - Effect: Allow
                Action:
                  - cloudwatch:PutMetricData
                Resource: "*"
                Condition:
                  StringEquals:
                    cloudwatch:namespace: CognitoManagement

  CognitoManagementFunction:
    Type: AWS::Serverless::Function
    Properties:
      Role: !GetAtt CognitoManagementLambdaRole.Arn
      # ... other properties
```

---

## 5. Terraform IAM Configuration (Alternative)

### 5.1 Lambda Execution Role

```hcl
# iam.tf

resource "aws_iam_role" "lambda_execution" {
  name = "CognitoManagementLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_execution" {
  name = "CognitoManagementPolicy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = "arn:aws:iam::*:role/CognitoManagementRole"
      }
    ]
  })
}
```

### 5.2 Cross-Account Role (for Target Accounts)

```hcl
# cross_account_role.tf (deploy in each target account)

variable "lambda_account_id" {
  description = "AWS account ID where Lambda function is deployed"
  type        = string
}

resource "aws_iam_role" "cognito_management" {
  name = "CognitoManagementRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.lambda_account_id}:role/CognitoManagementLambdaRole"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "cognito_management" {
  name = "CognitoManagementPolicy"
  role = aws_iam_role.cognito_management.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cognito-idp:ListUserPools",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:ListUsers",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminUpdateUserAttributes",
          "cognito-idp:AdminDeleteUser",
          "cognito-idp:AdminEnableUser",
          "cognito-idp:AdminDisableUser",
          "cognito-idp:AdminSetUserPassword",
          "cognito-idp:AdminResetUserPassword"
        ]
        Resource = "*"
      }
    ]
  })
}
```

---

## 6. IAM Policy Best Practices

### 6.1 Least Privilege

- Grant minimum required permissions
- Use resource-specific ARNs when possible
- Avoid wildcards (`*`) in Resource field

### 6.2 Condition Keys

Add conditions for additional security:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CognitoManagementRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-external-id-per-account"
        },
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

### 6.3 Session Duration

Limit session duration in AssumeRole:

```python
# In STS service
response = sts_client.assume_role(
    RoleArn=role_arn,
    RoleSessionName=session_name,
    DurationSeconds=3600,  # 1 hour maximum
    ExternalId="optional-external-id"  # Additional security
)
```

---

## 7. Multi-Account Setup Guide

### 7.1 Setup Steps

1. **Deploy Lambda in Management Account**
   - Create Lambda execution role
   - Deploy Lambda function
   - Note the account ID

2. **Create Cross-Account Role in Each Target Account**
   - Use the Lambda account ID in trust policy
   - Attach Cognito permissions policy
   - Note the role name (default: `CognitoManagementRole`)

3. **Configure Account List**
   - Add account IDs to configuration
   - Update Lambda environment variables or Parameter Store

4. **Test Access**
   - Verify AssumeRole works
   - Test Cognito operations

### 7.2 Account Configuration

```python
# config.py

ACCOUNTS = {
    "123456789012": {
        "name": "Production",
        "regions": ["us-east-1", "us-west-2"],
        "role_name": "CognitoManagementRole"
    },
    "987654321098": {
        "name": "Development",
        "regions": ["us-east-1"],
        "role_name": "CognitoManagementRole"
    }
}
```

---

## 8. Security Considerations

### 8.1 External ID

Use External ID for additional security:

```json
{
  "Condition": {
    "StringEquals": {
      "sts:ExternalId": "unique-per-account-external-id"
    }
  }
}
```

### 8.2 MFA (Optional)

Require MFA for AssumeRole:

```json
{
  "Condition": {
    "BoolIfExists": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

### 8.3 IP Restrictions

Restrict AssumeRole to specific IPs:

```json
{
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": ["203.0.113.0/24"]
    }
  }
}
```

---

## 9. Policy Examples Summary

| Role | Purpose | Key Permissions |
|------|---------|----------------|
| Lambda Execution Role | Run Lambda function | STS AssumeRole, CloudWatch Logs |
| CognitoManagementRole (Admin) | Full Cognito access | All Cognito admin operations |
| CognitoManagementRole (Developer) | Read-only access | List/Get operations only |

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024

