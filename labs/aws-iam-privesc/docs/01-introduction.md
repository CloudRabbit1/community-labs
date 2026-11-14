# Introduction

You have credentials for `dev-user`, a low-privilege AWS account. That account cannot read the flag in the S3 bucket `secret-bucket`. Your goal is to read the flag anyway.

The path goes through AWS Lambda. `dev-user` can create Lambda functions and choose which IAM role they execute under. One of the available roles, `AdminRole`, has full S3 access. By creating a Lambda function and passing `AdminRole` as its execution role, you run code with administrator permissions even though your own credentials have none.

This is **IAM privilege escalation via PassRole**. It is one of the most common misconfigurations in real AWS environments and has led to significant breaches.

## What you will do

Enumerate the permissions on `dev-user`, identify `AdminRole` as an escalation target, create a Lambda function that reads from S3, and invoke it. The Lambda runs as `AdminRole` and returns the flag.

## Lab setup

```bash
docker compose up --build -d
```

The lab listens on `http://localhost:8080`. All requests require an `X-Access-Key` header:

```
X-Access-Key: AKIAI-DEV-USER-KEY
```
