# Introduction

Server-Side Request Forgery (SSRF) happens when an application makes HTTP requests on behalf of a user without restricting which hosts it can reach. The attacker supplies a URL, and the server fetches it. If the server can reach internal services that the attacker cannot, the attacker has just gained access through the server as a proxy.

This lab simulates a URL preview service that any user can call. Supply a URL, and the app fetches it and returns the content. From the attacker's machine, the internal admin service on port 9000 is unreachable. From inside the container, it is on `127.0.0.1`. The app connects to whatever URL it is given, so pointing it at the internal address routes the request there.

The admin service checks the caller's IP before responding. It sees the request arriving from `127.0.0.1`, which is the app making the outbound request, and returns the flag.

SSRF appears in the OWASP Top 10. It is particularly dangerous in cloud environments where internal metadata services (AWS, GCP, Azure) are reachable from any instance and return credentials by default.
