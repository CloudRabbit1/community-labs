#!/usr/bin/env python3
"""Simulated AWS environment for IAM PassRole privilege escalation lab."""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

ACCESS_KEY = "AKIAI-DEV-USER-KEY"

POLICIES = {
    "DevUserPolicy": {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": ["iam:ListRoles", "iam:GetRole"], "Resource": "*"},
            {"Effect": "Allow", "Action": "lambda:CreateFunction", "Resource": "*"},
            {"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": "*"},
            {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"},
            {"Effect": "Allow", "Action": "iam:PassRole",
             "Resource": "arn:aws:iam::123456789012:role/*"},
        ]
    }
}

ROLES = {
    "LambdaBasicExecutionRole": {
        "Arn": "arn:aws:iam::123456789012:role/LambdaBasicExecutionRole",
        "Description": "Basic Lambda execution permissions: CloudWatch Logs only.",
        "has_s3_access": False,
    },
    "AdminRole": {
        "Arn": "arn:aws:iam::123456789012:role/AdminRole",
        "Description": "Administrator access to all AWS services.",
        "has_s3_access": True,
    },
}

LAMBDAS = {}


def execute_lambda(code, role_name, event):
    flag = open("/flag.txt").read().strip()
    has_s3 = ROLES.get(role_name, {}).get("has_s3_access", False)

    class S3Client:
        def list_buckets(self):
            if not has_s3:
                raise PermissionError(
                    "AccessDeniedException: not authorized to perform s3:ListBuckets"
                )
            return {"Buckets": [{"Name": "secret-bucket"}]}

        def get_object(self, Bucket="", Key="", **_):
            if not has_s3:
                raise PermissionError(
                    "AccessDeniedException: not authorized to perform s3:GetObject"
                )
            if Bucket == "secret-bucket" and Key == "flag.txt":
                return {"Body": flag, "ContentLength": len(flag)}
            raise FileNotFoundError(f"NoSuchKey: {Key} in {Bucket}")

    class Boto3Mock:
        def client(self, service, **_):
            if service == "s3":
                return S3Client()
            raise ValueError(f"Service '{service}' not available in this simulation")

    _boto3_mock = Boto3Mock()
    _json = json

    def _import(name, *args, **kwargs):
        if name == "boto3":
            return _boto3_mock
        if name == "json":
            return _json
        raise ImportError(f"Module '{name}' not available in this Lambda simulation")

    safe_builtins = {
        "__import__": _import,
        "print": print, "str": str, "int": int, "float": float,
        "dict": dict, "list": list, "tuple": tuple, "bool": bool,
        "len": len, "range": range, "enumerate": enumerate,
        "Exception": Exception, "PermissionError": PermissionError,
        "FileNotFoundError": FileNotFoundError, "ValueError": ValueError,
    }

    globs = {"__builtins__": safe_builtins, "json": json, "boto3": _boto3_mock}
    local_ns = {}
    exec(compile(code, "<lambda>", "exec"), globs, local_ns)

    if "lambda_handler" not in local_ns:
        raise ValueError("Lambda must define lambda_handler(event, context)")

    class Context:
        function_name = "privesc-function"
        aws_request_id = "sim-00000001"

    return local_ns["lambda_handler"](event, Context())


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def auth(self):
        key = self.headers.get("X-Access-Key", "").strip()
        if key != ACCESS_KEY:
            self.send_json(401, {"Error": {"Code": "InvalidClientTokenId",
                                           "Message": "The security token is invalid."}})
            return False
        return True

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        if not self.auth():
            return
        if self.path == "/":
            self.send_json(200, {
                "Message": "Welcome, dev-user.",
                "Credentials": {"AccessKeyId": ACCESS_KEY},
                "Endpoints": [
                    "GET  /iam/get-user-policies",
                    "GET  /iam/list-roles",
                    "POST /lambda/create-function",
                    "GET  /lambda/list-functions",
                    "POST /lambda/invoke",
                ],
            })
        elif self.path == "/iam/get-user-policies":
            self.send_json(200, {
                "UserName": "dev-user",
                "AttachedPolicies": POLICIES,
            })
        elif self.path == "/iam/list-roles":
            self.send_json(200, {"Roles": [
                {"RoleName": n, "Arn": r["Arn"], "Description": r["Description"]}
                for n, r in ROLES.items()
            ]})
        elif self.path == "/lambda/list-functions":
            self.send_json(200, {"Functions": [
                {"FunctionName": n, "Role": f["role"]}
                for n, f in LAMBDAS.items()
            ]})
        else:
            self.send_json(404, {"Error": {"Code": "NotFound"}})

    def do_POST(self):
        if not self.auth():
            return
        data = self.body()
        if self.path == "/lambda/create-function":
            name = data.get("FunctionName", "")
            code = data.get("Code", "")
            role = data.get("Role", "")
            if not (name and code and role):
                self.send_json(400, {"Error": {"Code": "InvalidParameterValueException",
                                               "Message": "FunctionName, Code, and Role are required"}})
                return
            role_name = role.split("/")[-1]
            if role_name not in ROLES:
                self.send_json(400, {"Error": {"Code": "NoSuchEntityException",
                                               "Message": f"Role {role} not found"}})
                return
            LAMBDAS[name] = {"code": code, "role": role_name}
            self.send_json(201, {
                "FunctionName": name,
                "FunctionArn": f"arn:aws:lambda:us-east-1:123456789012:function:{name}",
                "Role": role,
                "State": "Active",
            })
        elif self.path == "/lambda/invoke":
            name = data.get("FunctionName", "")
            payload = data.get("Payload", {})
            if name not in LAMBDAS:
                self.send_json(404, {"Error": {"Code": "ResourceNotFoundException",
                                               "Message": f"Function not found: {name}"}})
                return
            func = LAMBDAS[name]
            try:
                result = execute_lambda(func["code"], func["role"], payload)
                self.send_json(200, {"StatusCode": 200, "Payload": result})
            except PermissionError as e:
                self.send_json(200, {"StatusCode": 403, "FunctionError": "Unhandled",
                                     "Payload": str(e)})
            except Exception as e:
                self.send_json(200, {"StatusCode": 500, "FunctionError": "Unhandled",
                                     "Payload": str(e)})
        else:
            self.send_json(404, {"Error": {"Code": "NotFound"}})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
