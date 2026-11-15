# Background

## SAML SSO Flow

1. User visits the application (Service Provider, SP).
2. SP redirects to the Identity Provider (IdP) with a SAML AuthnRequest.
3. User authenticates at the IdP.
4. IdP sends a SAML Response (base64-encoded XML) back to the SP's Assertion Consumer Service (ACS) URL.
5. SP validates the signature and extracts the user's identity.

The SAML Response contains one or more `Assertion` elements. Each assertion includes the user's NameID (identity) and AttributeStatement (role, email, etc.).

## XML Digital Signatures

XML-DSig signs a specific node by its `ID` attribute. The signature covers the canonical form of the node with the signature element removed. A reference in `<ds:Reference URI="#assertion_id">` tells the verifier which node was signed.

Crucially: the signature does not cover the entire XML document. Only the referenced node is signed. Any other content in the document is unverified.

## The XSW Attack Surface

An XSW attack exploits a mismatch between:

- How the verifier finds the node to validate (by ID reference)
- How the attribute reader finds the assertion (by document position or XPath)

If those two operations return different nodes, the attacker wins.

## Why ID-Based Lookup Is Not Enough

A naive implementation might:
1. Verify: find the assertion that has a `<ds:Signature>` child, validate its HMAC.
2. Read: use `.find('.//saml:Assertion')` to get the first assertion.

If the attacker puts an unsigned assertion first, step 1 finds the signed one (second in document order), step 2 finds the unsigned one (first in document order). Both steps succeed independently.

The fix is to perform both operations on the same node: find the signed assertion, verify it, then read its attributes. Never read attributes from a different assertion.
