# Finding the Bug

## Enumerate your permissions

Start by checking what `dev-user` is allowed to do:

```bash
curl -s -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  http://localhost:8080/iam/get-user-policies | python3 -m json.tool
```

```json
{
  "UserName": "dev-user",
  "AttachedPolicies": {
    "DevUserPolicy": {
      "Version": "2012-10-17",
      "Statement": [
        {"Effect": "Allow", "Action": ["iam:ListRoles", "iam:GetRole"], "Resource": "*"},
        {"Effect": "Allow", "Action": "lambda:CreateFunction", "Resource": "*"},
        {"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": "*"},
        {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"},
        {"Effect": "Allow", "Action": "iam:PassRole",
         "Resource": "arn:aws:iam::123456789012:role/*"}
      ]
    }
  }
}
```

The key permissions are `lambda:CreateFunction`, `lambda:InvokeFunction`, and `iam:PassRole` scoped to `role/*`. That wildcard is the problem. `dev-user` can attach any role in the account to any Lambda function they create.

## List the available roles

Check which roles exist:

```bash
curl -s -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  http://localhost:8080/iam/list-roles | python3 -m json.tool
```

```json
{
  "Roles": [
    {
      "RoleName": "LambdaBasicExecutionRole",
      "Arn": "arn:aws:iam::123456789012:role/LambdaBasicExecutionRole",
      "Description": "Basic Lambda execution permissions: CloudWatch Logs only."
    },
    {
      "RoleName": "AdminRole",
      "Arn": "arn:aws:iam::123456789012:role/AdminRole",
      "Description": "Administrator access to all AWS services."
    }
  ]
}
```

`AdminRole` is the target. `dev-user` cannot assume this role directly. But `dev-user` can create a Lambda function with `AdminRole` as its execution role, and then invoke that function. The function runs as `AdminRole`.
