# Introduction

## What This Lab Is About

Business logic flaws are vulnerabilities in the application's intended workflow rather than in a specific technology. No injection, no memory corruption -- just a gap between how the developer expected the system to be used and how an attacker can actually use it.

This lab has two flaws:

**Flaw 1: Coupon deduplication is missing.** A coupon can be applied 20, 50, or 1000 times in a row. The server never checks whether the same code was already used. The UI might enforce it, but the server does not, and attackers talk to the server.

**Flaw 2: Price has no lower bound.** After enough flat discounts, the price becomes negative. The checkout endpoint accepts the transaction, crediting the user's balance instead of charging them. The business logic assumes "price will never be negative" but never enforces it.

## Why These Flaws Matter

Coupon stacking and negative price exploits are real attacks documented against real e-commerce platforms. They result in direct financial loss -- free items, credit card refunds, or account credit that can be cashed out. Unlike injection attacks, they leave no obvious traces in logs and are often discovered only during financial reconciliation.

The lesson: every business rule that the application depends on must be enforced explicitly in code, not assumed from context.
