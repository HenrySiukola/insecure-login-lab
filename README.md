# Insecure Login Lab

Insecure Login Lab is a deliberately vulnerable Flask web application designed for learning web application security concepts in a safe local environment.

The lab contains intentionally insecure implementations of:

- SQL Injection
- Cross-Site Scripting (XSS)
- CSRF
- Cookie poisoning
- Privilege escalation
- Weak session management
- Insecure file uploads

## !!!Warning!!!

This application is intentionally insecure.

- Run locally only
- Do not expose to the internet
- Do not use real credentials
- Do not deploy to production

## Requirements

- Python 3.12+
- pip

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd insecure-login
```

---

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python
```

```python
from app.db import init_db
init_db()
exit()
```

## Running the Application

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

## Additional Documentation

- `documentation.md` → technical details and vulnerability explanations
- `exercises.md` → guided exercises and hints

## Recommended Tools

- OWASP ZAP
- Burp Suite Community Edition

## Ethical Use

This project exists for education and defensive learning only.

Do not test systems you do not own or have permission to test.