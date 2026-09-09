# 🔐 Secure Password Manager

A local, security-focused password manager built with Python.

This project securely stores website credentials inside an encrypted local vault using **Argon2id for password-based key derivation** and **AES-256-GCM for authenticated encryption**.

The project is designed as a hands-on cybersecurity and secure software development project, with an emphasis on proper cryptographic primitives, secure password handling, input validation, data integrity, and minimizing sensitive data exposure.

> ⚠️ This is an educational/local security project and has not undergone an independent security audit. It should not be considered equivalent to a professionally audited production password manager.

---

## ✨ Features

- 🔑 Master password protected vault
- 🧂 Cryptographically secure random salt
- 🔐 Argon2id key derivation
- 🛡️ AES-256-GCM authenticated encryption
- 🔄 Fresh encryption nonce for every vault save
- 💾 Encrypted SQLite-based vault
- ➕ Add credentials
- 📋 List stored credentials
- 🔎 Search credentials
- 👁️ Explicit password reveal
- 🗑️ Delete credentials
- 🔄 Change master password
- 🎲 Cryptographically secure password generator
- ✅ Vault integrity/authentication checks
- ⏳ Progressive delay after failed unlock attempts
- 🔒 POSIX vault file permissions (`0600`)
- 🧹 No plaintext master password storage
- 🚫 No arbitrary shell command execution
- 📦 No external database server required
- 🐍 Python standard library + `cryptography`

---

# 🛡️ Security Architecture

The application follows this basic architecture:

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

The master password is used to derive an encryption key.

The derived key encrypts the complete vault using AES-256-GCM.

The SQLite database stores encrypted data and cryptographic metadata rather than individual plaintext credentials.

---

# 🔐 Cryptography

## Argon2id

The master password is processed using **Argon2id**, a memory-hard password-based key derivation function.

The project uses:

```text
Memory:     19 MiB
Iterations: 2
Parallelism: 1
Key size:   256 bits
Salt:       16 random bytes
```

These parameters are based on the OWASP Password Storage Cheat Sheet's Argon2id baseline.

Argon2id is intentionally more expensive than a fast hash such as SHA-256, making large-scale password guessing more expensive.

---

## AES-256-GCM

Vault data is encrypted using:

```text
AES-256-GCM
```

GCM provides:

* Confidentiality
* Authentication
* Integrity protection

If an attacker modifies the encrypted vault, authentication should fail rather than silently returning modified plaintext.

A fresh random nonce is generated for each vault encryption operation.

---

## Randomness

The project uses Python's:

```python
secrets
```

module for security-sensitive random values.

It is used for:

* Encryption salts
* AES-GCM nonces
* Credential IDs
* Generated passwords

The insecure `random` module is not used for cryptographic purposes.

---

# 🔑 Master Password

The master password is the root secret protecting the vault.

The application:

* Does not store the master password
* Does not write the master password to the database
* Does not intentionally log the master password
* Does not transmit the master password over a network

The master password must contain at least:

```text
15 characters
```

Long passphrases are recommended.

Example format:

```text
correct-horse-battery-staple-example
```

Do not use this example as your real password.

---

# ⚠️ Master Password Recovery

There is intentionally **no password recovery mechanism**.

If you lose the master password, the encrypted vault cannot normally be decrypted.

This is an important property of an offline encrypted vault.

Therefore:

> **Never forget your master password.**

---

# 📁 Project Structure

```text
01_secure_password_manager/
│
├── password_manager.py
├── requirements.txt
├── .gitignore
└── README.md
```

The application automatically creates the vault in:

```text
~/.secure_password_manager/vault.db
```

The exact location depends on the operating system and user's home directory.

---

# ⚙️ Requirements

## Software

* Python 3.9+
* `cryptography`

Supported environments:

* Windows
* Linux
* macOS

No database server is required.

SQLite is included with Python.

---

# 📦 Installation

Open a terminal inside the project directory.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

If your system uses `python3`:

```bash
python3 -m pip install -r requirements.txt
```

Verify the installation:

```bash
python -c "import cryptography; print(cryptography.__version__)"
```

---

# 🚀 Getting Started

## 1. Display Help

Run:

```bash
python password_manager.py --help
```

You should see the available commands.

---

