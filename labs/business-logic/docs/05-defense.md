# Defense

## Fix 1: Enforce Coupon Uniqueness Server-Side

Before applying a coupon, check whether it was already used in this cart:

```python
if code in cart['coupons_applied']:
    return jsonify({'error': f'Coupon {code} has already been applied'}), 400
```

A single set membership check eliminates coupon stacking entirely.

For stronger guarantees, track redemptions in a persistent store rather than the session, so the same coupon cannot be used across multiple sessions or after a session reset:

```python
used_coupons = db.get_used_coupons(order_id)
if code in used_coupons:
    return error(...)
db.record_coupon_use(order_id, code)
```

## Fix 2: Validate the Final Price Before Checkout

Reject any cart total that falls below zero:

```python
if cart['price_cents'] < 0:
    return jsonify({'error': 'Invalid cart total'}), 400
```

Also enforce a minimum charge if the business requires one:

```python
MIN_CHARGE_CENTS = 1_00  # $1.00
if cart['price_cents'] < MIN_CHARGE_CENTS:
    return jsonify({'error': f'Minimum order is ${MIN_CHARGE_CENTS / 100:.2f}'}), 400
```

## Fix 3: Cap the Total Discount at the Item Price

Prevent individual discounts from overflowing the item's value:

```python
discount = min(discount, cart['price_cents'])
cart['price_cents'] = max(0, cart['price_cents'] - discount)
```

This caps the price at $0 regardless of how many coupons are applied.

## Checklist for Developers

- List every business rule as an explicit check in the backend, not just the frontend.
- For coupons: deduplicate per order in persistent storage.
- For prices: validate the total is within an acceptable range before charging.
- Write a test for each rule that proves it cannot be bypassed by calling the API directly.
- Conduct regular business logic reviews, not just security scans. Scanners do not detect these flaws.
