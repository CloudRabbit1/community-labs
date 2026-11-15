# Introduction

This lab demonstrates an OAuth 2.0 misconfiguration: the `redirect_uri` open redirect.

OAuth lets a user grant a third-party application access to their account on another service without sharing their password. The authorization server issues a short-lived code to the application, which exchanges it for a token. The whole flow depends on the authorization server sending that code only to a URI the application owner has pre-registered.

The lab's server skips that check. Any `redirect_uri` is accepted, so an attacker who can trick a user into visiting a crafted link ends up with the user's authorization code and, from there, their access token.

Your goal: craft the authorization request with an attacker-controlled `redirect_uri`, intercept the code, and use it to read the flag from `/api/me`.
