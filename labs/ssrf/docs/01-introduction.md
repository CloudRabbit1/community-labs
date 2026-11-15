# Introduction

Server-Side Request Forgery (SSRF) is a vulnerability where an application fetches a URL supplied by the user without restricting which hosts it can reach. The attacker does not connect to the internal service directly. Instead, they tell the server to connect on their behalf. The server's network position, which may include access to internal hosts, cloud metadata APIs, and admin interfaces, becomes the attacker's vantage point.

This lab runs a URL fetcher that proxies HTTP requests for the user. A second service on `127.0.0.1:9000` holds the flag but binds only to the loopback interface, so it cannot be reached from outside the container. By supplying `http://127.0.0.1:9000/secret` as the URL to fetch, the attacker uses the web server as a relay.

SSRF was added to the OWASP Top 10 in 2021 after a string of high-impact incidents, including a 2019 breach of a major cloud provider where an attacker read AWS instance metadata credentials through a misconfigured proxy.

## What you will do

- Confirm the fetch endpoint makes outbound requests to attacker-controlled URLs
- Identify the internal metadata service and its port
- Use the SSRF to retrieve the flag from the internal service

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- curl or Python 3
