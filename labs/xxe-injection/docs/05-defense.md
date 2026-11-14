# Defense

## Disable External Entity Expansion

The root fix is to tell the parser not to expand external entities. How to do this depends on the language and library.

**Python (defusedxml):**
```python
import defusedxml.ElementTree as ET

# safe: raises DefusedXmlException on external entity
root = ET.fromstring(xml_string)
```

**Python (stdlib, Python 3.8+):**
Python's `xml.etree.ElementTree` raises `ParseError` on external entities by default since 3.8. The vulnerability in this lab is from a custom handler that bypasses that protection.

**Java (DocumentBuilderFactory):**
```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.apache.org/xercesj/features/disallow-doctype-decl", true);
dbf.setExpandEntityReferences(false);
```

**PHP (libxml):**
```php
libxml_disable_entity_loader(true);  // PHP < 8.0
// PHP 8.0+: external entity loading is disabled by default
```

## Reject DOCTYPE Declarations

If the application does not need DOCTYPE support, refuse any document that contains one:

```python
if "<!DOCTYPE" in xml_string.upper():
    return error("DOCTYPE not allowed")
```

This is a defense-in-depth layer, not a substitute for disabling entity expansion in the parser itself.

## Use JSON Instead of XML

If XML is used only because it was a default choice, switching to JSON removes the entire attack surface. JSON has no concept of entities or external resources. For APIs that accept both formats, disable XML input if JSON covers all use cases.
