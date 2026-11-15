# Defense

## Scope iam:PassRole to specific roles

The root cause is `iam:PassRole` with `Resource: *`. Replace the wildcard with the specific roles a user legitimately needs to attach to their functions:

```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": [
    "arn:aws:iam::123456789012:role/LambdaBasicExecutionRole"
  ]
}
```

With this policy, `dev-user` can only attach `LambdaBasicExecutionRole` to new functions. `AdminRole` is out of reach.

## Add a permission boundary

For users who need to deploy Lambda functions, add a **permission boundary**: a policy that caps the maximum permissions any resource they create can have. Even if `dev-user` somehow passes a high-privilege role, the boundary prevents the function from exceeding the developer's own permissions.

```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "iam:PassedToService": "lambda.amazonaws.com"
    },
    "ArnLike": {
      "iam:AssociatedResourceArn": "arn:aws:lambda:*:123456789012:function:dev-*"
    }
  }
}
```

## Audit with IAM Access Analyzer

AWS IAM Access Analyzer flags policies that allow privilege escalation. Run it against your account and review any finding that involves `iam:PassRole` with a wildcard resource.

The output of a scan on the vulnerable policy would include:

```
Finding: PassRole with wildcard resource
Policy: DevUserPolicy
Statement: PassRole -> Resource: *
Risk: User can escalate to any role in the account via Lambda, EC2, ECS, or similar services
Remediation: Replace * with specific role ARNs
```

## Detect exploitation in CloudTrail

An exploitation attempt leaves a clear trail:

```
CreateFunction . User: dev-user, role: AdminRole
InvokeFunction . User: dev-user, function: privesc-function
GetObject      . Principal: AdminRole, bucket: secret-bucket
```

The `GetObject` call comes from `AdminRole`, but the `CreateFunction` that set it up came from `dev-user`. Correlate `CreateFunction` events that attach high-privilege roles with subsequent `GetObject` calls from those roles.

A CloudWatch alarm on `CreateFunction` calls where the role ARN does not match a known safe list catches this in real time.
