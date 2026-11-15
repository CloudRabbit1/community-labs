# Background

Authentication answers "who are you?" Authorisation answers "are you allowed to do this?" Many applications get authentication right and get authorisation wrong. IDOR is the most common form of that mistake.

The pattern looks like this. A user logs in and gets a token. The token proves identity. The user then makes a request to `/api/documents/2`. The server checks the token (authentication passes), looks up document 2, and returns it without checking whether the token's owner is the document's owner. The ID in the URL is the direct object reference. Using it without an ownership check makes it insecure.

The impact scales with how predictable the IDs are. Sequential integers are the worst case: once you know your own resource has ID 1, you can enumerate 2, 3, 4 to find everyone else's. UUIDs raise the bar slightly because guessing them is harder, but they are not a fix. If the access control logic is missing, any ID that leaks (from a log, a shared link, or another user's response) can be used to access that resource.

The fix is an authorisation check at the point of access, not a change to how IDs are generated.
