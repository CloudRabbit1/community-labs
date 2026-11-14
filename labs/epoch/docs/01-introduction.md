# Introduction

UNIX timestamps count the seconds since January 1, 1970. Web applications convert them to human-readable dates for display, logging, and debugging. The conversion is usually done by calling a system utility like `date`.

The problem: when an application builds a shell command string from user input and runs it without sanitization, the user controls part of the shell. Shell metacharacters like `;`, `|`, and `&&` let an attacker terminate the original command and start a new one. This is OS command injection.

This lab reproduces the vulnerability in the TryHackMe "Epoch" room: a timestamp conversion service that calls `date -d @<ts>` with the user's input pasted directly into the command string. The goal is to inject a second command that reads the flag.
