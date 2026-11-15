# Business Logic Flaw Lab

A hands-on lab demonstrating two related business logic vulnerabilities in a simple e-commerce shop: coupon stacking (no deduplication) and negative price checkout (no lower-bound validation).

**Vulnerability class:** Business Logic Flaw (OWASP A04:2021 Insecure Design)
**Difficulty:** Beginner
**Flags:** 2

---

## What You Will Learn

- Why application logic must enforce all business rules server-side
- How missing deduplication allows coupon stacking to any depth
- How the absence of price validation allows negative totals
- Why "this should never happen" is not a defense
- Defense: enforce invariants at the boundary, not just in the UI

---

## Prerequisites

- Docker and Docker Compose
- `curl` or Python 3

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8095`.

---

## Lab Scenario

A shop sells a "Premium Report" for $100. Users can apply coupon codes before checkout.

| Coupon | Discount |
|--------|----------|
| SAVE15 | 15% off current price |
| SAVE10 | 10% off current price |
| FLAT5  | $5 flat off |

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cart` | GET | View cart and current price |
| `/cart/reset` | POST | Reset to $100 |
| `/coupon/apply` | POST | Apply a coupon code |
| `/checkout` | POST | Complete purchase |
| `/balance` | GET | View account balance |

---

## Goal

1. Apply `FLAT5` enough times to drive the price to $0 or below (flag 1).
2. Checkout with a negative price so the shop credits your account (flag 2).

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
