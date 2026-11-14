# Introduction

## What This Lab Is About

SAML (Security Assertion Markup Language) is the protocol behind single sign-on. When a user logs in through a corporate identity provider, the IdP sends a digitally signed XML document called a SAML Response to the application. The app verifies the signature and extracts the user's identity and role from the assertion inside it.

XML Signature Wrapping (XSW) is an attack where the attacker keeps the original signed assertion intact (so signature verification passes) but injects a second, unsigned assertion that the application reads for attribute values.

The core bug is a disconnect: the code that verifies the signature and the code that reads the attributes do not operate on the same node.

## The Vulnerable Pattern

```
Original valid response:
  <samlp:Response>
    <saml:Assertion ID="alice_123" role="user">   <- signed
      <Signature>valid_sig</Signature>
    </saml:Assertion>
  </samlp:Response>

After XSW injection:
  <samlp:Response>
    <saml:Assertion ID="inject" role="admin">     <- unsigned, read by attribute reader
    </saml:Assertion>
    <saml:Assertion ID="alice_123" role="user">   <- signed, found by verifier
      <Signature>valid_sig</Signature>
    </saml:Assertion>
  </samlp:Response>
```

The verifier finds the second assertion (the one with a Signature element) and validates it. The attribute reader grabs the first assertion in document order (the unsigned admin one). Both succeed; the user is logged in as admin.

## Real-World Impact

XSW vulnerabilities have been found in Microsoft Active Directory Federation Services (ADFS), OneLogin, and many SAML libraries. The class of attack was first described in 2008 and continues to appear in new codebases.
