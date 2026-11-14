# Finding the Bug

The vulnerability is in the `/transfer` handler in `app.py`:

```python
current = STATE["balance"]
if current < amount:
    self.send_json(400, {"error": "insufficient funds"})
    return

time.sleep(0.05)  # 50ms window

STATE["balance"] -= amount
```

The balance is read once into `current`, checked, then the function sleeps, then the balance is deducted. `STATE["balance"]` is a plain integer with no lock. Between the check and the deduct, another thread can read the same value of `STATE["balance"]` and also pass the check.

The fix requires an atomic check-and-deduct. In Python a `threading.Lock` works:

```python
with LOCK:
    if STATE["balance"] < amount:
        ...
    STATE["balance"] -= amount
```

No sleep inside the lock means the window collapses to nanoseconds, and other threads block on the lock instead of racing through the check.
