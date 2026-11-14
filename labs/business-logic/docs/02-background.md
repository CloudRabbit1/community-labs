# Background

## What Is a Business Logic Flaw?

A business logic flaw is a vulnerability that arises from incorrect assumptions in the application's design, not from a technical weakness like SQL injection or buffer overflow. The code does exactly what the developer wrote; the problem is that the developer did not write the right code.

Common categories:

| Category | Example |
|----------|---------|
| Missing uniqueness check | Apply same coupon 100 times |
| Missing boundary check | Price goes negative |
| Missing ownership check | Cancel another user's order |
| Missing state validation | Skip payment step in a multi-step flow |
| Missing rate limiting | Brute-force a referral code |

## Why Server-Side Enforcement Matters

Front-end controls (a greyed-out "Apply" button after first use) are not security controls. An attacker can:

- Use `curl` or Burp Suite to bypass the UI entirely.
- Modify JavaScript in the browser.
- Replay captured requests.

Every business rule must be enforced by the server. The server must behave correctly even when the client is adversarial.

## The Coupon Stacking Pattern

A correct coupon implementation tracks which codes have been applied per session (or per order):

```python
if code in cart['coupons_applied']:
    return error('Coupon already applied')
```

The vulnerable implementation skips this check, treating the coupon list as a log rather than a constraint.

## The Negative Price Pattern

A correct checkout validates the total:

```python
if cart['price_cents'] < 0:
    return error('Invalid cart total')
```

The vulnerable implementation processes any integer value, including negative ones. If the payment gateway accepts negative amounts as refunds, the attacker receives money rather than paying it.
