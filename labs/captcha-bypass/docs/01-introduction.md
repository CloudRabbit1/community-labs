# Introduction

A CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) is meant to stop automated bots from submitting forms. When implemented poorly, attackers can bypass the CAPTCHA entirely and automate requests just as if it did not exist.

This lab has two weaknesses. First, the CAPTCHA answer is computed from a static seed that the server exposes in the challenge text. Any attacker who reads the challenge can compute the correct answer without solving anything. Second, CAPTCHA tokens are never invalidated after use. The same token works an unlimited number of times.

## What you will do in this lab

1. Fetch the CAPTCHA challenge and observe the seed disclosed in the response.
2. Compute the expected answer from the seed.
3. Submit a login request with the computed answer and obtain Flag 2.
4. Confirm the token replay vulnerability by reusing the same token multiple times.
