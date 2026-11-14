# Defense

## Use unpredictable server-side challenges

The CAPTCHA challenge must be derived from a random value that is not shared with the client. Store the expected answer server-side and never expose the seed or the answer in the response. Use a cryptographically random value as the challenge basis, not a static string.

## Invalidate tokens after use

Remove the token from the valid set immediately after a successful verification, before the login logic runs. This prevents replay:

```python
# Correct: remove before use
if captcha_token not in _valid_tokens:
    return 403
_valid_tokens.discard(captcha_token)  # single-use
# ... rest of login ...
```

## Add token expiry

Tokens that are never used should expire after a short window (60 to 300 seconds). Store tokens with their creation timestamp and reject any token older than the expiry threshold.

## Rate limit CAPTCHA requests and login attempts

Limit how many CAPTCHA tokens a single IP can request per minute and how many login attempts are allowed. This slows brute-force attacks even if the CAPTCHA answer is guessable.

## Use a proven CAPTCHA library

Implement reCAPTCHA, hCaptcha, or a similar third-party service rather than building your own. Rolling a custom CAPTCHA almost always introduces one of these weaknesses.
