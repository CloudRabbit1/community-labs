# Defense

## Never Use innerHTML with Untrusted Input

Replace:

```js
element.innerHTML = userInput;
```

With:

```js
element.textContent = userInput;
```

`textContent` treats the value as plain text. The browser does not parse it as HTML, so no tags or event handlers can execute.

## Content Security Policy

A `Content-Security-Policy` header that restricts `script-src` to known origins limits what injected scripts can do. It is not a substitute for fixing the sink, but it reduces blast radius.

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

This blocks inline `onerror` handlers and prevents `fetch` calls to attacker-controlled origins.

## Sanitize When HTML Is Needed

If you must display user-supplied HTML (a rich text editor, for example), use a library that strips dangerous tags and attributes:

- DOMPurify (browser-side): `element.innerHTML = DOMPurify.sanitize(userInput)`
- bleach (server-side, Python): `bleach.clean(userInput)`
