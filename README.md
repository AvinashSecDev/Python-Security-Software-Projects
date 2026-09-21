# 🛡️ Python Security & Software Projects

A collection of practical Python projects focused on **cybersecurity, cryptography, networking, secure software development, automation, and defensive security**.

This repository is the second phase of my Python learning journey.

Instead of focusing only on small utilities, this phase focuses on building larger, more security-conscious applications while learning how to design, test, and improve software with security in mind.

---

## 🚀 About This Repository

The goal of this repository is to move from basic Python scripting toward more advanced:

* 🐍 Python development
* 🔐 Cryptography
* 🛡️ Cybersecurity
* 🌐 Networking
* 🔑 Authentication
* 💾 Database development
* 🔒 Secure data storage
* 🧪 Security testing
* 🏗️ Software architecture
* 🤖 Security automation
* 📊 Monitoring and detection

Each project is designed to solve a practical problem while introducing new software development and security concepts.

---

# 📂 Projects

| #  | Project                        | Description                                                                            | Technologies                             | Status         |
| -- | ------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------- | -------------- |
| 01 | 🔐 Secure Password Manager     | Local encrypted password vault using Argon2id and AES-256-GCM                          | Python, SQLite, Cryptography             | 🚧 Development |
| 02 | 🧪 Vulnerability Scanner       | Defensive network and service exposure scanner with security checks and JSON reporting | Python, Networking, Sockets, TLS         | ✅ Completed    |
| 03 | 📡 Network Monitor             | Host availability, latency, packet-loss and TCP service monitoring tool                | Python, Networking, Sockets, Concurrency | ✅ Completed    |
| 04 | 🔐 Secure File Transfer        | Coming soon                                                                            | Python, Sockets, Cryptography            | 🔜 Coming Soon |
| 05 | 🌐 Security REST API           | Coming soon                                                                            | Python, FastAPI/Flask, REST              | 🔜 Coming Soon |
| 06 | 📊 Security Dashboard          | Coming soon                                                                            | Python, Database, Visualization          | 🔜 Coming Soon |
| 07 | 🔑 Authentication API          | Coming soon                                                                            | Python, JWT, Authentication              | 🔜 Coming Soon |
| 08 | 🧰 Security Automation Toolkit | Coming soon                                                                            | Python, Cybersecurity                    | 🔜 Coming Soon |
| 09 | 📝 SIEM-Style Log Monitor      | Coming soon                                                                            | Python, Logging, Detection               | 🔜 Coming Soon |
| 10 | 🚀 Full-Stack Security Project | Coming soon                                                                            | Python, Web, Security                    | 🔜 Coming Soon |

> Projects are added progressively as I learn, build, test, and improve them.

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
```

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

# 🧪 Project 02 — Vulnerability Scanner

A defensive Python-based network and service exposure scanner designed to help identify potentially risky services and basic security configuration issues on authorized systems.

The scanner focuses on **visibility and assessment rather than exploitation**.

### Main features

* 🌐 Hostname and IP resolution
* 🔌 TCP port scanning
* ⚡ Concurrent port scanning
* 🧩 Service identification
* 📡 Basic service banner collection
* ⚠️ Risky service detection
* 🌐 HTTP security-header checks
* 🔐 TLS certificate inspection
* 📝 Version/banner information analysis
* 📊 Custom risk scoring
* 💾 JSON report generation
* 🖥️ Command-line interface
* ⏱️ Configurable timeout
* ⚡ Configurable worker count

### Security checks

The scanner can identify exposure involving services such as:

* FTP
* Telnet
* SMB/NetBIOS
* MSSQL
* Oracle
* Docker API
* MySQL
* RDP
* PostgreSQL
* VNC
* Redis
* Elasticsearch
* MongoDB

It can also inspect selected HTTP security headers and TLS certificate information.

### Important distinction

The scanner does **not** claim that an open port or detected version automatically represents a confirmed vulnerability.

Findings require manual validation.

The project's risk score is a custom project-specific heuristic and is **not CVSS**.

### Technologies

```text
Python
Sockets
TCP/IP
Concurrency
HTTP/HTTPS
TLS/SSL
JSON
Argparse
Regular Expressions
```

### Project structure

```text
02_vulnerability_scanner/
│
├── vulnerability_scanner.py
├── requirements.txt
├── README.md
├── .gitignore
└── reports/
    └── .gitkeep
