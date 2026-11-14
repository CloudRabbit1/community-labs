# 01: Introduction

This lab demonstrates how two individually low-severity web vulnerabilities can be chained together into a critical account-takeover attack.

## The two flaws

**Flaw 1: Open redirect.** The legitimate client application exposes an endpoint at `/client/go?to=...` that forwards the browser to any URL without validating the destination. On its own, this is a phishing risk.

**Flaw 2: Weak redirect_uri validation.** The OAuth authorization server checks that the redirect_uri parameter starts with a registered prefix (`http://127.0.0.1:8097/client`). It does not require an exact match. On its own, this only matters if a URL starting with that prefix can be turned into something useful.

**Combined:** An attacker registers the open redirect endpoint as the redirect destination. It starts with the allowed prefix, so the OAuth server accepts it. The OAuth authorization code is delivered to the open redirect, which immediately forwards it to the attacker.

## The scenario

BankOAuth is a local OAuth 2.0 provider for the CorpApp client. Users click "Allow" to authorize the client. The client registered `http://127.0.0.1:8097/client` as its redirect prefix. CorpApp also exposes `/client/go?to=...` for internal navigation.

An attacker discovers these two properties and uses them to steal another user's authorization code.

## Why it matters

This class of vulnerability has appeared in production OAuth implementations including Moodle (CVE-2024-21501), several Microsoft OAuth flows, and GitHub Enterprise. The fix is conceptually simple but easy to get wrong: redirect_uri must be validated by exact match against a registered whitelist, never by prefix or substring.
