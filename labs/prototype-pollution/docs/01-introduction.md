# Introduction

Prototype pollution is a JavaScript vulnerability where an attacker controls keys in an object that is recursively merged into another object. When a key is `__proto__`, the value does not land on the target object. It lands on `Object.prototype`, the shared base object that every other object in the Node.js process inherits from. Any property added there immediately appears on every empty object in the runtime.

This lab runs a note-sharing API that lets users customize note settings via a merge endpoint. The merge function does not filter `__proto__` keys. By sending `{"__proto__": {"isAdmin": true}}`, you add `isAdmin` to `Object.prototype`. The admin check creates a fresh empty object and reads `isAdmin` from it. The property resolves through the prototype chain and returns `true`. The check passes. You read the flag.

## What you will do

- Confirm that a fresh object inherits a property injected into Object.prototype
- Craft a JSON payload that poisons Object.prototype through the merge endpoint
- Retrieve the flag from the admin-only endpoint after bypassing the admin check

## What you need

- Docker with Compose installed (instructions in the README)
- Basic comfort with curl or Python
- Familiarity with JavaScript objects is helpful but not required
