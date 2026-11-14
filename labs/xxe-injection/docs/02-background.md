# Background

## XML Entities

XML entities are named shortcuts for text. Internal entities expand to a fixed string:

```xml
<!DOCTYPE data [
  <!ENTITY greeting "Hello, world">
]>
<data><item>&greeting;</item></data>
```

The parser replaces `&greeting;` with `Hello, world` before the application processes the document.

## External Entities and SYSTEM

A SYSTEM entity fetches its value from a URI instead of a literal string:

```xml
<!ENTITY secret SYSTEM "file:///etc/passwd">
```

When the parser encounters `&secret;`, it opens `/etc/passwd` and substitutes its contents. The URI can also be `http://`, `https://`, or any scheme the runtime supports.

## DOCTYPE Declaration

The DOCTYPE block at the top of an XML document is where entity declarations live:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY flagfile SYSTEM "file:///flag.txt">
]>
<root><item>&flagfile;</item></root>
```

The structure: `<!DOCTYPE` names the root element, `[...]` contains the internal subset (entity declarations), and `>` closes the declaration.

## Why This Matters

An application that accepts user-supplied XML and passes it to a parser with external entity support gives every user the ability to read any file the server process can open. No authentication bypass is needed; a valid XML document with a crafted DOCTYPE is sufficient.
