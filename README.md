# 🛡️ Python Security & Software Projects

A collection of practical Python projects focused on **cybersecurity, cryptography, networking, secure software development, automation, and defensive security**.

This repository is the second phase of my Python learning journey.

Instead of focusing only on small utilities, this phase focuses on building larger, more security-conscious applications while learning how to design, test, and improve software with security in mind.

---

## 🚀 About This Repository

The goal of this repository is to move from basic Python scripting toward more advanced:

- 🐍 Python development
- 🔐 Cryptography
- 🛡️ Cybersecurity
- 🌐 Networking
- 🔑 Authentication
- 💾 Database development
- 🔒 Secure data storage
- 🧪 Security testing
- 🏗️ Software architecture
- 🤖 Security automation
- 📊 Monitoring and detection

Each project is designed to solve a practical problem while introducing new software development and security concepts.

---

# 📂 Projects

| # | Project | Description | Technologies | Status |
|---|---|---|---|---|
| 01 | 🔐 Secure Password Manager | Local encrypted password vault using Argon2id and AES-256-GCM | Python, SQLite, Cryptography | 🚧 Development |
| 02 | 🧪 Vulnerability Scanner | Coming soon | Python, Networking, Security | 🔜 Coming Soon |
| 03 | 📡 Network Monitor | Coming soon | Python, Networking | 🔜 Coming Soon |
| 04 | 🔐 Secure File Transfer | Coming soon | Python, Sockets, Cryptography | 🔜 Coming Soon |
| 05 | 🌐 Security REST API | Coming soon | Python, FastAPI/Flask, REST | 🔜 Coming Soon |
| 06 | 📊 Security Dashboard | Coming soon | Python, Database, Visualization | 🔜 Coming Soon |
| 07 | 🔑 Authentication API | Coming soon | Python, JWT, Authentication | 🔜 Coming Soon |
| 08 | 🧰 Security Automation Toolkit | Coming soon | Python, Cybersecurity | 🔜 Coming Soon |
| 09 | 📝 SIEM-Style Log Monitor | Coming soon | Python, Logging, Detection | 🔜 Coming Soon |
| 10 | 🚀 Full-Stack Security Project | Coming soon | Python, Web, Security | 🔜 Coming Soon |

> Projects will be added progressively as I learn and build them.

---

# 🔐 Project 01 — Secure Password Manager

The first project in this phase is a local encrypted password manager.

It securely stores credentials inside an encrypted SQLite vault.

### Security architecture

```text
                     Master Password
                            │
                            ▼
                    ┌──────────────┐
                    │   Argon2id   │
                    │              │
                    │ 19 MiB       │
                    │ 2 iterations │
                    │ 1 lane       │
                    └──────┬───────┘
                           │
                           ▼
                      256-bit Key
                           │
                           ▼
                    ┌──────────────┐
                    │  AES-256-GCM │
                    │     AEAD     │
                    └──────┬───────┘
                           │
                           ▼
                    Encrypted Vault
                           │
                           ▼
                         SQLite
````

### Main features

* 🔑 Master password authentication
* 🔐 Argon2id key derivation
* 🛡️ AES-256-GCM encryption
* 🧂 Random cryptographic salt
* 🔄 Fresh encryption nonce
* 💾 SQLite storage
* ➕ Credential management
* 🔎 Credential search
* 🎲 Secure password generation
* 🔄 Master password rotation
* 🗑️ Credential deletion
* ✅ Vault integrity verification
* 🔒 POSIX file permission protection
* 🚫 No plaintext master password storage

---

# 🧠 Security Philosophy

Security is treated as part of the development process rather than something added at the end.

The projects in this repository aim to follow principles such as:

### 🔐 Secure by Design

Security requirements are considered while designing the application.

### 🛡️ Defense in Depth

Multiple security controls are used instead of relying on a single protection mechanism.

### 🔑 Least Privilege

Applications should operate with the minimum privileges required.

### 🚫 Secure Defaults

The safest reasonable behavior should be the default behavior.

### 🧂 Cryptographically Secure Randomness

Security-sensitive random values should use appropriate cryptographic randomness.

### 🔒 Established Cryptography

The projects use established cryptographic libraries and algorithms rather than implementing cryptographic primitives manually.

### 🧪 Security Testing

Projects are tested not only for expected functionality but also for failure cases and security weaknesses.

---

# 🛠️ Technologies

Technologies used throughout the repository will include:

```text
Python
SQLite
Sockets
HTTP/HTTPS
Cryptography
Argon2id
AES-GCM
REST APIs
JWT
Regular Expressions
Logging
JSON
CLI Development
Automation
Databases
Testing
```

Technologies will be introduced as required by individual projects.

---

# 📈 Learning Roadmap

The repository follows a progression from individual security components toward larger applications.

```text
Python Development
        │
        ▼
Secure Data Handling
        │
        ▼
Cryptography
        │
        ▼
Authentication
        │
        ▼
Networking
        │
        ▼
Security Automation
        │
        ▼
Monitoring & Detection
        │
        ▼
Secure APIs
        │
        ▼
Security Applications
        │
        ▼
