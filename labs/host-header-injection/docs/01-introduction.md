# Introduction

## What This Lab Is About

This lab shows how an application that uses the HTTP `Host` header to build URLs can be exploited to steal password reset tokens. The attacker never touches the victim's email account. Instead, they make the application generate a reset link that points to a server the attacker controls.

## The Vulnerable Flow

A user clicks "forgot password" and the app emails a link like:

```
http://app.example.com/reset?token=abc123
```

The app builds that URL using whatever `Host` header the request contained. If the attacker sends the reset request with a forged header:

```
Host: attacker.com
```

The app generates:

```
http://attacker.com/reset?token=abc123
```

When the victim clicks the link, the token lands on the attacker's server. The attacker then uses that token on the real app to change the password and take over the account.

## Why This Matters

Password reset poisoning is a real class of attack with documented CVEs across popular frameworks and applications. The fix is a single line of code: use the app's configured base URL instead of the request header.