# 🔐 2. Create the Vault

Run:

```bash
python password_manager.py init
```

The application will ask:

```text
Create master password:
Confirm master password:
```

Enter a strong master password.

The vault will then be created automatically.

Example:

```text
Creating a new secure vault.

Create master password:
Confirm master password:

Vault created successfully.
Vault: /home/user/.secure_password_manager/vault.db

IMPORTANT: The master password is not stored.
If you lose it, the encrypted vault cannot be recovered.
```

---

# ➕ 3. Add a Credential

Run:

```bash
python password_manager.py add
```

The application asks for information such as:

```text
Service / website name:
Username/email:
URL (optional):
Notes (optional):
Generate a secure password? [Y/n]:
```

If you choose to generate a password, the application uses Python's `secrets` module.

Example:

```text
Service / website name: Test Website
Username/email: test@example.com
URL (optional): https://example.com
Notes (optional):
Generate a secure password? [Y/n]: y
Password length [24]: 24
```

A cryptographically secure password will be generated.

---

# 📋 4. List Credentials

Run:

```bash
python password_manager.py list
```

Example:

```text
ID                                 NAME
--------------------------------------------------------------------------------
4c4d2a...                          Test Website
a8d193...                          GitHub

Total entries: 2
```

The password itself is not displayed.

---

# 🔎 5. Search Credentials

Search by service name, username, or URL.

Example:

```bash
python password_manager.py search github
```

Example output:

```text
ID                                 NAME                           USERNAME
----------------------------------------------------------------------------------------------------
a8d193...                          GitHub                         example@email.com

Matches: 1
```

---

# 👁️ 6. View a Credential

First obtain the credential ID using:

```bash
python password_manager.py list
```

Then:

```bash
python password_manager.py show ENTRY_ID
```

Example:

```bash
python password_manager.py show a8d193...
```

The application displays information about the credential without revealing the password.

---

# 🔓 7. Reveal a Password

If you intentionally need to see the password:

```bash
python password_manager.py show ENTRY_ID --reveal
```

The application asks for explicit confirmation:

```text
Reveal the stored password on screen? [y/N]:
```

Only after confirmation is the password displayed.

Avoid using `--reveal` when screen sharing or recording your terminal.

---

# 🗑️ 8. Delete a Credential

Find the entry ID:

```bash
python password_manager.py list
```

Then:

```bash
python password_manager.py delete ENTRY_ID
```

The application asks for confirmation before deleting the entry.

Example:

```text
Entry: GitHub
Permanently remove this credential from the vault? [y/N]:
```

---

# 🔄 9. Change Master Password

Run:

```bash
python password_manager.py change-master
```

The application asks for:

```text
Current master password:
New master password:
Confirm new master password:
```

The vault is decrypted using the old password and then re-encrypted using a newly derived key.

A new salt and encryption nonce are generated during the save.

---

# 🎲 10. Generate a Secure Password

You can use the password generator without opening the vault.

Example:

```bash
python password_manager.py generate
```

Default length:

```text
24 characters
```

Specify a custom length:

```bash
python password_manager.py generate --length 32
```

Example:

```text
python password_manager.py generate --length 40
```

The generator uses cryptographically secure randomness.

---

# ✅ 11. Check the Vault

Run:

```bash
python password_manager.py check
```

The application authenticates the vault and reports whether it can be successfully opened.

Example:

```text
Vault authentication successful.
Entries: 5
```

If the encrypted data has been corrupted or modified, authentication can fail.

---

# 🧰 Command Reference

| Command            | Purpose                            |
| ------------------ | ---------------------------------- |
| `init`             | Create a new encrypted vault       |
| `add`              | Add a credential                   |
| `list`             | List stored credentials            |
| `search QUERY`     | Search credentials                 |
| `show ID`          | Display credential metadata        |
| `show ID --reveal` | Reveal password after confirmation |
| `delete ID`        | Delete a credential                |
| `change-master`    | Change the master password         |
| `generate`         | Generate a secure password         |
| `check`            | Verify vault authentication        |
| `--help`           | Display help                       |
| `--version`        | Display application version        |

---

# 📍 Custom Vault Location

By default, the vault is stored at:

```text
~/.secure_password_manager/vault.db
```

You can specify another location using:

