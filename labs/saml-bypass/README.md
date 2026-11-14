# SAML XML Signature Wrapping Lab

A hands-on lab demonstrating the XML Signature Wrapping (XSW) attack against a SAML Service Provider. The SP verifies a valid signature on one assertion node but reads attributes from a different, unsigned node injected by the attacker.

**CVE anchor:** CVE-2012-6283 (class of vulnerability; real-world variants include CVE-2017-11427, CVE-2020-12729)
**Difficulty:** Intermediate
**Flags:** 2

---

## What You Will Learn

- How SAML SSO works and how assertions are signed
- Why XML digital signature verification is not the same as attribute verification
- How to construct an XSW payload by injecting an unsigned assertion
- Why the SP must verify attributes on the signed node, not positionally
- Defense: use a SAML library with proper XSW protections

---

## Prerequisites

- Docker and Docker Compose
- Python 3 or `curl`

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8093`.

---

## Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/debug/idp` | GET | Test IdP: returns a valid signed SAML Response for alice |
| `/sso/acs` | POST | Assertion Consumer Service: consumes a SAML Response |
| `/profile` | GET | View current session; admin role reveals flag 1 |
| `/admin/secret` | GET | Admin-only endpoint returning flag 2 |

---

## Goal

1. Obtain a valid signed SAML Response for alice (role=user) from the debug IdP.
2. Wrap it with an unsigned admin assertion to bypass signature verification.
3. POST the wrapped response to `/sso/acs` and obtain admin access.
4. Read flag 1 from `/profile` and flag 2 from `/admin/secret`.

---

## Automated Exploit

```bash
python3 exploit/exploit.py
```

---

## Teardown

```bash
docker compose down
```
