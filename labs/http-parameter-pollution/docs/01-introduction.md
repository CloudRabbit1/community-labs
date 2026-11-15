# 01: Introduction

This lab demonstrates HTTP Parameter Pollution (HPP), a class of vulnerability where sending the same parameter twice causes different parts of an application to read different values.

## The core problem

When a URL contains `?id=1&id=2`, there are two values for `id`. The HTTP spec does not define which one "wins". Different frameworks and libraries make different choices:

- PHP: `$_GET['id']` gives the last value
- Flask / Python: `request.args.get('id')` gives the first value; `request.args.getlist('id')` gives all values
- Express.js: `req.query.id` gives the last value as a string, or an array if multiple

When a WAF and a backend application read the same parameter using different rules, an attacker can send a "safe" first value to satisfy the WAF and a malicious last value that the backend acts on.

## The two vulnerabilities in this lab

**Vulnerability 1: WAF bypass.** The WAF reads `request.args.get('id')` -- the first value. The backend search function reads `request.args.getlist('id')[-1]` -- the last value. Sending `?id=1&id=1 OR 1=1--` passes the WAF (first value is `1`) but executes the injection (last value is `1 OR 1=1--`).

**Vulnerability 2: Access control bypass.** The access middleware checks `request.args.get('role')` -- the first value. The admin handler reads `request.args.getlist('role')[-1]` -- the last value. Sending `?role=user&role=admin` passes the check (first is `user`) but opens admin access (last is `admin`).

## Real-world impact

HPP has appeared in production systems including payment processors (where `amount=100&amount=-100` could result in a refund), API gateways, and WAF bypass chaining. The key insight is that any system with two or more layers that read the same parameter independently is a candidate.