```bash
python password_manager.py --vault ./my-vault.db init
```

For example:

```bash
python password_manager.py --vault /path/to/vault.db check
```

---

# 🔒 Database Security

The vault database contains encrypted vault information.

Conceptually, the database contains:

```text
SQLite Database
│
├── Version
├── Argon2id Parameters
├── Random Salt
├── AES-GCM Nonce
├── Encrypted Vault
├── Creation Timestamp
└── Update Timestamp
```

Individual passwords are not stored as plaintext SQLite columns.

---

# 🛡️ File Permissions

On POSIX systems such as Linux and macOS, the application attempts to set the vault file permissions to:

```text
0600
```

This means:

```text
Owner: read + write
Group: no access
Others: no access
```

This provides an additional local protection layer.

Windows uses its operating-system permission model instead of this POSIX permission setting.

---

# 🚫 What This Project Does NOT Do

The application intentionally does not:

* Execute arbitrary shell commands
* Modify firewall configuration
* Modify system security settings
* Send credentials to a server
* Upload vault contents
* Store the master password
* Store credentials in plaintext
* Require an online account
* Require administrator/root privileges
* Automatically expose passwords
* Include password recovery that bypasses the master password

---

# 🧠 Threat Model

The design primarily considers the following threats.

## Stolen Vault Database

If an attacker obtains:

```text
vault.db
```

the credential data remains encrypted.

The attacker would still need to recover the master password.

Argon2id makes offline password guessing more expensive than using a fast password hash.

---

## Modified Vault

If an attacker modifies encrypted vault data, AES-GCM authentication should detect the modification.

The application should refuse to accept unauthenticated ciphertext.

---

## Weak Master Password

Encryption cannot compensate for a weak master password.

A short or predictable password can make offline guessing substantially easier.

Use a strong, unique passphrase.

---

## Local Malware

This project does not claim protection against malware that already controls the user's machine.

Malware with sufficient privileges may be able to:

* Read process memory
* Capture keyboard input
* Capture screen contents
* Inspect files
* Modify the operating system

A local password manager cannot completely defend against a compromised host.

---

# ⚠️ Important Security Limitations

This project is intentionally transparent about its limitations.

## No Independent Security Audit

The code has not undergone:

* Professional penetration testing
* Independent cryptographic review
* Formal security audit
* Formal verification

Therefore it should not be marketed as a production-grade password manager.

---

## Memory Protection

Python does not provide guaranteed secure memory erasure.

Sensitive strings may exist temporarily in memory due to:

* Python string immutability
* Garbage collection
* Interpreter implementation
* Memory allocation behavior

Therefore the application cannot guarantee cryptographic memory wiping.

---

## Clipboard Security

The application does not automatically copy passwords to the clipboard.

This is intentional.

Clipboard contents can potentially be accessed by other applications.

---

## Offline Attack Resistance

Argon2id helps make password guessing more expensive, but it does not make a weak master password secure.

A strong master password remains essential.

---

## Backups

The application does not implement encrypted cloud backups.

If you manually back up the vault, protect the backup as carefully as the original.

A copied vault is still sensitive encrypted data.

---

# 🔐 GitHub Security

## NEVER upload your vault

Do not commit:

```text
vault.db
*.db
*.sqlite
*.sqlite3
```

The project includes a `.gitignore` to help prevent accidental uploads.

Before pushing the repository, verify that your vault is not inside the project directory.

---

# 🚨 If You Accidentally Upload a Vault

If you accidentally commit a vault containing real credentials:

1. Remove it from the repository.
2. Treat the exposed vault as compromised.
3. Change important account passwords.
4. Rotate affected API keys/tokens.
5. Review Git history because deleting a file from the latest commit does not necessarily remove it from previous commits.
6. Consider the repository compromised if it was public.

Never assume deleting the visible file completely removes sensitive information from Git history.

---

# 🧪 Security Testing Checklist

Before considering the project complete, test the following:

