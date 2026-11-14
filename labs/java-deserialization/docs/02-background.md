# Background

## What Is Serialization?

Serialization converts an in-memory object (a dict, a class instance) into a byte stream that can be stored or transmitted. Deserialization is the reverse: it converts bytes back into an object.

Python's `pickle` module is the standard serialization library:

```python
import pickle, base64

data = {'user': 'alice', 'role': 'user'}
blob = pickle.dumps(data)          # bytes
print(base64.b64encode(blob))      # safe to put in JSON
```

To restore it:

```python
restored = pickle.loads(blob)      # back to dict
```

## The __reduce__ Protocol

Python lets any class customize how it is pickled by defining `__reduce__`. This method returns a tuple that tells `pickle.loads` how to reconstruct the object. The first element is a callable; `pickle.loads` calls it with the remaining elements as arguments.

```python
import os, pickle

class Exploit:
    def __reduce__(self):
        return (os.system, ('id > /tmp/proof.txt',))

payload = pickle.dumps(Exploit())
```

When `pickle.loads(payload)` runs, it calls `os.system('id > /tmp/proof.txt')`. The object itself is never created; only the callable in `__reduce__` matters.

## Why pickle Is Unsafe for Untrusted Input

The Python documentation states this directly:

> Warning: The pickle module is not secure. Only unpickle data you trust.

There is no way to safely deserialize an untrusted pickle. Even allowlisting types at the import level can often be bypassed by chaining built-in callables. The only safe fix is to not use pickle for data that comes from outside the process.

## Java Deserialization: The Same Problem

Java's `ObjectInputStream.readObject()` has the same flaw. Java classes can override `readObject()` or implement `readResolve()` to run arbitrary code during deserialization. When a class with these methods is on the application's classpath (even transitively through a library like Apache Commons Collections), an attacker can chain gadgets to achieve RCE.

The attack surface, exploit chain, and defense strategies are the same as for `pickle`.
