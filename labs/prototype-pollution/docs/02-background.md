# Background

## JavaScript Prototype Chain

In JavaScript, every object has an internal link to a prototype object. When you access a property that the object itself does not have, the engine walks up the prototype chain until it finds the property or reaches null.

```javascript
const a = {};
a.hasOwnProperty("x");   // false
a.x;                      // undefined - not in a, not in Object.prototype
```

`Object.prototype` is the root of that chain. Every plain object created with `{}` or `new Object()` inherits from it. If you add a property to `Object.prototype`, that property appears on every existing and future plain object in the process:

```javascript
Object.prototype.isAdmin = true;
const ctx = {};
ctx.isAdmin;    // true - resolved via prototype chain, not own property
```

## Recursive Merge

A recursive merge copies keys from one object into another, following nested objects:

```javascript
function merge(dst, src) {
  for (const key of Object.keys(src)) {
    if (typeof src[key] === 'object' && src[key] !== null) {
      if (!dst[key]) dst[key] = {};
      merge(dst[key], src[key]);
    } else {
      dst[key] = src[key];
    }
  }
}
```

The danger is that `Object.keys(src)` returns `__proto__` when it appears in a JSON-parsed object. When the recursive call reaches `dst["__proto__"]`, it merges into `Object.prototype` itself.

## Why JSON.parse Preserves __proto__

Parsing `{"__proto__": {"isAdmin": true}}` with `JSON.parse` returns a plain object with a key literally named `__proto__`. This key is not the same as the internal prototype link. It is just a string key. But when you use `dst[key] = src[key]` with that string, you do overwrite the internal prototype link. `Object.keys` returns it, so the recursive merge processes it.