```text
[ ] Create a new vault
[ ] Reject weak master password
[ ] Reject mismatched master passwords
[ ] Unlock with correct password
[ ] Reject incorrect password
[ ] Add credential
[ ] List credentials
[ ] Search credentials
[ ] Show credential
[ ] Require confirmation before password reveal
[ ] Generate secure password
[ ] Delete credential
[ ] Change master password
[ ] Unlock with new master password
[ ] Ensure old master password no longer works
[ ] Corrupt encrypted vault and verify failure
[ ] Modify authentication metadata and verify failure
[ ] Verify vault file permissions on Linux/macOS
[ ] Confirm vault is ignored by Git
[ ] Verify no passwords are written to application logs
```

---

# 🔍 Example Workflow

A typical workflow looks like:

```bash
# Install dependency
python -m pip install -r requirements.txt

# Create vault
python password_manager.py init

# Add credential
python password_manager.py add

# List credentials
python password_manager.py list

# Search
python password_manager.py search github

# View credential metadata
python password_manager.py show ENTRY_ID

# Generate password
python password_manager.py generate --length 32

# Check vault
python password_manager.py check

# Change master password
python password_manager.py change-master

# Delete credential
python password_manager.py delete ENTRY_ID
```

---

# 🏗️ Technologies

| Technology  | Purpose                             |
| ----------- | ----------------------------------- |
| Python      | Application development             |
| SQLite      | Local encrypted-vault storage       |
| Argon2id    | Password-based key derivation       |
| AES-256-GCM | Authenticated encryption            |
| `secrets`   | Cryptographically secure randomness |
| `getpass`   | Hidden password input               |
| `argparse`  | CLI interface                       |
| `json`      | Vault serialization                 |
| `pathlib`   | Filesystem handling                 |

---

# 📚 Security Standards & Guidance

The project design is informed by established security guidance, including:

* OWASP Password Storage Cheat Sheet
* OWASP Cryptographic Storage Cheat Sheet
* NIST Digital Identity Guidelines
* Python `secrets` documentation
* `cryptography` library AEAD and Argon2id documentation

The project follows the principle of using established cryptographic primitives rather than implementing cryptography manually.

---

# 🎯 Learning Objectives

This project is designed to strengthen practical knowledge of:

### Python

* Classes
* Functions
* Type hints
* Dataclasses
* Exception handling
* CLI development
* SQLite
* File handling

### Cybersecurity

* Password security
* Key derivation
* Authenticated encryption
* Threat modeling
* Secret management
* Data integrity
* Secure file permissions
* Local attack surfaces

### Secure Software Development

* Input validation
* Error handling
* Secure defaults
* Least privilege
* Dependency management
* Sensitive-data handling
* Defensive programming

---

# 🚀 Future Improvements

Potential future versions could add:

* [ ] Automated unit tests
* [ ] Integration tests
* [ ] Security regression tests
* [ ] Password strength estimation
* [ ] Have I Been Pwned-style breach checking without sending plaintext passwords
* [ ] Secure clipboard integration
* [ ] OS keychain integration
* [ ] Encrypted backup system
* [ ] Import/export with carefully designed secure formats
* [ ] TOTP/2FA secret support
* [ ] Password history
* [ ] Entry editing
* [ ] Audit logging without sensitive information
* [ ] Better cross-platform permission handling
* [ ] Hardware-backed key storage where supported
* [ ] Formal threat model documentation
* [ ] Fuzz testing
* [ ] Independent security review

---

# ⚖️ Ethical & Legal Disclaimer

This project is created for **educational, defensive, and authorized security purposes**.

Only use it with credentials and systems that you own or have explicit permission to manage.

Do not use the project to store credentials that you are not authorized to possess or access.

The author makes no guarantee that the software is suitable for production use or that it provides protection against every possible attack.

---

# 📌 Project Status

**Phase:** 2

**Project:** 01

**Name:** Secure Password Manager

**Status:** 🚧 Development / Educational

**Category:** Cybersecurity / Cryptography / Secure Software Development

**Difficulty:** Advanced

---

# 👨‍💻 Author

**Avinash Das Manikpuri**

GitHub:

```text
https://github.com/Avinash-05-web
```

---

# ⭐ Project Goal

This project is part of a broader journey from basic Python programming toward **cybersecurity, software development, cryptography, networking, and secure application engineering**.

The objective is not simply to write code that works, but to understand:

```text
How it works
     ↓
Why it works
     ↓
How it can fail
     ↓
How it can be attacked
     ↓
How it can be made safer
```
