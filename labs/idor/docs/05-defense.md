# Defense

Add an ownership check at the point of access. After retrieving the document, compare its `owner_id` against the authenticated user's ID:

```python
doc = DOCS.get(doc_id)
if not doc:
    self.send_json(404, {"error": "Document not found"})
    return
# Fix: reject if the requesting user does not own this document
if doc["owner_id"] != USERS[user]["id"]:
    self.send_json(403, {"error": "Forbidden"})
    return
self.send_json(200, {"document": doc})
```

Return 403, not 404. Returning 404 for documents the user does not own leaks which IDs exist. Returning 403 tells them the document exists but they are not allowed to read it. Both responses stop the data leak; 403 is more correct. Some teams prefer 404 everywhere to avoid confirming existence, but that obscures errors during development and rarely provides meaningful security in practice since the IDs are still discoverable through other means.

For admin access patterns, the check becomes a role check:

```python
if doc["owner_id"] != USERS[user]["id"] and USERS[user].get("role") != "admin":
    self.send_json(403, {"error": "Forbidden"})
    return
```

Switching from sequential integers to UUIDs does not fix the bug. It only raises the bar for guessing. Authorisation checks must exist regardless of ID format.

Detection: look for authenticated users accessing resources owned by other users. In access logs, flag any user ID that appears in `GET /api/documents/<id>` requests where the `id` does not belong to that user. Any such access either means a legitimate admin use case (which should be explicit in code) or an active IDOR exploit.
