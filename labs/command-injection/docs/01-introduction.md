# Introduction

OS command injection happens when an application passes user-supplied input to a system shell without sanitizing it first. The shell interprets metacharacters like `;`, `|`, and `&&` as command separators, so an attacker can append arbitrary commands to the intended one.

This lab simulates a network diagnostic tool that runs `ping` for a user-supplied hostname. Because the hostname goes directly into the shell command string, injecting `;cat /flag.txt` after the hostname causes the server to run both `ping` and `cat`.

Command injection is consistently in the OWASP Top 10. It is one of the most damaging vulnerability classes because it gives the attacker direct access to the operating system as the web server's user.
