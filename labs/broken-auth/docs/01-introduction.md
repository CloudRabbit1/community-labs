# Introduction

Broken authentication covers a range of flaws that let an attacker bypass or undermine the login process. This lab demonstrates two that commonly appear together: username enumeration via different error messages, and a weak password that falls to a small wordlist.

The first flaw is subtle. Returning "user not found" for an unknown username but "incorrect password" for a wrong password tells the attacker which usernames are valid without requiring a successful login. That information cuts the brute-force search space from millions of username-password combinations down to just the passwords for accounts that exist.

The second flaw is simpler: the admin account uses `admin123`. Combined with username enumeration, an attacker can confirm `admin` is valid and then find its password in a wordlist within seconds.

## What you will do

- Send login requests with invented usernames to observe the different error messages
- Confirm that `admin` is a valid account via the error message difference
- Brute-force the admin password from a short wordlist and read the flag from `/dashboard`

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- Python 3
