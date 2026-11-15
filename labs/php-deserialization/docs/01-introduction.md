# Introduction

## What This Lab Is About

This lab shows how calling `unserialize()` on attacker-supplied bytes in PHP can lead to privilege escalation and arbitrary file writes.

PHP serialization turns any value into a string representation. An attacker who can supply that string controls what objects PHP reconstructs. If the application's codebase contains classes with magic methods like `__destruct` or `__wakeup`, those methods run automatically when `unserialize()` finishes, with the attacker-supplied property values.

## The Two Attack Paths

**Path 1: data forgery.** PHP serializes arrays and primitives just like objects. The session stores `['user' => 'alice', 'role' => 'user']`. The application reads `role` from the deserialized value and trusts it. Submitting a forged serialized array with `'role' => 'admin'` is enough to escalate privileges.

**Path 2: gadget chains.** The codebase contains a `Logger` class whose `__destruct` method calls `file_put_contents($this->logfile, $this->message)`. An attacker serializes a `Logger` object with attacker-controlled `logfile` and `message` properties. When PHP garbage-collects it after `unserialize()`, `__destruct` runs and writes any content to any file accessible by the web server process.

## Why This Matters

PHP object injection has been exploited in WordPress, Joomla, Drupal, Magento, Laravel, and dozens of other frameworks. Any call to `unserialize()` on user-supplied input is a potential vulnerability, even if the application never directly uses the deserialized value.
