# Defense

## Lock the Check-Act Sequence

```python
import threading
LOCK = threading.Lock()

with LOCK:
    if STATE["balance"] < amount:
        return error
    STATE["balance"] -= amount
```

The lock makes the check and the deduct atomic from other threads' perspective. While one request holds the lock, all others wait at the `with LOCK:` line.

## Database Transactions

Production systems use database transactions with row-level locks:

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = ? FOR UPDATE;
-- check balance in application code
UPDATE accounts SET balance = balance - ? WHERE id = ?;
COMMIT;
```

`FOR UPDATE` acquires a row lock that prevents other transactions from reading the row until this transaction commits.

## Idempotency Keys

For payment systems, generate a unique transfer ID per request and reject duplicates. Even if two requests race, only the first one with a given ID commits.
