# Race Conditions

| Field | Value |
|-------|-------|
| Technique | Race condition: check-then-act without locking |
| Target | BankSim transfer endpoint |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/transfer` endpoint checks the account balance, sleeps 50ms, then deducts the amount. No lock protects the check-deduct window. Firing 20 concurrent transfer requests means all 20 pass the balance check before any deduction runs, driving the balance far below zero.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/race-conditions
docker compose up --build -d
```