Full-Stack Security Project
```

---

# 🎯 Skills I'm Building

## 🐍 Python Development

* Functions
* Classes
* Type hints
* Exception handling
* CLI applications
* Modules and packages
* File handling
* Database integration
* Testing

## 🔐 Cybersecurity

* Secure password handling
* Authentication
* Authorization
* Cryptography
* Encryption
* Hashing
* Network security
* Vulnerability assessment
* Security monitoring
* Threat detection

## 🌐 Networking

* TCP/IP
* Sockets
* HTTP/HTTPS
* DNS
* Network services
* Client/server architecture
* Network monitoring

## 🏗️ Software Development

* Application architecture
* Database design
* API development
* Input validation
* Error handling
* Secure coding
* Testing
* Documentation

---

# 🧪 Development Approach

Each project follows a practical development workflow:

```text
1. Define the problem
        ↓
2. Design the application
        ↓
3. Identify security requirements
        ↓
4. Build the core functionality
        ↓
5. Test normal behavior
        ↓
6. Test failure cases
        ↓
7. Test security controls
        ↓
8. Improve the implementation
        ↓
9. Document the project
        ↓
10. Publish the project
```

The goal is to learn how to build software that is not only functional, but also designed with security considerations from the beginning.

---

# 📁 Repository Structure

```text
python-security-software-projects/
│
├── 01_secure_password_manager/
│   ├── password_manager.py
│   ├── requirements.txt
│   ├── .gitignore
│   └── README.md
│
├── 02_vulnerability_scanner/
│   └── ...
│
├── 03_network_monitor/
│   └── ...
│
├── 04_secure_file_transfer/
│   └── ...
│
└── README.md
```

Each project contains its own README with:

* Project overview
* Features
* Installation
* Usage
* Security architecture
* Security considerations
* Testing
* Limitations
* Future improvements

---

# ⚙️ General Requirements

Most projects will require:

* Python 3.9+
* Git
* A terminal
* Basic Python knowledge

Individual projects may have additional dependencies.

Always check the project's own `README.md` before running it.

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Avinash-05-web/python-security-software-projects.git
```

Enter the repository:

```bash
cd python-security-software-projects
```

Then enter the project you want to run.

For example:

```bash
cd 01_secure_password_manager
```

Follow that project's README for installation and usage instructions.

---

# 🔒 Security & Privacy

Projects in this repository may handle sensitive information during testing.

Important rules:

* Never commit passwords.
* Never commit API keys.
* Never commit authentication tokens.
* Never commit private keys.
* Never commit real production credentials.
* Never upload real password-manager vaults.
* Use test accounts whenever possible.
* Keep `.env` and credential files out of Git.
* Review files before uploading them to GitHub.

---

# ⚠️ Ethical & Legal Disclaimer

The cybersecurity projects in this repository are intended for **educational, defensive, and authorized security testing purposes**.

Only use security tools against systems, networks, applications, and accounts that you own or have explicit permission to test.

Do not use these projects for:

* Unauthorized access
* Credential theft
* Malware deployment
* Data theft
* Denial-of-service attacks
* Unauthorized scanning
* Privacy violations
* Any other illegal activity

Understanding cybersecurity also means understanding responsible and ethical use.

---

# 📊 Project Progress

| Phase   | Focus                        | Projects |
| ------- | ---------------------------- | -------: |
| Phase 1 | Python Mini Projects         |     13 ✅ |
| Phase 2 | Security & Software Projects |     1 🚧 |

### Phase 1

**Python Mini Projects**

Completed with 13 practical projects covering:

* Python fundamentals
* Automation
* Networking
* GUI development
* CLI applications
* Cryptography
* Hashing
* Log analysis
* Defensive security

### Phase 2

**Python Security & Software Projects**

Current focus:

* Cybersecurity
* Secure software development
* Cryptography
* Authentication
* Networking
* Security automation
* Larger applications

---

# 🎯 Current Milestone

```text
Phase 2
   │
   └── Project 01
          │
          └── 🔐 Secure Password Manager
                    │
                    ├── Argon2id
                    ├── AES-256-GCM
                    ├── SQLite
                    ├── Secure Password Generation
                    └── Encrypted Vault
```

**Current status: 🚧 Development**

---

# 🚀 Future Goals

The long-term goal of this repository is to progress from individual security utilities to complete security-focused applications.

Eventually, I want to build projects involving:

* Secure APIs
* Authentication systems
* Network monitoring
* Vulnerability assessment
* Security automation
* Log monitoring
* Threat detection
* Databases
* Web applications
* Full-stack security systems

The focus is on understanding both **how software works and how software can fail from a security perspective**.

---

# 👨‍💻 Author

**Avinash Das Manikpuri**

GitHub:

```text
https://github.com/Avinash-05-web
```

---

# ⭐ Why This Repository?

This repository documents my transition from learning Python fundamentals to building practical cybersecurity and software engineering projects.

The objective is not simply to collect projects.

It is to build the ability to:

```text
Understand
    ↓
Design
    ↓
Build
    ↓
Test
    ↓
Break
    ↓
Secure
    ↓
Improve
```

---

# 🔥 Learning Philosophy

> Build real projects.
> Understand the technology.
> Think like an attacker.
> Defend like an engineer.
> Keep improving.

**Build. Learn. Secure. Improve. Repeat. 🚀**
