<!-- Partly adapted from affaan-m/everything-claude-code, agents/security-reviewer.md (MIT). Changed: rewritten as a defect-only finder brief over the security-review checklist, and the false-positive list extended into an exclusion list. See THIRD_PARTY_NOTICES.md. -->

# Security lens

Find code that an attacker can exploit, or that exposes data or secrets.

## Rubric

Read the checklist file you were given (the daedalus-core `security-review` skill) and check the changed code against it. Its sections cover secrets, input validation, injection, authentication and authorization, XSS, CSRF, rate limiting, sensitive data exposure, and dependencies. The checklist's examples use particular libraries; apply each rule to the libraries this repository uses.

## Look for

- Injection: SQL, shell, template, path, LDAP, or code built from input without parameters or escaping.
- Broken access control: a route, handler, or query that skips the authentication or authorization check its neighbours apply, or that lets one user read or change another user's data.
- Secrets in code: keys, tokens, or passwords committed to source, tests, or config.
- Sensitive data exposure: secrets, credentials, tokens, or personal data written to logs, error messages, or responses.
- Unsafe handling of untrusted data: deserialization, file paths, redirects, or URLs fetched on the server.
- Weak cryptography for a security purpose: plaintext or fast-hash password storage, predictable tokens, disabled certificate checks.

Trace where the data comes from. A finding needs a path from input an attacker controls (a request, a file upload, a message, an environment the attacker can set) to the dangerous call, shown in the code.

## Do not report

- Values in `.env.example`, sample config, or docs that are placeholders, not real secrets.
- Credentials in test files that are clearly test-only and reach no real system.
- Public keys and identifiers that are meant to be public.
- Fast hashes (MD5, SHA-1, SHA-256) used for checksums, cache keys, or deduplication, not for passwords or signatures.
- Missing rate limiting, missing security headers, or missing hardening, unless a repo rule or the checklist requires it for this kind of code.
- Denial of service through resource exhaustion, and regular-expression denial of service.
- Outdated dependencies, unless the diff adds or changes one with a known vulnerability.
- Memory-safety claims in memory-safe languages.
- Input from a source the attacker does not control, such as constants, trusted configuration, or the program's own output.

## Severity

- **C:** an anonymous attacker can read, change, or delete data they must not reach, run code, or take over an account; or a real secret is committed.
- **H:** the same, but the attacker needs a precondition the code shows is easy to meet, such as any logged-in account; or sensitive data leaks to logs or responses.
- **M:** the attacker needs a precondition the code shows is rare.
- **L:** a hardening gap that a repo rule or the checklist asks for, with no exploit path shown.
