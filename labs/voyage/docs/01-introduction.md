# Introduction

This lab demonstrates a multi-stage exploit chain that starts with an unauthenticated file read vulnerability and ends with remote code execution. Each stage opens the door to the next.

The three vulnerabilities are: Local File Inclusion (LFI) in a file viewer, plaintext credentials stored in a configuration file, and OS command injection in an admin utility.

## What you will do in this lab

1. Use LFI to read a configuration file that should not be accessible.
2. Extract the admin password from the configuration file and log in.
3. Exploit command injection in the admin ping tool to execute code on the server.

## Why it matters

Multi-stage chains are how real attacks work. No single bug is always enough. Attackers combine a low-severity read vulnerability with a medium-severity credential exposure with a high-severity injection to reach full system access. Understanding each link in the chain helps defenders prioritize which vulnerability to fix first (the LFI, in this case, since it enables everything else).
