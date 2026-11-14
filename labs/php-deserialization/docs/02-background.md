# Background

## PHP Serialization Format

PHP's `serialize()` function converts any value to a portable string. The format is compact and human-readable:

| Type | Example |
|------|---------|
| String | `s:5:"hello";` |
| Integer | `i:42;` |
| Boolean | `b:1;` |
| Array | `a:2:{s:3:"key";s:3:"val";}` |
| Object | `O:9:"ClassName":1:{s:4:"prop";s:5:"value";}` |

An array with two string keys looks like:

```
a:2:{s:4:"user";s:5:"alice";s:4:"role";s:4:"user";}
```

An object of class `Logger` with two string properties looks like:

```
O:6:"Logger":2:{s:7:"logfile";s:14:"/tmp/test.txt";s:7:"message";s:4:"test";}
```

The letter codes are: `a` = array, `O` = object, `s` = string, `i` = integer, `b` = boolean.

## Magic Methods

PHP classes can define special methods that run automatically in response to lifecycle events:

| Method | When it runs |
|--------|-------------|
| `__wakeup()` | Immediately after `unserialize()` reconstructs the object |
| `__destruct()` | When the object is garbage-collected (after `unserialize()` returns) |
| `__toString()` | When the object is used in a string context |
| `__get()` | When an undefined property is read |

These methods run with the property values the attacker supplied in the serialized payload. If `__destruct` calls `file_put_contents($this->logfile, $this->message)`, the attacker controls both arguments.

## Gadget Chains

A single class rarely does something directly dangerous. But in a large codebase, an attacker can chain several classes:

1. Class A's `__wakeup` calls a method on `$this->helper`.
2. If `$this->helper` is a Class B object, B's method runs.
3. B's method calls `$this->target->exec()`.
4. Class C implements `exec()` as a system call.

Tools like PHPGGC (PHP Generic Gadget Chains) catalog known gadget chains for popular frameworks. This lab demonstrates a single-step `__destruct` gadget to keep the focus on the core concept.
