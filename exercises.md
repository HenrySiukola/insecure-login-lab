# Insecure Login Lab Exercises

This document contains practical exercises for exploring the intentionally vulnerable functionality in Insecure Login Lab.

The exercises are ordered roughly from easiest to hardest.

All exercises should only be performed locally against the intentionally vulnerable lab environment.

---

# Exercise 1 — Basic SQL Injection

## Objective and Learning Goals

Attempt to bypass login authentication using SQL injection.

- Understand SQL injection basics
- Learn why parameterized queries matter
- See how authentication bypasses work

---

## Background

The login route constructs SQL queries directly from user input.

Improper query construction may allow attackers to manipulate query logic.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Inspect how the SQL query is built.

</details>

<details>
<summary>Hint 2</summary>

What happens if user input changes the structure of the WHERE clause?

</details>

<details>
<summary>Hint 3</summary>

Observe the SQL query printed in the server logs.

</details>

<details>
<summary>Exploit</summary>

Login using the following as username:
```text
' OR '1'='1' --
```
Password can be anything.

This SQL injection modifies the constructed SQL query so that the authentication condition always evaluates to true, allowing the attacker to bypass the password check and log in as the first matching user.


</details>

---

# Exercise 2 — Reflected Cross-Site Scripting (XSS)

## Objective and Learning Goals

Execute JavaScript through the search page.

- Understand reflected XSS
- Learn how template escaping works
- Understand why `|safe` is dangerous

---

## Background

The search feature intentionally disables Jinja escaping.

User input is reflected directly into HTML output.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Inspect how the search result is rendered.

</details>

<details>
<summary>Hint 2</summary>

Does the template escape user input?

</details>

<details>
<summary>Hint 3</summary>

Test whether HTML is interpreted or displayed literally.

</details>

<details>
<summary>Exploit</summary>

Search using the following payload:

```html
<script>alert('XSS')</script>
```

The application renders the search query directly into the page without escaping HTML, causing the browser to execute attacker-controlled JavaScript.

</details>

---


# Exercise 3 — Stored XSS via File Uploads

## Objective and Learning Goals

Upload content that executes JavaScript when viewed.

- Understand stored XSS
- Learn how upload systems become dangerous
- Understand same-origin implications

---

## Background

The upload system allows arbitrary files to be uploaded and served from the same origin.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

What file types are accepted?

</details>

<details>
<summary>Hint 2</summary>

How are uploaded files displayed?

</details>

<details>
<summary>Hint 3</summary>

Can uploaded HTML execute scripts?

</details>

<details>
<summary>Exploit</summary>

Upload an HTML file containing:

```html
<script>alert(document.cookie)</script>
```

When the uploaded file is viewed, the browser executes the embedded JavaScript because uploaded HTML files are served directly from the application's origin.

</details>

---

# Exercise 4 — Cookie Analysis

## Objective and Learning Goals

Understand how authentication cookies are structured.

- Understand client-controlled state
- Learn how cookies influence authentication
- Understand why cookie integrity matters

---

## Background

The application uses a custom authentication cookie format.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Inspect browser cookies.

</details>

<details>
<summary>Hint 2</summary>

How is the authentication cookie formatted?

</details>

<details>
<summary>Hint 3</summary>

Does the server trust cookie contents directly?

</details>

<details>
<summary>Exploit</summary>

Inspect the browser cookies using developer tools.

The application stores authentication state in a custom cookie formatted as:

```text
user_id|username|role
```

Because the server trusts this client-controlled cookie directly, modifying its structure can influence authorization behavior.

</details>

---

# Exercise 5 — Privilege Escalation via Cookie Manipulation

## Objective and Learning Goals

Gain access to the admin page without a legitimate admin account.

- Understand insecure authorization
- Learn delimiter injection concepts
- Understand privilege escalation logic flaws

---

## Background

The application trusts fields parsed from a custom cookie.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Look at how the cookie is parsed.

</details>

<details>
<summary>Hint 2</summary>

What separates the fields?

</details>

<details>
<summary>Hint 3</summary>

Can user-controlled input affect the structure of the cookie?

</details>

<details>
<summary>Exploit</summary>

Create an account with a username containing a delimiter:

```text
alice|admin
```

The application inserts the username directly into the authentication cookie and later parses the cookie using `split('|')`.

