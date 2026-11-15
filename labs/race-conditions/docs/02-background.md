# Background

## Check-Then-Act

The vulnerable pattern:

```
1. Check: is balance >= amount?
2. (gap)
3. Act: deduct amount from balance
```

If two requests both execute step 1 before either executes step 3, they both see a sufficient balance and both proceed with the deduction. The balance ends up negative by as much as `(concurrent_requests - 1) * amount`.

## The 50ms Sleep

The lab inserts a deliberate `time.sleep(0.05)` between the check and the deduct to make the window large enough to demonstrate reliably. Real vulnerabilities have much smaller windows, but the same attack applies. Tools like `turbo intruder` or threading libraries can fire hundreds of requests simultaneously to hit even microsecond windows.

## Why Threading Is the Right Tool

A sequential loop fires requests one at a time. Each request completes before the next starts, so each deduction is visible to the next check. Concurrent threads fire all requests at once, so all checks complete before any deduction runs.

Python's `threading.Barrier` synchronizes threads at a starting line so they all begin the HTTP request at the same instant.
