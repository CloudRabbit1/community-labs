# Introduction

A race condition happens when a program's behavior depends on the timing of two or more operations, and those operations are not properly synchronized. In web applications this usually means a check-then-act sequence where another request can slip in between the check and the action.

This lab simulates a bank that checks an account balance before transferring funds but waits 50ms before deducting the amount. That gap lets multiple concurrent requests each pass the balance check before any deduction runs. The account ends up deeply overdrawn.

Race conditions in financial logic have caused real losses. They appear in coupon redemption systems, vote counters, rate limiters, and anywhere two steps happen without a lock between them.
