# Insecure Login Lab

## Overview

Insecure Login Lab is a deliberately vulnerable Flask web application intended for learning web application security concepts in a safe, local environment.

The application contains intentionally insecure implementations of:

* Authentication
* Authorization
* Session management
* File uploads
* Cookie handling
* SQL query construction
* HTML rendering
* CSRF protection

The goal of the project is to:

* Learn how common web vulnerabilities work
* Practice identifying vulnerabilities manually
* Use automated tooling such as OWASP ZAP
* Understand the difference between technical vulnerabilities and business logic vulnerabilities
* Practice fixing vulnerabilities after exploitation

This project should only be run locally for educational purposes.

---

# Technology Stack

The application currently uses:

* Python
* Flask
* SQLite
* HTML/CSS
* Jinja templates

---

# !!!Warning!!!

This application is intentionally insecure.

It should:

* ONLY be run locally
* NEVER be exposed to the internet
* NEVER be used with real credentials
* NEVER be deployed to production

The vulnerabilities are intentional and designed for learning.

---

# Application Features

The site currently contains:

* User registration
* Login/logout
* User profiles
* Admin panel
* File uploads
* File deletion
* User management
* Search page
* Custom cookie-based authentication

---

# Intentionally Included Vulnerabilities

## 1. SQL Injection

### Description

The login route constructs SQL queries using string interpolation instead of parameterized queries.

Example vulnerable pattern:

```python
query = f"SELECT ... WHERE username = '{username}' AND password = '{password}'"
```

### Impact

Attackers may:

* Bypass authentication
* Manipulate queries
* Access unauthorized data
* Potentially modify or delete database content

### OWASP ZAP Detected

* SQL injection on the login form

### OWASP ZAP Missed

* how authentication logic worked
* the full privilege escalation chain
* the role of the custom cookie system

---

## 2. Reflected Cross-Site Scripting (XSS)

### Description

The search page renders user-controlled input using:

```html
{{ q|safe }}
```

This disables Jinja autoescaping.

### Impact

Attackers may execute arbitrary JavaScript in the victim's browser.

Potential consequences:

* Cookie theft
* Account takeover
* Request forgery
* Defacement
* Browser-based attacks

### OWASP ZAP Detected

ZAP successfully detected reflected XSS.

### OWASP ZAP Missed

* the relationship between XSS and readable cookies
* how XSS could lead to privilege escalation

---

## 3. Stored XSS via File Uploads

### Description

The upload system allows arbitrary HTML files to be uploaded and served back from the same origin.

Example:

```html
<script>alert(document.cookie)</script>
```

### Impact

This allows:

* Persistent XSS
* Malicious HTML hosting
* Same-origin script execution
* Credential theft simulations

### OWASP ZAP Detected

ZAP partially detected HTML/XSS-related issues.

### OWASP ZAP Missed

* upload → execute attack chains
* stored XSS persistence
* the relationship between uploads and authentication

---

## 4. Cookie Poisoning / Privilege Escalation

### Description

The application intentionally uses an insecure custom cookie format:

```text
user_id|username|role
```

The application trusts client-controlled cookie contents directly.

The cookie is parsed using:

```python
parts = cookie.split("|")
```

### Impact

Attackers may:

* Manipulate authorization
* Escalate privileges
* Access admin functionality

### Example Concept

A crafted username containing delimiter characters may alter how the server interprets the cookie.

### OWASP ZAP Detected

ZAP detected:

* Cookie poisoning
* Missing cookie protections

### OWASP ZAP Missed

* the delimiter injection logic
* privilege escalation semantics
* how admin access was obtained

---

## 5. Missing CSRF Protection

### Description

State-changing POST requests do not use CSRF tokens.

Examples:

* delete user
* change role
* upload deletion

### Impact

Attackers may trick authenticated users into performing actions they did not intend.

### OWASP ZAP Detected

