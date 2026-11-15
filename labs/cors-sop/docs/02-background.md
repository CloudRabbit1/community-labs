# Background

Your browser will not let a page at `https://attacker.com` read a response from `https://bank.com/account`. That is the Same-Origin Policy. Two URLs share an origin when their scheme, host, and port all match. The rule exists because cookies are automatically sent with requests, so without it any page you visit could silently read your email, your bank balance, or your session data from every other site you are logged into.

CORS lets a server say "I trust these other origins too." The server adds an `Access-Control-Allow-Origin` header to its response naming the trusted origin. For credentialed requests (ones that send cookies), it also adds `Access-Control-Allow-Credentials: true`. The browser only exposes the response body to the calling page when both headers are present and the calling origin matches.

The key constraint: `Access-Control-Allow-Origin: *` is incompatible with `Access-Control-Allow-Credentials: true`. Browsers reject that combination. So a server that wants to allow credentialed cross-origin requests must name specific trusted origins. Reflecting the `Origin` request header back as the `Access-Control-Allow-Origin` response header sidesteps this constraint, but it also grants trust to every origin in the world.

Preflight requests are OPTIONS requests the browser sends before a cross-origin request to check whether the server will allow it. The server's OPTIONS response determines whether the browser sends the real request. For this bug, the preflight check is what exposes the misconfiguration directly.
