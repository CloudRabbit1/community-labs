# Background

## IAM roles and policies

In AWS, every resource that runs code, a Lambda function, an EC2 instance, a container task, does so under an **IAM role**. The role is a collection of permissions. When code runs under a role, it can call any AWS API that the role permits.

Roles are separate from users. A user is a long-lived identity with static credentials. A role is temporary: a service assumes it at runtime and gets short-lived credentials that expire when the work is done.

## iam:PassRole

When you create a Lambda function, you tell AWS which role the function should run under. That act of assignment is controlled by a separate IAM permission: `iam:PassRole`.

If `dev-user` has `lambda:CreateFunction` but not `iam:PassRole`, they cannot attach a role to a Lambda. If they have both, they can. The intent of `iam:PassRole` is to control role assignment. When it is granted too broadly, it becomes an escalation path.

The logic is: `dev-user` cannot call `s3:GetObject`. But if `dev-user` can create a Lambda with `AdminRole` attached, the Lambda can call `s3:GetObject` on their behalf. The Lambda's permissions are `AdminRole`'s permissions, not `dev-user`'s.

## Why this misconfiguration happens

Developers often grant `iam:PassRole` with `Resource: *` for convenience, meaning "allow this user to attach any role to any service". The intention is to let developers deploy applications. The side effect is that any role in the account becomes reachable, including roles with far more access than the developer was meant to have.

Fixing it requires scoping `iam:PassRole` to specific roles: only the roles a developer legitimately needs to attach to their functions. That is more work to maintain. Many teams skip it.

## Lambda execution model

When you invoke a Lambda function, AWS runs the handler with the credentials of the function's execution role. Those credentials have the permissions of that role. If the role is `AdminRole`, the function can do anything `AdminRole` permits, regardless of who invoked it.

This is by design. The invoker does not need the invoked Lambda's permissions. The invoker only needs `lambda:InvokeFunction`.
