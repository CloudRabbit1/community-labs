# Background

## What is DOM-Based XSS?

XSS (cross-site scripting) is a class of attack where an attacker gets JavaScript to run in a victim's browser in the context of a trusted site. That lets the attacker read cookies, make authenticated requests, and steal data.

DOM-based XSS is the variant where the injection happens entirely on the client side. The server never sees the malicious payload. A JavaScript snippet reads attacker-controlled data (the URL, `localStorage`, a form field) and writes it to the DOM using a dangerous sink.

## The Dangerous Sink

`element.innerHTML = userInput` is the classic DOM XSS sink. If `userInput` is `<img src=x onerror=alert(1)>`, the browser creates an img element and fires the onerror handler as JavaScript. No HTML encoding happens because you are bypassing the HTML parser by writing directly to the DOM.

Safe alternatives: `element.textContent`, `DOMPurify.sanitize(input)`.

## Why Cookies Matter

The flag endpoint `/api/flag` requires a valid session cookie. An attacker who steals that cookie from the victim's browser can call `/api/flag` as the victim.
