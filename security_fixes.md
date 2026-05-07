# Security Fixes

This document describes the security improvements implemented in the `secure` branch of Insecure Login Lab.

The goal of the secure branch is to demonstrate how intentionally vulnerable code can be remediated using common defensive web security practices.

---

# Overview

The vulnerable version of the application intentionally included multiple common web application vulnerabilities for educational purposes.

The secure branch introduces mitigations for:

- SQL Injection
- Plaintext password storage
- Cookie poisoning
- Privilege escalation
- Reflected XSS
- Stored XSS
- Weak session handling
- Missing CSRF protection
- Unsafe file uploads
- Path traversal risks
- Missing browser security headers

---

# SQL Injection Fixes

## Vulnerable Behavior

The vulnerable branch constructed SQL queries using Python string interpolation:

```python
query = f"SELECT * FROM users WHERE username = '{username}'"
```

This allowed attackers to manipulate SQL query structure.

---

## Remediation

The secure branch replaces vulnerable queries with parameterized statements:

```python
cur.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)
```

This prevents user input from modifying SQL syntax.

---

# Password Storage Improvements

## Vulnerable Behavior

Passwords were stored directly in plaintext inside the database.

---

## Remediation

Passwords are now hashed using Werkzeug password hashing:

```python
generate_password_hash(password)
```

Authentication uses:

```python
check_password_hash(...)
```

instead of plaintext comparison.

---

# Authentication and Session Security

## Vulnerable Behavior

The vulnerable branch used a custom client-controlled authentication cookie:

```text
user_id|username|role
```

This allowed:
- cookie poisoning
- delimiter injection
- privilege escalation

---

## Remediation

The secure branch:
- removes the custom authentication cookie
- uses Flask's signed session system
- reloads authorization state from the database

Administrative access is now verified server-side.

---

# Cross-Site Scripting (XSS) Fixes

## Vulnerable Behavior

The vulnerable search page intentionally disabled Jinja escaping using:

```jinja2
{{ q|safe }}
```

This enabled reflected XSS.

The upload system also allowed executable HTML uploads.

---

## Remediation

The secure branch:
- removes `|safe`
- restores normal Jinja escaping
- restricts uploaded file types
- sanitizes uploaded filenames using `secure_filename`

---

# File Upload Security

## Vulnerable Behavior

The vulnerable upload system:
- accepted arbitrary file types
- allowed HTML uploads
- served uploaded content directly from the application origin

---

## Remediation

The secure branch:
- restricts upload extensions
- sanitizes filenames
- isolates uploads per user
- uses Flask's safe file serving helpers

Allowed extensions are now limited to common non-executable formats.

---

# Path Traversal Mitigation

## Vulnerable Behavior

User-controlled file paths could potentially be abused to escape intended directories.

---

## Remediation

The secure branch uses:

```python
send_from_directory(...)
```

together with sanitized filenames to safely resolve file paths.

---

# CSRF Protection

## Vulnerable Behavior

The vulnerable branch did not include CSRF protection on POST forms.

Attackers could potentially trigger authenticated actions through malicious external pages.

---

## Remediation

The secure branch uses Flask-WTF CSRF protection:

```python
CSRFProtect(app)
```

POST forms now include CSRF tokens.

---

# Cookie Security Improvements

## Vulnerable Behavior

The vulnerable branch intentionally disabled browser cookie protections.

---

## Remediation

The secure branch enables safer Flask session settings:

```python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
```

These settings reduce:
- JavaScript cookie access
- cross-site request abuse

---

# Browser Security Headers

## Remediation

The secure branch uses Flask-Talisman to add browser security headers including:

- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options

These headers improve browser-side protections against:
- XSS
- clickjacking
- MIME sniffing

---

# OWASP ZAP Testing

OWASP ZAP was used to compare the vulnerable and secure versions of the application.

The vulnerable branch produced numerous findings including:
- SQL Injection
- XSS
- missing CSRF protection
- weak cookie settings

After remediation, automated scans primarily reported:
- informational findings
- development server disclosures
- low-severity CSP configuration suggestions

Manual verification confirmed that the major exploitable vulnerabilities were mitigated.

---

# Remaining Limitations

The secure branch improves security significantly, but it is still an educational project and not production-ready.

Examples of additional improvements that could be implemented include:

- rate limiting
- account lockout protection
- password complexity requirements
- audit logging
- secure deployment configuration
- HTTPS enforcement
- production WSGI deployment

---

# Educational Goal

The purpose of this project is to demonstrate both:

1. how common web vulnerabilities occur
2. how those vulnerabilities can be remediated

The comparison between the vulnerable and secure branches is intended to help learners understand secure development practices in realistic Flask applications.