This causes the server to misinterpret the cookie fields and incorrectly assign the `admin` role to the attacker.

</details>

---

# Exercise 6 — Cross-Site Request Forgery (CSRF)

## Objective and Learning Goals

Trigger a state-changing action from another page.

- Understand CSRF fundamentals
- Learn how browsers automatically send cookies
- Understand why CSRF tokens exist

---

## Background

The application does not use CSRF tokens for POST requests.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Inspect forms that modify application state.

</details>

<details>
<summary>Hint 2</summary>

Do requests contain unpredictable validation tokens?

</details>

<details>
<summary>Hint 3</summary>

What information does the browser automatically send with requests?

</details>

<details>
<summary>Exploit</summary>

Create a malicious HTML page containing a form that automatically submits a POST request to the vulnerable application.

When a logged-in victim visits the malicious page, the browser automatically includes the victim's authentication cookies, causing the application to perform unintended actions without the victim's consent.

</details>

---

# Exercise 7 — Cookie Theft via XSS

## Objective and Learning Goals

Understand how XSS and insecure cookie settings interact.

- Understand HttpOnly cookies
- Understand XSS impact escalation
- Learn how XSS can affect session security

---

## Background

The application intentionally disables several cookie protections.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Can JavaScript access cookies?

</details>

<details>
<summary>Hint 2</summary>

What browser protections normally prevent this?

</details>

<details>
<summary>Hint 3</summary>

Inspect cookie settings in the application configuration.

</details>

<details>
<summary>Exploit</summary>

Execute the following JavaScript through an XSS vulnerability:

```html
<script>alert(document.cookie)</script>
```

Because the authentication cookie is not protected with the `HttpOnly` flag, JavaScript can access it directly, allowing attackers to steal session information.

</details>

---

# Exercise 8 — Path Traversal Investigation

## Objective and Learning Goals

Investigate whether uploaded file access can escape intended directories.

- Understand path traversal concepts
- Learn why path validation is difficult
- Understand safe file-serving practices

---

## Background

Improper file path handling may allow access outside intended directories.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

How are file paths constructed?

</details>

<details>
<summary>Hint 2</summary>

What does `../` represent?

</details>

<details>
<summary>Hint 3</summary>

Does the application validate resolved paths?

</details>

<details>
<summary>Solution</summary>

Attempt to access files outside the intended upload directory using path traversal sequences such as:

```text
../
```

If file paths are constructed insecurely without proper validation, attackers may escape the intended directory and access unauthorized files.

</details>

---

# Exercise 9 — Automated Security Scanning with OWASP ZAP

## Objective and Learning Goals

Use OWASP ZAP to identify vulnerabilities in the application.

- Learn basic vulnerability scanning
- Understand scanner strengths and weaknesses
- Learn authenticated scanning concepts

---

## Background

Automated scanners can identify many common vulnerability patterns.

---

## Hints and Solution

<details>
<summary>Hint 1</summary>

Run both unauthenticated and authenticated scans.

</details>

<details>
<summary>Hint 2</summary>

Use the browser through the ZAP proxy.

</details>

<details>
<summary>Hint 3</summary>

Compare scanner findings against known vulnerabilities.

</details>

---

# Exercise 10 — Manual Security Testing

## Objective and Learning Goals

Identify vulnerabilities that automated scanners miss.

- Understand business logic vulnerabilities
- Learn manual testing techniques
- Understand multi-stage attack chains

---

## Background

Many important vulnerabilities involve business logic and authorization semantics.

---

## Hints and Exploit

<details>
<summary>Hint 1</summary>

Inspect how roles are determined.

</details>

<details>
<summary>Hint 2</summary>

Observe relationships between cookies and authorization.

</details>

<details>
<summary>Hint 3</summary>

Think about how vulnerabilities may chain together.

</details>

---

# Suggested Remediation Exercises

After completing exploitation exercises, attempt to fix vulnerabilities.

Examples:

- Replace vulnerable SQL queries with parameterized queries
- Re-enable HTML escaping
- Add CSRF protection
- Use signed sessions
- Enable HttpOnly cookies
- Add SameSite protection
- Use secure file handling
- Validate paths safely
- Re-check authorization server-side

---

# Final Learning Objective

The most important goal of this lab is understanding that:

```text
Real security testing combines:
- automated tooling
- manual analysis
- understanding application logic
- understanding how vulnerabilities chain together
```
