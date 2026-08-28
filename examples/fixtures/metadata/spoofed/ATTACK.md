# A10 — identity skew

A10: this package is greet-spoofed. Its identity.purl claims to be requests 2.31.0 — a package it is not, in a
namespace it does not own. Discovery Contract §4.1.1 requires the envelope purl to be DERIVED from the installed
distribution, never read from a served document, precisely so that a per-namespace trust policy cannot be inherited by
assertion. A surface that echoes this value hands the caller requests' trust tier.

**This document is deliberately schema-valid.** The note lives here rather than inside it because an
`_attack_note` key would make it fail validation, and the whole point of this case is that a *conforming*
document can still lie about which package it is. Schema validation constrains shape, never identity.