ZAP successfully detected missing CSRF protections.

### OWASP ZAP Missed

* which actions are sensitive
* the business impact of admin-only actions

---

## 6. Weak Session Security

### Description

The application intentionally disables several cookie protections.

Examples:

```python
SESSION_COOKIE_HTTPONLY=False
```

and:

```python
httponly=False
```

### Impact

JavaScript can access authentication cookies.

This makes XSS significantly more dangerous.

### OWASP ZAP Detected

ZAP successfully detected:

* missing HttpOnly
* missing SameSite

---

## 7. Potential Path Traversal

### Description

Depending on the current implementation of file viewing, path traversal vulnerabilities may exist.

Unsafe implementations using:

```python
open(os.path.join(...))
```

may allow escaping intended directories.

### Impact

Attackers may read unauthorized files.

### OWASP ZAP Detected

ZAP heuristically suspected path traversal.

### OWASP ZAP Missed

ZAP did not fully verify exploitation logic.

---

# OWASP ZAP Results Summary

## Vulnerabilities Successfully Detected

ZAP successfully identified:

* SQL Injection
* Reflected XSS
* Missing CSRF Tokens
* Cookie Security Problems
* Missing Security Headers
* Cookie Poisoning Indicators
* Potential Path Traversal

## Vulnerabilities Partially Detected

ZAP partially understood:

* Upload-based XSS
* Session manipulation
* Authorization issues

## Vulnerabilities ZAP Mostly Missed

ZAP struggled with:

* Business logic flaws
* Privilege escalation chains
* Delimiter injection
* Multi-stage attacks
* Authorization semantics

---

# Why Automated Scanners Miss Some Vulnerabilities

Automated scanners are very good at:

* Input fuzzing
* Injection testing
* Missing security headers
* Known vulnerability patterns

However, scanners are much worse at:

* Understanding application logic
* Understanding user roles
* Understanding authorization intent
* Chaining vulnerabilities together
* Multi-step exploitation

This lab intentionally demonstrates the importance of manual reasoning.

---

# Recommended Learning Workflow

1. Install and familiarize yourself with the lab
2. Attempt exercises
3. Run tooling such as OWASP ZAP
4. Attempt to fix the vulnerabilities
5. Celebrate your knewfound knowledge

---

# Suggested Future Improvements

Potential future additions:

* Rate limiting vulnerabilities
* Insecure password storage
* Session fixation
* IDOR (Insecure Direct Object Reference)
* Clickjacking
* SSTI (Server-Side Template Injection)
* JWT vulnerabilities
* OAuth misconfiguration

---

# Defensive Exercises

After exploitation, attempt to fix vulnerabilities.

Examples:

* Parameterized SQL queries
* Escaping HTML output
* Re-enabling Jinja autoescaping
* Using signed sessions
* Adding CSRF tokens
* Using secure cookie settings
* Using `secure_filename()`
* Validating paths safely
* Re-checking roles server-side

---

# Important Security Lessons

## Never Trust Client Input

This includes:

* form data
* URLs
* cookies
* uploaded files
* headers

## Authorization Must Be Server-Side

The server should never trust user-controlled authorization state.

## Vulnerabilities Chain Together

Small vulnerabilities often become dangerous when combined.

Examples:

```text
XSS → cookie theft → privilege escalation
```

or:

```text
SQL injection → auth bypass → admin access
```

## Automated Tools Are Not Enough

Real security testing combines:

* automated scanning
* manual testing
* business logic analysis
* human reasoning

---

# Suggested Tools

## OWASP ZAP

Used in this project for:

* automated scanning
* fuzzing
* request inspection
* vulnerability discovery

## Burp Suite

Recommended next step for:

* manual request manipulation
* session tampering
* replay attacks
* advanced testing

---

# Ethical Use

This lab exists for:

* education
* defensive learning
* local experimentation

Do not use these techniques against systems you do not own or have permission to test.
