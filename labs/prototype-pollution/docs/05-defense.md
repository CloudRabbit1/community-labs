# Defense

## Filter Dangerous Keys in the Merge Function

The fix is to skip keys that would mutate the prototype chain:

```javascript
function merge(dst, src) {
  for (const key of Object.keys(src)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;      // skip prototype-chain keys
    }
    if (typeof src[key] === 'object' && src[key] !== null) {
      if (!dst[key]) dst[key] = {};
      merge(dst[key], src[key]);
    } else {
      dst[key] = src[key];
    }
  }
}
```

This blocks the three paths that reach `Object.prototype` or a constructor's prototype.

## Use Object.create(null) for Merge Targets

If the merge target has no prototype, polluting `__proto__` only affects that one object:

```javascript
const options = Object.create(null);   // no prototype chain
merge(options, userInput);
```

This does not protect against merges into objects with a normal prototype, so the key filter is still needed.

## Use structuredClone or a Validated Schema

For configuration merges, avoid recursive key-walking entirely. Validate the input against an explicit schema before applying it:

```javascript
const ALLOWED_OPTIONS = new Set(['color', 'font', 'size']);
for (const key of Object.keys(input)) {
  if (ALLOWED_OPTIONS.has(key)) options[key] = input[key];
}
```

An allowlist of valid keys cannot be bypassed with `__proto__`, `constructor`, or any other injection.

## Use a Battle-Tested Library

Libraries like `lodash.merge` have patched prototype pollution. If you need deep merge, use a maintained library rather than a hand-rolled recursive function.
