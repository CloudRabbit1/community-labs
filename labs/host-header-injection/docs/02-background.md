# Background

## The HTTP Host Header

Every HTTP/1.1 request carries a `Host` header that tells the server which domain the client is trying to reach. For a request to `https://example.com/page`, the browser sends:

```
GET /page HTTP/1.1
Host: example.com
```

The header exists because one server can host many domains (virtual hosting). The server uses `Host` to route the request to the right application.

## Why the Host Header Is Dangerous Input

The `Host` header is sent by the client. Any HTTP client, including `curl`, Burp Suite, or a custom script, can set it to any value:

```bash
curl -H "Host: attacker.com" http://victim-app.com/reset-password
```

The server receives the request on its normal IP address, but the header says `attacker.com`. An application that reads `request.headers['Host']` and trusts it is reading attacker-controlled input.

## The Password Reset Flow

A typical reset flow has three steps:

1. User submits their email address.
2. App generates a secret token, stores it, and emails a link containing the token.
3. User clicks the link, app validates the token, and allows a password change.

The token is a secret that proves ownership of the email account. The link only works because the token is embedded in it. If the attacker can redirect that link to their own server, they capture the token without ever accessing the email account.

## Simulating the Email Server

This lab includes a `/debug/last-email` endpoint that acts as a stand-in for the attacker's server. In a real attack, the attacker would run a web server and wait for the victim to click the link. The debug endpoint serves the same purpose here: it lets you see what the email contained.
