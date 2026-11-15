"""
Business Logic Flaw lab: coupon stacking and negative price exploitation.

The shop sells one item (a "Premium Report") for $100. Users can apply
coupon codes that reduce the price by a percentage. Two flaws:

Flaw 1: The same coupon can be applied multiple times (no deduplication).
Flaw 2: The price is stored as a signed integer. Applying 15% off repeatedly
        can drive the price below $0, and the checkout endpoint honors any
        price including negative ones, crediting the user's balance instead.

Flags:
  FLAG1: when the item price reaches $0 or below after coupon abuse
  FLAG2: when the user "purchases" the item with a negative price
         (i.e., the shop owes the user money)
"""
import secrets
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

COUPONS = {
    'SAVE15': {'type': 'percent', 'value': 15},
    'SAVE10': {'type': 'percent', 'value': 10},
    'FLAT5':  {'type': 'flat',    'value': 5_00},  # $5 in cents
}

ITEM_PRICE_CENTS = 100_00  # $100.00


def get_cart():
    if 'cart' not in session:
        session['cart'] = {
            'price_cents': ITEM_PRICE_CENTS,
            'coupons_applied': [],
        }
    return session['cart']


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


@app.route('/')
def index():
    return jsonify({
        'app': 'CorpShop',
        'endpoints': [
            'GET  /cart            -- view current cart',
            'POST /cart/reset      -- reset cart to $100',
            'POST /coupon/apply    -- apply a coupon code',
            'POST /checkout        -- purchase the item',
            'GET  /balance         -- view account balance',
        ],
        'coupons': list(COUPONS.keys()),
    })


@app.route('/cart')
def view_cart():
    cart = get_cart()
    return jsonify({
        'price_cents': cart['price_cents'],
        'price_display': f'${cart["price_cents"] / 100:.2f}',
        'coupons_applied': cart['coupons_applied'],
    })


@app.route('/cart/reset', methods=['POST'])
def reset_cart():
    session.pop('cart', None)
    session.pop('balance_cents', None)
    return jsonify({'message': 'Cart reset', 'price_display': '$100.00'})


@app.route('/coupon/apply', methods=['POST'])
def apply_coupon():
    data = request.get_json(force=True) or {}
    code = (data.get('code', '') or '').upper().strip()
    if code not in COUPONS:
        return jsonify({'error': 'Unknown coupon code'}), 400

    cart = get_cart()

    # Bug 1: no check for duplicate coupons -- same code can be applied repeatedly
    coupon = COUPONS[code]
    if coupon['type'] == 'percent':
        discount = (cart['price_cents'] * coupon['value']) // 100
    else:
        discount = coupon['value']

    cart['price_cents'] -= discount
    cart['coupons_applied'].append(code)
    save_cart(cart)

    result = {
        'message': f'Coupon {code} applied',
        'discount_cents': discount,
        'price_cents': cart['price_cents'],
        'price_display': f'${cart["price_cents"] / 100:.2f}',
        'coupons_applied': cart['coupons_applied'],
    }

    # Flag 1: price at or below zero
    if cart['price_cents'] <= 0:
        result['flag1'] = FLAG1

    return jsonify(result)


@app.route('/checkout', methods=['POST'])
def checkout():
    cart = get_cart()

    # Bug 2: accepts negative price without validation
    # In a real app this would credit the user's payment method
    paid = cart['price_cents']
    balance = session.get('balance_cents', 0) - paid
    session['balance_cents'] = balance

    result = {
        'message': 'Purchase complete',
        'paid_cents': paid,
        'paid_display': f'${paid / 100:.2f}',
        'balance_cents': balance,
        'balance_display': f'${balance / 100:.2f}',
    }

    # Flag 2: negative price means the shop "owes" the user
    if paid < 0:
        result['flag2'] = FLAG2

    session.pop('cart', None)
    return jsonify(result)


@app.route('/balance')
def balance():
    bal = session.get('balance_cents', 0)
    return jsonify({
        'balance_cents': bal,
        'balance_display': f'${bal / 100:.2f}',
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
