# Community Labs

Hands-on security labs you can run locally with Docker.

![Labs](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCloudRabbit1%2Fcommunity-labs%2Fmaster%2Fstats.json&query=%24.total_labs&label=labs&color=orange) ![Clones](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCloudRabbit1%2Fcommunity-labs%2Fmaster%2Fstats.json&query=%24.total_clones&label=clones&color=blue) ![Unique cloners](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCloudRabbit1%2Fcommunity-labs%2Fmaster%2Fstats.json&query=%24.total_uniques&label=unique%20cloners&color=green)

## Mythic Labs

| Lab | Topic |
|-----|-------|
| [cve-2024-23897](./labs/cve-2024-23897/) | Jenkins < 2.442 arbitrary file read: CLI args4j @file expansion leaks any file unauthenticated; chain reads admin password then executes Groovy for RCE |
| [cve-2023-46604](./labs/cve-2023-46604/) | Apache ActiveMQ pre-auth RCE: crafted OpenWire frame triggers ClassPathXmlApplicationContext load, Spring bean executes arbitrary command |
| [cve-2024-28255](./labs/cve-2024-28255/) | OpenMetadata < 1.3.1: hardcoded JWT secret OM_JWT_SECRET allows admin token forgery; metadata description field SSTI via Flask render_template_string |
| [cve-2024-27198](./labs/cve-2024-27198/) | JetBrains TeamCity < 2023.11.4 auth bypass: ;.jsp path parameter suffix skips exact-match auth filter; create SYSTEM_ADMIN and read privileged token |
| [cve-2022-46169](./labs/cve-2022-46169/) | Cacti < 1.2.23 unauth cmdi: X-Forwarded-For bypasses IP check on polling endpoint; poller_id parameter goes to shell_exec without sanitization |
| [cve-2026-123158](./labs/cve-2026-123158/) | OpenSSH auth bypass via musl crypt() |
| [cve-2025-32433](./labs/cve-2025-32433/) | Erlang/OTP SSH pre-authentication RCE |
| [cve-2024-50379](./labs/cve-2024-50379/) | Apache Tomcat partial PUT TOCTOU -> JSP RCE |
| [cve-2022-26134](./labs/cve-2022-26134/) | Atlassian Confluence pre-auth OGNL injection RCE |
| [attacking-ecb-oracles](./labs/attacking-ecb-oracles/) | AES-ECB byte-at-a-time oracle decryption |
| [azure-lateral-movement](./labs/azure-lateral-movement/) | Azure Managed Identity hop chain: IMDS → Key Vault → Blob Storage |
| [cve-2024-10924](./labs/cve-2024-10924/) | Really Simple Security WordPress plugin auth bypass (unauthenticated admin login) |
| [aws-iam-privesc](./labs/aws-iam-privesc/) | AWS IAM PassRole privilege escalation via Lambda |
| [container-escape-docker-socket](./labs/container-escape-docker-socket/) | Container escape via SSRF to unauthenticated Docker socket |
| [cve-2023-22515](./labs/cve-2023-22515/) | Atlassian Confluence broken access control. unauthenticated admin account creation |
| [cve-2023-38408](./labs/cve-2023-38408/) | OpenSSH ssh-agent RCE via agent-library-load extension (agent forwarding) |
| [cve-2026-46331](./labs/cve-2026-46331/) | Linux kernel partial copy-on-write race → local privilege escalation |
| [cve-2022-0847](./labs/cve-2022-0847/) | Dirty Pipe. overwrite read-only page-cached files via pipe splice bug |
| [cve-2025-64459](./labs/cve-2025-64459/) | Django StaticFilesHandler path traversal via %2F-encoded directory traversal |
| [monitoring-evasion](./labs/monitoring-evasion/) | ETW function-pointer patching to suppress Windows event logging |
| [farewell](./labs/farewell/) | Backdoor hidden in a minified JavaScript bundle by a departing developer |
| [cve-2025-58360](./labs/cve-2025-58360/) | GeoServer OGC filter XPath injection. unauthenticated RCE via exec() in property names |
| [cve-2026-43499](./labs/cve-2026-43499/) | GhostLock advisory lock bypass via X-Lock-Bypass header |
| [cve-2023-7028](./labs/cve-2023-7028/) | GitLab account takeover via password reset email sent to all array entries |
| [joomify](./labs/joomify/) | Joomla CVE-2025-25227 MFA bypass. skipping the TOTP step grants admin access |
| [laraveltokenguard-cve-2026-114509](./labs/laraveltokenguard-cve-2026-114509/) | Laravel TokenGuard type-juggling auth bypass. token=0 authenticates as any user |
| [looneytunes](./labs/looneytunes/) | CVE-2023-4911 Looney Tunables. oversized GLIBC_TUNABLES heap overflow → root |
| [nextjs-cve-2025-29927](./labs/nextjs-cve-2025-29927/) | Next.js middleware bypass via x-middleware-subrequest header |
| [brotli-cve-2026-111497](./labs/brotli-cve-2026-111497/) | Brotli CVE-2026-111497. crafted compressed stream triggers OOB read and flag disclosure |
| [wordpress-cve-2026-63030](./labs/wordpress-cve-2026-63030/) | WordPress REST API batch route confusion + SQL injection → unauthenticated RCE |
| [xss2shell-cve-2026-64638](./labs/xss2shell-cve-2026-64638/) | WordPress reflected XSS on login page → admin session → app password → plugin RCE |
| [chameleonescape](./labs/chameleonescape/) | Container escape via CAP_SYS_PTRACE. read host process memory via /proc/1/mem |
| [log4shell-cve-2021-44228](./labs/log4shell-cve-2021-44228/) | Log4Shell. JNDI lookup injection in log message triggers remote class load, unauthenticated RCE |
| [spring4shell-cve-2022-22965](./labs/spring4shell-cve-2022-22965/) | Spring4Shell. data binding classLoader chain writes JSP webshell via Tomcat AccessLogValve |
| [pwnkit-cve-2021-4034](./labs/pwnkit-cve-2021-4034/) | PwnKit. pkexec argc=0 OOB write lets attacker control envp[0] as PATH, escalates to root |
| [papercut-cve-2023-27350](./labs/papercut-cve-2023-27350/) | PaperCut MF/NG auth bypass on setup endpoint, unauthenticated admin password reset then script RCE |
| [roundcube-cve-2025-49113](./labs/roundcube-cve-2025-49113/) | Roundcube post-auth RCE. PHP object deserialization via _from parameter, Crypt_GPG_Engine gadget chain |
| [cve-2023-29489](./labs/cve-2023-29489/) | cPanel 11 reflected XSS via unsanitized username parameter in the login error response |
| [cve-2023-32243](./labs/cve-2023-32243/) | Elementor Pro < 3.12.3 unauthenticated admin password reset via exposed WordPress AJAX action |
| [cve-2023-34362](./labs/cve-2023-34362/) | MOVEit Transfer pre-auth SQLi: UNION injection via folder parameter extracts data from any table |
| [cve-2023-42793](./labs/cve-2023-42793/) | JetBrains TeamCity pre-auth admin token creation: POST to `/app/rest/users/id:1/tokens/<name>` returns a live admin API token |
| [cve-2024-1709](./labs/cve-2024-1709/) | ConnectWise ScreenConnect setup wizard bypass: unauthenticated admin account creation then panel access |
| [cve-2024-21893](./labs/cve-2024-21893/) | Ivanti Connect Secure SSRF via crafted SAML idp_url: server fetches attacker-supplied URL without validation |
| [cve-2024-38856](./labs/cve-2024-38856/) | Apache OFBiz auth bypass via `?requirePasswordChange=Y` skips authentication on every view handler including ProgramExport RCE |
| [cve-2024-45519](./labs/cve-2024-45519/) | Zimbra postjournal pre-auth RCE: shell metacharacters in SMTP email recipient address reach a shell_exec call |
| [cve-2024-4577](./labs/cve-2024-4577/) | PHP-CGI Windows RCE: soft-hyphen (%AD) in query string bypasses IIS argument injection protection and passes -d flags to PHP |
| [cve-2024-7954](./labs/cve-2024-7954/) | SPIP CMS unauthenticated SSTI via article title parameter: Jinja2 expression evaluates to subprocess.Popen RCE |
| [cve-2025-24813](./labs/cve-2025-24813/) | Apache Tomcat partial PUT writes deserialization payload to temp file; matching JSESSIONID triggers FileStore deserialization for RCE |
| [advanced-container-escapes](./labs/advanced-container-escapes/) | Docker socket API escape: SSRF to the exposed socket spawns a privileged container mapping the host filesystem |
| [k8s-pod-escape](./labs/k8s-pod-escape/) | Kubernetes hostPath volume escape: pod with host filesystem mount reads node secrets via /proc |