```

### Status

**✅ Completed**

---

# 📡 Project 03 — Network Monitor

A defensive Python-based network monitoring application designed to monitor authorized hosts, measure network latency, track packet loss, check TCP connectivity, record monitoring events, and generate JSON reports.

The project focuses on **network visibility, reliability, monitoring, and defensive security**.

### Main features

* 🌐 Multiple host monitoring
* 📡 Host availability checking
* ⏱️ Network latency measurement
* 📉 Packet-loss calculation
* 🔌 TCP port connectivity checks
* 🚨 UP/DOWN status detection
* ⚡ Concurrent monitoring
* 🔄 Continuous monitoring mode
* 🔢 Configurable monitoring cycles
* 📝 Event logging
* 📊 Monitoring statistics
* 💾 JSON report generation
* 🖥️ Command-line interface
* ⏱️ Configurable timeout
* ⚙️ Configurable monitoring interval
* 🧵 Configurable concurrent workers
* 🪟 Windows support
* 🐧 Linux support where the required system `ping` command is available

### Host Monitoring

The application uses the operating system's `ping` command to determine whether a target host is reachable.

Possible states include:

```text
UP
DOWN
ERROR
```

Successful checks can record latency in milliseconds.

### TCP Monitoring

The application can test selected TCP ports.

Example:

```bash
python network_monitor.py 127.0.0.1 --ports 22,80,443
```

Possible results include:

```text
OPEN
CLOSED
FILTERED/TIMEOUT
ERROR
```

### Continuous Monitoring

The application can continuously monitor hosts.

Example:

```bash
python network_monitor.py 127.0.0.1 -c
```

Custom interval:

```bash
python network_monitor.py 127.0.0.1 -c -i 10
```

Limited monitoring cycles:

```bash
python network_monitor.py 127.0.0.1 -c --cycles 5
```

### Monitoring Statistics

The application calculates:

* Total checks
* Successful checks
* Failed checks
* Packet loss percentage
* Average latency
* Minimum latency
* Maximum latency

### Logging

Monitoring events are stored locally in:

```text
logs/network_monitor.log
```

Events can include:

```text
HOST UP
HOST DOWN
HOST ERROR
PORT OPEN
REPORT SAVED
MONITORING STOPPED
```

### JSON Reporting

Results can be exported as structured JSON:

```bash
python network_monitor.py 127.0.0.1 --report reports/local_scan.json
```

Reports may contain IP addresses, hostnames, port information, and other infrastructure details, so generated reports should not be uploaded publicly when they contain sensitive information.

### Technologies

```text
Python
Sockets
TCP/IP
Subprocess
ThreadPoolExecutor
Argparse
JSON
Dataclasses
Regular Expressions
File I/O
Logging
```

### Project structure

```text
03_network_monitor/
│
├── network_monitor.py
├── requirements.txt
├── README.md
│
├── reports/
│   └── .gitkeep
│
└── logs/
    └── .gitkeep
