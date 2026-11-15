# Introduction

This lab demonstrates a DOM-based cross-site scripting (XSS) vulnerability.

The search application reflects your query back onto the page. The developer used `innerHTML` to display your search term, and that one decision lets an attacker inject HTML and JavaScript that runs in the victim's browser.

Your goal: inject a payload that reads the flag from `/api/flag` and exfiltrates it to an attacker-controlled endpoint.