## Prime Labs

| Lab | Topic |
|-----|-------|
| [command-injection](./labs/command-injection/) | OS command injection via unsanitized shell input in a network diagnostic tool |
| [jwt-security](./labs/jwt-security/) | JWT alg:none bypass and weak HMAC secret forgery |
| [cors-sop](./labs/cors-sop/) | CORS origin reflection with credentials: cross-origin session data leak |
| [idor](./labs/idor/) | IDOR: authenticated but not authorized document access via integer ID enumeration |
| [ssti](./labs/ssti/) | Server-Side Template Injection: Jinja2 expression eval to subprocess.Popen RCE |
| [prototype-pollution](./labs/prototype-pollution/) | Prototype Pollution: __proto__ merge into Object.prototype bypasses admin check |
| [path-traversal](./labs/path-traversal/) | Path traversal via unsanitized filename parameter reads files outside the document root |
| [ssrf](./labs/ssrf/) | SSRF: URL fetcher proxies requests to an internal metadata service holding the flag |
| [xxe-injection](./labs/xxe-injection/) | XXE: external entity expansion reads arbitrary files including /flag.txt |
| [broken-auth](./labs/broken-auth/) | Username enumeration via error message difference, weak password brute-force |
| [file-inclusion](./labs/file-inclusion/) | Local file inclusion via unsanitized page parameter reads arbitrary files including /flag.txt |
| [race-conditions](./labs/race-conditions/) | TOCTOU race on bank transfer endpoint: concurrent requests exploit check-then-act window |
| [orm-injection](./labs/orm-injection/) | ORM injection via raw SQL string interpolation: login bypass with admin'-- payload |
| [ldap-injection](./labs/ldap-injection/) | LDAP filter injection: wildcard payload bypasses username and password checks |
| [dom-based-attacks](./labs/dom-based-attacks/) | DOM XSS via innerHTML: injected script steals admin session cookie |
| [oauth-vulnerabilities](./labs/oauth-vulnerabilities/) | OAuth open redirect: unvalidated redirect_uri lets attacker hijack authorization codes |
| [mfa](./labs/mfa/) | MFA bypass: OTP derived from server timestamp is predictable within the same second |
| [session-management](./labs/session-management/) | Session prediction: sequential session IDs let an attacker hijack the admin session |
| [ws-request-smuggling](./labs/ws-request-smuggling/) | WebSocket request smuggling: raw HTTP bytes after upgrade handshake reach backend as new request |
| [http-browser-desync](./labs/http-browser-desync/) | HTTP request smuggling (CL.TE): Content-Length vs chunked disagreement smuggles admin request |
| [modern-web-stacks](./labs/modern-web-stacks/) | Next.js middleware bypass via x-middleware-subrequest header skips authentication |
| [epoch](./labs/epoch/) | Command injection via unsanitized UNIX timestamp parameter in a date conversion tool |
| [xss-introduction](./labs/xss-introduction/) | Stored XSS: injected script tag in comment board steals admin bot session cookie |
| [docker-rodeo](./labs/docker-rodeo/) | Docker socket escape: exposed /var/run/docker.sock lets attacker spawn privileged container |
| [hammer](./labs/hammer/) | Auth bypass chain: X-Forwarded-For rate-limit bypass + OTP brute force + command allowlist bypass |
| [surfer](./labs/surfer/) | SSRF to internal admin panel: URL fetcher proxies attacker-supplied requests to 127.0.0.1:9000 |
| [matryoshka](./labs/matryoshka/) | Container escape via cgroup v1 release_agent: privileged container writes shell to notify hook |
| [api-auth-flaws](./labs/api-auth-flaws/) | BOLA, BFLA, and mass assignment in a REST API: three authorization flaws, three flags |
| [auth-bypass](./labs/auth-bypass/) | Unsigned base64 session cookie forgery and predictable MD5 password reset token |
| [linux-privesc](./labs/linux-privesc/) | Four LPE paths: SUID binary, sudo find, world-writable sudo script, cap_dac_read_search on Python |
| [webserver-misconfig](./labs/webserver-misconfig/) | Apache directory listing exposes config backup (flag1); CGI semicolon injection reads secret file (flag2) |
| [silent-monitor](./labs/silent-monitor/) | Default credentials in HTML comment; command injection on ping endpoint pivots to internal service on :9090 |
| [support](./labs/support/) | Unsigned pickle session cookie: craft __reduce__ payload for RCE (flag1) or forge admin role without RCE (flag2) |
| [mass-assignment](./labs/mass-assignment/) | JSON over-posting to PUT /api/user/profile injects role:admin field, bypassing server-side authorization |
| [nosql-injection](./labs/nosql-injection/) | MongoDB operator injection via $gt and $regex in JSON login body: auth bypass and admin role escalation |
| [graphql-injection](./labs/graphql-injection/) | GraphQL introspection reveals broken login mutation that skips password check; admin token unlocks second flag |
| [business-logic](./labs/business-logic/) | Coupon stacking and negative price bypass in an e-commerce checkout: no server-side deduplication or floor check |
| [captcha-bypass](./labs/captcha-bypass/) | CAPTCHA answer computable from seed in challenge text; token never invalidated enabling replay attacks |
| [crlf-injection](./labs/crlf-injection/) | HTTP response header injection via unsanitized redirect parameter |
| [host-header-injection](./labs/host-header-injection/) | Host header injection hijacks password reset tokens: app trusts the Host header when building reset links |
| [http-parameter-pollution](./labs/http-parameter-pollution/) | WAF bypass and access control bypass via duplicate HTTP query parameters |
| [java-deserialization](./labs/java-deserialization/) | Untrusted deserialization: attacker-supplied session blob forges admin role or triggers RCE via __reduce__ |
| [open-redirect-chain](./labs/open-redirect-chain/) | OAuth authorization code theft via chained open redirect and weak redirect_uri validation |
| [php-deserialization](./labs/php-deserialization/) | PHP object injection via unserialize() on session blobs: gadget chain gives privilege escalation and RCE |
| [saml-bypass](./labs/saml-bypass/) | XML Signature Wrapping (XSW) attack: valid signature verified on decoy node while attacker-controlled assertion is accepted |
| [sequence](./labs/sequence/) | Three-stage chain: SQLi leaks admin hash, MD5 brute-force gives credentials, SSRF to internal admin API completes compromise |
| [subdomain-takeover](./labs/subdomain-takeover/) | Dangling CNAME to deleted Netlify site: register the external service and serve malicious content under the company subdomain |
| [voyage](./labs/voyage/) | Three-stage chain: LFI leaks config credentials, command injection on admin ping endpoint gives code execution |
| [web-cache-poisoning](./labs/web-cache-poisoning/) | X-Forwarded-Host cache poisoning: unkeyed header injects malicious host into responses cached for all users |
| [xss](./labs/xss/) | Three XSS vectors in one app: reflected via search parameter, stored via comment board, and DOM-based via location.hash |