```

### Security scope

The Network Monitor is designed for:

* Network administration
* Defensive monitoring
* Authorized testing
* Personal labs
* Virtual machines
* Systems owned by the user

It does not perform:

* Exploitation
* Credential attacks
* Packet injection
* Password capture
* Traffic interception
* Vulnerability exploitation

### Status

**✅ Completed**

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

### 📊 Monitoring & Visibility

Security also requires understanding what is happening within systems and networks.

Monitoring projects are designed to provide visibility into:

* Availability
* Network latency
* Service connectivity
* Logs
* Security events
* System behavior

---

# 🛠️ Technologies

Technologies used throughout the repository include:

```text
Python
SQLite
Sockets
TCP/IP
HTTP/HTTPS
TLS/SSL
Cryptography
Argon2id
AES-GCM
REST APIs
JWT
Regular Expressions
Logging
JSON
CLI Development
Concurrency
ThreadPoolExecutor
Automation
Databases
Testing
```

Technologies are introduced as required by individual projects.

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
* JSON serialization
* Concurrency
* Thread pools

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
* Security configuration analysis

## 🌐 Networking

* TCP/IP
* Sockets
* HTTP/HTTPS
* TLS/SSL
* DNS
* TCP connectivity
* Network latency
* Packet loss
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
* CLI application development
* Structured reporting

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
Python-Security-Software-Projects/
│
├── 01_secure_password_manager/
│   ├── password_manager.py
│   ├── requirements.txt
│   ├── .gitignore
│   └── README.md
│
├── 02_vulnerability_scanner/
│   ├── vulnerability_scanner.py
│   ├── requirements.txt
│   ├── .gitignore
│   ├── README.md
│   └── reports/
│       └── .gitkeep
│
├── 03_network_monitor/
│   ├── network_monitor.py
│   ├── requirements.txt
│   ├── README.md
│   ├── reports/
│   │   └── .gitkeep
│   └── logs/
│       └── .gitkeep
│
├── 04_secure_file_transfer/
│   └── ...
│
├── 05_security_rest_api/
│   └── ...
│
├── 06_security_dashboard/
│   └── ...
│
├── 07_authentication_api/
│   └── ...
│
├── 08_security_automation_toolkit/
│   └── ...
│
├── 09_siem_style_log_monitor/
│   └── ...
│
├── 10_full_stack_security_project/
│   └── ...
│
└── README.md
```

Each project contains its own README with:

* Project overview
* Features
* Installation
* Usage
* Architecture
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

The repository can be downloaded or cloned from GitHub.

Repository:

```text
https://github.com/AvinashSecDev/Python-Security-Software-Projects
```

If using Git:

```bash
git clone https://github.com/AvinashSecDev/Python-Security-Software-Projects.git
```

Enter the repository:

```bash
cd Python-Security-Software-Projects
```

Then enter the project you want to run.

For example:

```bash
cd 03_network_monitor
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
* Never upload real network monitoring logs containing sensitive infrastructure information.
* Never upload real security scan reports containing sensitive infrastructure information.
* Use test accounts whenever possible.
* Keep `.env` and credential files out of Git.
* Review files before uploading them to GitHub.

Security tools should be used only against systems and networks where authorization exists.

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
* Unauthorized network monitoring
* Any other illegal activity

Understanding cybersecurity also means understanding responsible and ethical use.

---

# 📊 Project Progress

| Phase   | Focus                        |   Progress |
| ------- | ---------------------------- | ---------: |
| Phase 1 | Python Mini Projects         |  13 / 13 ✅ |
| Phase 2 | Security & Software Projects | 2 ✅ / 1 🚧 |

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

Current progress:

* 🔐 Project 01 — Secure Password Manager — 🚧 Development
* 🧪 Project 02 — Vulnerability Scanner — ✅ Completed
* 📡 Project 03 — Network Monitor — ✅ Completed
* 🔐 Project 04 — Secure File Transfer — 🔜 Coming Soon
* 🌐 Project 05 — Security REST API — 🔜 Coming Soon
* 📊 Project 06 — Security Dashboard — 🔜 Coming Soon
* 🔑 Project 07 — Authentication API — 🔜 Coming Soon
* 🧰 Project 08 — Security Automation Toolkit — 🔜 Coming Soon
* 📝 Project 09 — SIEM-Style Log Monitor — 🔜 Coming Soon
* 🚀 Project 10 — Full-Stack Security Project — 🔜 Coming Soon

---

# 🎯 Current Milestone

```text
Phase 2
   │
   ├── Project 01
   │      └── 🔐 Secure Password Manager
   │             └── 🚧 Development
   │
   ├── Project 02
   │      └── 🧪 Vulnerability Scanner
   │             └── ✅ Completed
   │
   └── Project 03
          └── 📡 Network Monitor
                 └── ✅ Completed
```

### Current focus

The next major focus is completing:

```text
Project 01 — Secure Password Manager
```

After that, the roadmap continues toward secure file transfer, APIs, monitoring dashboards, authentication systems, security automation, SIEM-style monitoring, and eventually a larger full-stack security application.

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
https://github.com/AvinashSecDev
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
