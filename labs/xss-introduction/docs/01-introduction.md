# Introduction

Cross-site scripting (XSS) happens when an application includes user-supplied data in a page without escaping it first. The browser receiving the page cannot tell the difference between the developer's HTML and the attacker's injected script. Both execute.

This lab is a comment board. Any text you submit is stored on the server and displayed to every visitor, including an admin bot that checks the page every two seconds. The admin's session cookie contains the flag. Your goal is to inject a script that steals that cookie.

XSS is one of the most common vulnerabilities on the web. It can lead to account takeover, session hijacking, credential theft, and malware distribution. The OWASP Top 10 has listed XSS in every edition since 2003.
