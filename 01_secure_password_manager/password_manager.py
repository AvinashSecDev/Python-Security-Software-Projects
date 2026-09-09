#!/usr/bin/env python3
"""
Secure Password Manager
-----------------------

A local, encrypted password manager designed for educational and
defensive security purposes.

Security design:
- Argon2id derives a 256-bit vault encryption key from the master password.
- AES-256-GCM provides authenticated encryption.
- Fresh random salt for every vault.
- Fresh random nonce for every vault save.
- All credential metadata and values are encrypted together.
- Master password is never stored.
- SQLite stores only encrypted vault data and cryptographic metadata.
- Password input uses getpass instead of normal input().
- Passwords are never intentionally printed to logs.
- Atomic database updates reduce the chance of corrupting the vault.
- Basic failed-attempt delay helps against repeated interactive guesses.
- Strong generated passwords use Python's cryptographically secure secrets module.

This application is NOT a replacement for an independently audited
production password manager.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import secrets
import sqlite3
import string
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


# ============================================================
# Configuration
# ============================================================

APP_NAME = "Secure Password Manager"
APP_VERSION = "1.0.0"
SCHEMA_VERSION = 1

DEFAULT_VAULT = Path.home() / ".secure_password_manager" / "vault.db"

# OWASP-recommended Argon2id baseline.
# 19 MiB memory, 2 iterations, 1 lane.
ARGON2_MEMORY_COST = 19 * 1024
ARGON2_ITERATIONS = 2
ARGON2_LANES = 1

SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12

MIN_MASTER_PASSWORD_LENGTH = 15
MAX_MASTER_PASSWORD_LENGTH = 1024

MAX_ENTRY_NAME_LENGTH = 200
MAX_USERNAME_LENGTH = 320
MAX_URL_LENGTH = 2048
MAX_NOTES_LENGTH = 10000
MAX_PASSWORD_LENGTH = 2048

MAX_VAULT_SIZE = 10 * 1024 * 1024  # 10 MiB

FAILED_ATTEMPT_DELAY_BASE = 1.0
FAILED_ATTEMPT_DELAY_MAX = 8.0

# A small local blocklist.
# This is intentionally not presented as a complete compromised-password
# database. Length remains the primary requirement.
COMMON_PASSWORDS = {
    "password",
    "password123",
    "password1234",
    "123456",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "welcome123",
    "iloveyou",
    "abc123",
    "changeme",
    "monkey",
    "dragon",
}


# ============================================================
# Exceptions
# ============================================================

class VaultError(Exception):
    """Base exception for expected vault errors."""


class VaultNotInitializedError(VaultError):
    """Raised when the vault has not been initialized."""


class VaultAuthenticationError(VaultError):
    """Raised when authentication/decryption fails."""


class VaultIntegrityError(VaultError):
    """Raised when encrypted vault data is corrupted or modified."""


class ValidationError(VaultError):
    """Raised for invalid user input."""


# ============================================================
# Data structures
# ============================================================

@dataclass
class VaultMetadata:
    version: int
    salt: bytes
    memory_cost: int
    iterations: int
    lanes: int


# ============================================================
# Secure password helpers
# ============================================================

def secure_random_password(
    length: int = 24,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """
    Generate a cryptographically secure random password.

    Uses secrets.choice rather than random.choice.
    """

    if length < 12:
        raise ValidationError("Generated password length must be at least 12.")

    pools = []

    if use_upper:
        pools.append(string.ascii_uppercase)

    if use_lower:
        pools.append(string.ascii_lowercase)

    if use_digits:
        pools.append(string.digits)

    if use_symbols:
        pools.append("!@#$%^&*()-_=+[]{}:,.?")

    if not pools:
        raise ValidationError("At least one character set must be enabled.")

    if length < len(pools):
        raise ValidationError(
            "Password length is too short for the selected character sets."
        )

    # Guarantee at least one character from every selected set.
    password_chars = [
        secrets.choice(pool)
        for pool in pools
    ]

    all_characters = "".join(pools)

    password_chars.extend(
        secrets.choice(all_characters)
        for _ in range(length - len(password_chars))
    )

    # Fisher-Yates shuffle using cryptographically secure randomness.
    for index in range(len(password_chars) - 1, 0, -1):
        swap_index = secrets.randbelow(index + 1)
        password_chars[index], password_chars[swap_index] = (
            password_chars[swap_index],
            password_chars[index],
        )

    return "".join(password_chars)


def validate_master_password(password: str) -> None:
    """
    Validate the master password.

    We prioritize length and reject a small list of extremely common
    passwords. We intentionally do not enforce arbitrary composition rules.
    """

    if not isinstance(password, str):
        raise ValidationError("Master password must be text.")

    length = len(password)

    if length < MIN_MASTER_PASSWORD_LENGTH:
        raise ValidationError(
            f"Master password must be at least "
            f"{MIN_MASTER_PASSWORD_LENGTH} characters long."
        )

    if length > MAX_MASTER_PASSWORD_LENGTH:
        raise ValidationError(
            f"Master password must not exceed "
            f"{MAX_MASTER_PASSWORD_LENGTH} characters."
        )

    if password.casefold() in COMMON_PASSWORDS:
        raise ValidationError(
            "That master password is too common. Choose a stronger passphrase."
        )


def validate_text(
    value: str,
    field_name: str,
    maximum: int,
    allow_empty: bool = False,
) -> str:
    """Validate general text fields."""

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be text.")

    if not allow_empty and not value.strip():
        raise ValidationError(f"{field_name} cannot be empty.")

    if len(value) > maximum:
        raise ValidationError(
            f"{field_name} is too long. Maximum: {maximum} characters."
        )

    return value


# ============================================================
# Key derivation
# ============================================================

def derive_key(
    master_password: str,
    metadata: VaultMetadata,
) -> bytes:
    """
    Derive a 256-bit encryption key from the master password.

    Argon2id is memory-hard and designed for password-based key derivation.
    """

    kdf = Argon2id(
        salt=metadata.salt,
        length=KEY_SIZE,
        iterations=metadata.iterations,
        lanes=metadata.lanes,
        memory_cost=metadata.memory_cost,
    )

    return kdf.derive(master_password.encode("utf-8"))


# ============================================================
# Vault encryption
# ============================================================

def build_aad(metadata: VaultMetadata) -> bytes:
    """
    Build authenticated-but-not-encrypted metadata.

    If the version or KDF parameters are altered, AES-GCM authentication
    will fail instead of silently accepting modified metadata.
    """

    return (
        f"SPM-v{metadata.version}|"
        f"argon2id:{metadata.memory_cost}:"
        f"{metadata.iterations}:"
        f"{metadata.lanes}"
    ).encode("ascii")


def encrypt_vault(
    vault_data: dict[str, Any],
    master_password: str,
) -> tuple[VaultMetadata, bytes, bytes]:
    """Encrypt complete vault contents."""

    serialized = json.dumps(
        vault_data,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    if len(serialized) > MAX_VAULT_SIZE:
        raise VaultError("Vault is too large.")

    metadata = VaultMetadata(
        version=SCHEMA_VERSION,
        salt=secrets.token_bytes(SALT_SIZE),
        memory_cost=ARGON2_MEMORY_COST,
        iterations=ARGON2_ITERATIONS,
        lanes=ARGON2_LANES,
    )

    key = derive_key(master_password, metadata)

    nonce = secrets.token_bytes(NONCE_SIZE)

    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(
        nonce,
        serialized,
        build_aad(metadata),
    )

    return metadata, nonce, ciphertext


def decrypt_vault(
    metadata: VaultMetadata,
    nonce: bytes,
    ciphertext: bytes,
    master_password: str,
) -> dict[str, Any]:
    """Decrypt and authenticate the complete vault."""

    if len(nonce) != NONCE_SIZE:
        raise VaultIntegrityError("Invalid vault nonce.")

    if len(ciphertext) < 16:
        raise VaultIntegrityError("Vault ciphertext is invalid.")

    if len(ciphertext) > MAX_VAULT_SIZE + 16:
        raise VaultIntegrityError("Vault ciphertext is too large.")

    key = derive_key(master_password, metadata)

    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(
            nonce,
            ciphertext,
            build_aad(metadata),
        )
    except InvalidTag as exc:
        raise VaultAuthenticationError(
            "Invalid master password or corrupted vault."
        ) from exc

    try:
        decoded = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VaultIntegrityError(
            "Vault decrypted but contained invalid data."
        ) from exc

    if not isinstance(decoded, dict):
        raise VaultIntegrityError("Vault root must be an object.")

    return decoded


# ============================================================
# SQLite storage
# ============================================================

class VaultDatabase:
    """Small SQLite wrapper that stores encrypted vault data."""

    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()

    def exists(self) -> bool:
        return self.path.exists()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=5,
        )

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA secure_delete = ON")

        return connection

    def initialize(self) -> None:
        """Create the database schema."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = self._connect()

        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vault (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    version INTEGER NOT NULL,
                    salt BLOB NOT NULL,
                    memory_cost INTEGER NOT NULL,
                    iterations INTEGER NOT NULL,
                    lanes INTEGER NOT NULL,
                    nonce BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

        finally:
            connection.close()

        set_private_file_permissions(self.path)

    def read(self) -> tuple[VaultMetadata, bytes, bytes] | None:
        """Read encrypted vault metadata and ciphertext."""

        if not self.exists():
            return None

        connection = self._connect()

        try:
            row = connection.execute(
                """
                SELECT
                    version,
                    salt,
                    memory_cost,
                    iterations,
                    lanes,
                    nonce,
                    ciphertext
                FROM vault
                WHERE id = 1
                """
            ).fetchone()

        finally:
            connection.close()

        if row is None:
            return None

        (
            version,
            salt,
            memory_cost,
            iterations,
            lanes,
            nonce,
            ciphertext,
        ) = row

        try:
            metadata = VaultMetadata(
                version=int(version),
                salt=bytes(salt),
                memory_cost=int(memory_cost),
                iterations=int(iterations),
                lanes=int(lanes),
            )

            nonce = bytes(nonce)
            ciphertext = bytes(ciphertext)

        except (TypeError, ValueError) as exc:
            raise VaultIntegrityError(
                "Vault metadata is invalid."
            ) from exc

        validate_metadata(metadata)

        return metadata, nonce, ciphertext

    def write(
        self,
        metadata: VaultMetadata,
        nonce: bytes,
        ciphertext: bytes,
    ) -> None:
        """Atomically replace the encrypted vault record."""

        if len(nonce) != NONCE_SIZE:
            raise VaultError("Invalid nonce length.")

        if len(ciphertext) > MAX_VAULT_SIZE + 16:
            raise VaultError("Encrypted vault is too large.")

        self.initialize()

        now = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        )

        connection = self._connect()

        try:
            connection.execute("BEGIN IMMEDIATE")

            connection.execute(
                """
                INSERT INTO vault (
                    id,
                    version,
                    salt,
                    memory_cost,
                    iterations,
                    lanes,
                    nonce,
                    ciphertext,
                    created_at,
                    updated_at
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    version = excluded.version,
                    salt = excluded.salt,
                    memory_cost = excluded.memory_cost,
                    iterations = excluded.iterations,
                    lanes = excluded.lanes,
                    nonce = excluded.nonce,
                    ciphertext = excluded.ciphertext,
                    updated_at = excluded.updated_at
                """,
                (
                    metadata.version,
                    metadata.salt,
                    metadata.memory_cost,
                    metadata.iterations,
                    metadata.lanes,
                    nonce,
                    ciphertext,
                    now,
                    now,
                ),
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        set_private_file_permissions(self.path)


# ============================================================
# Filesystem security
# ============================================================

def set_private_file_permissions(path: Path) -> None:
    """
    On POSIX systems, restrict the vault file to owner read/write.

    Windows ACLs are handled by the operating system and are not modified
    here because portable ACL manipulation is platform-specific.
    """

    if os.name == "posix":
        try:
            os.chmod(path, 0o600)
        except OSError:
            # Failure to tighten permissions should not destroy the vault.
            pass


# ============================================================
# Metadata validation
# ============================================================

def validate_metadata(metadata: VaultMetadata) -> None:
    """Reject unsupported or obviously unsafe cryptographic parameters."""

    if metadata.version != SCHEMA_VERSION:
        raise VaultIntegrityError(
            f"Unsupported vault version: {metadata.version}"
        )

    if len(metadata.salt) != SALT_SIZE:
        raise VaultIntegrityError("Invalid salt length.")

    if metadata.memory_cost < 8 * 1024:
        raise VaultIntegrityError("Unsafe Argon2id memory cost.")

    if metadata.memory_cost > 1024 * 1024:
        raise VaultIntegrityError("Unreasonable Argon2id memory cost.")

    if metadata.iterations < 1 or metadata.iterations > 10:
        raise VaultIntegrityError("Invalid Argon2id iteration count.")

    if metadata.lanes < 1 or metadata.lanes > 16:
        raise VaultIntegrityError("Invalid Argon2id parallelism.")


# ============================================================
# Vault manager
# ============================================================

class SecureVault:
    """High-level password vault."""

    def __init__(self, database: VaultDatabase):
        self.database = database

    def create(
        self,
        master_password: str,
        confirm_password: str,
    ) -> None:
        """Create a new empty encrypted vault."""

        if self.database.exists():
            existing = self.database.read()

            if existing is not None:
                raise VaultError(
                    "A vault already exists at this location."
                )

        validate_master_password(master_password)

        if master_password != confirm_password:
            raise ValidationError("Master passwords do not match.")

        vault_data = {
            "format": "secure-password-manager",
            "version": SCHEMA_VERSION,
            "entries": [],
        }

        metadata, nonce, ciphertext = encrypt_vault(
            vault_data,
            master_password,
        )

        self.database.write(
            metadata,
            nonce,
            ciphertext,
        )

    def unlock(self, master_password: str) -> dict[str, Any]:
        """Unlock and return decrypted vault contents."""

        stored = self.database.read()

        if stored is None:
            raise VaultNotInitializedError(
                "No initialized vault was found."
            )

        metadata, nonce, ciphertext = stored

        return decrypt_vault(
            metadata,
            nonce,
            ciphertext,
            master_password,
        )

    def save(
        self,
        vault_data: dict[str, Any],
        master_password: str,
    ) -> None:
        """Encrypt and save the complete vault."""

        metadata, nonce, ciphertext = encrypt_vault(
            vault_data,
            master_password,
        )

        self.database.write(
            metadata,
            nonce,
            ciphertext,
        )

    def change_master_password(
        self,
        old_password: str,
        new_password: str,
        confirm_password: str,
    ) -> None:
        """Re-encrypt the vault under a new master password."""

        vault_data = self.unlock(old_password)

        validate_master_password(new_password)

        if new_password != confirm_password:
            raise ValidationError("New master passwords do not match.")

        self.save(
            vault_data,
            new_password,
        )


# ============================================================
# Entry operations
# ============================================================

def find_entry(
    vault_data: dict[str, Any],
    entry_id: str,
) -> dict[str, Any] | None:

    for entry in vault_data.get("entries", []):
        if entry.get("id") == entry_id:
            return entry

    return None


def create_entry(
    name: str,
    username: str,
    password: str,
    url: str,
    notes: str,
) -> dict[str, Any]:

    name = validate_text(
        name,
        "Name",
        MAX_ENTRY_NAME_LENGTH,
    )

    username = validate_text(
        username,
        "Username",
        MAX_USERNAME_LENGTH,
        allow_empty=True,
    )

    password = validate_text(
        password,
        "Password",
        MAX_PASSWORD_LENGTH,
    )

    url = validate_text(
        url,
        "URL",
        MAX_URL_LENGTH,
        allow_empty=True,
    )

    notes = validate_text(
        notes,
        "Notes",
        MAX_NOTES_LENGTH,
        allow_empty=True,
    )

    return {
        "id": secrets.token_hex(16),
        "name": name.strip(),
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "created_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
    }


# ============================================================
# CLI helpers
# ============================================================

def get_master_password(
    prompt: str = "Master password: ",
) -> str:
    """Read a master password without echoing it."""

    password = getpass.getpass(prompt)

    if not password:
        raise ValidationError("Master password cannot be empty.")

    return password


def confirm_action(message: str) -> bool:
    """Ask for explicit confirmation."""

    response = input(f"{message} [y/N]: ").strip().casefold()

    return response in {"y", "yes"}


def print_entry(entry: dict[str, Any]) -> None:
    """Display a credential entry without revealing its password."""

    print()
    print(f"ID:       {entry['id']}")
    print(f"Name:     {entry['name']}")
    print(f"Username: {entry['username']}")
    print(f"URL:      {entry['url'] or '-'}")
    print(f"Created:  {entry.get('created_at', '-')}")
    print()


def load_unlocked_vault(
    vault: SecureVault,
) -> tuple[dict[str, Any], str]:
    """
    Authenticate the user with limited interactive retry delays.

    Note:
    This only slows guesses through this application.
    It cannot prevent offline attacks against a stolen vault file.
    """

    failed_attempts = 0

    while True:
        password = get_master_password()

        try:
            vault_data = vault.unlock(password)

            return vault_data, password

        except VaultAuthenticationError:
            failed_attempts += 1

            delay = min(
                FAILED_ATTEMPT_DELAY_BASE * (2 ** (failed_attempts - 1)),
                FAILED_ATTEMPT_DELAY_MAX,
            )

            print("Authentication failed.", file=sys.stderr)

            if failed_attempts >= 5:
                print(
                    f"Too many failed attempts. Waiting {delay:.1f} seconds.",
                    file=sys.stderr,
                )

            time.sleep(delay)

        except VaultError:
            raise


# ============================================================
# Command handlers
# ============================================================

def command_init(args: argparse.Namespace) -> int:
    """Initialize a new vault."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    if database.exists() and database.read() is not None:
        print("A vault already exists.")
        return 1

    print("Creating a new secure vault.")
    print(
        f"Master password must be at least "
        f"{MIN_MASTER_PASSWORD_LENGTH} characters."
    )
    print()

    master_password = get_master_password(
        "Create master password: "
    )

    confirm_password = get_master_password(
        "Confirm master password: "
    )

    try:
        vault.create(
            master_password,
            confirm_password,
        )
    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print()
    print("Vault created successfully.")
    print(f"Vault: {database.path}")
    print()
    print(
        "IMPORTANT: The master password is not stored."
    )
    print(
        "If you lose it, the encrypted vault cannot be recovered."
    )

    return 0


def command_list(args: argparse.Namespace) -> int:
    """List vault entries."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, _ = load_unlocked_vault(vault)

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    entries = vault_data.get("entries", [])

    if not entries:
        print("Vault is empty.")
        return 0

    print()
    print(f"{'ID':<34} {'NAME'}")
    print("-" * 80)

    for entry in entries:
        print(
            f"{entry.get('id', ''):<34} "
            f"{entry.get('name', '')}"
        )

    print()
    print(f"Total entries: {len(entries)}")

    return 0


def command_add(args: argparse.Namespace) -> int:
    """Add a new credential."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, master_password = load_unlocked_vault(vault)

        name = input("Service / website name: ").strip()
        username = input("Username/email: ").strip()
        url = input("URL (optional): ").strip()
        notes = input("Notes (optional): ").strip()

        password_choice = input(
            "Generate a secure password? [Y/n]: "
        ).strip().casefold()

        if password_choice in {"", "y", "yes"}:
            length_text = input(
                "Password length [24]: "
            ).strip()

            length = int(length_text) if length_text else 24

            password = secure_random_password(
                length=length,
            )

            print()
            print("Generated password:")
            print(password)
            print()
            print(
                "Store it in the vault only after confirming "
                "you have copied it safely."
            )

        else:
            password = getpass.getpass(
                "Password: "
            )

        entry = create_entry(
            name=name,
            username=username,
            password=password,
            url=url,
            notes=notes,
        )

        vault_data.setdefault("entries", []).append(entry)

        vault.save(
            vault_data,
            master_password,
        )

    except (VaultError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Credential added successfully.")

    return 0


def command_show(args: argparse.Namespace) -> int:
    """Show a credential, including password only after explicit confirmation."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, _ = load_unlocked_vault(vault)

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    entry = find_entry(
        vault_data,
        args.id,
    )

    if entry is None:
        print("Entry not found.", file=sys.stderr)
        return 1

    print_entry(entry)

    if args.reveal:
        if not confirm_action(
            "Reveal the stored password on screen?"
        ):
            print("Password was not revealed.")
            return 0

        print("Password:")
        print(entry["password"])

    return 0


def command_search(args: argparse.Namespace) -> int:
    """Search entries by service name, username, or URL."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, _ = load_unlocked_vault(vault)

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    query = args.query.casefold()

    matches = []

    for entry in vault_data.get("entries", []):
        searchable = " ".join(
            [
                entry.get("name", ""),
                entry.get("username", ""),
                entry.get("url", ""),
            ]
        ).casefold()

        if query in searchable:
            matches.append(entry)

    if not matches:
        print("No matching entries.")
        return 0

    print()
    print(f"{'ID':<34} {'NAME':<30} {'USERNAME'}")
    print("-" * 100)

    for entry in matches:
        print(
            f"{entry.get('id', ''):<34} "
            f"{entry.get('name', '')[:29]:<30} "
            f"{entry.get('username', '')}"
        )

    print()
    print(f"Matches: {len(matches)}")

    return 0


def command_delete(args: argparse.Namespace) -> int:
    """Delete a credential from the encrypted vault."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, master_password = load_unlocked_vault(vault)

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    entry = find_entry(
        vault_data,
        args.id,
    )

    if entry is None:
        print("Entry not found.", file=sys.stderr)
        return 1

    print(f"Entry: {entry['name']}")

    if not confirm_action(
        "Permanently remove this credential from the vault?"
    ):
        print("Deletion cancelled.")
        return 0

    vault_data["entries"] = [
        item
        for item in vault_data.get("entries", [])
        if item.get("id") != args.id
    ]

    try:
        vault.save(
            vault_data,
            master_password,
        )

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Credential deleted.")

    return 0


def command_change_master(args: argparse.Namespace) -> int:
    """Change the vault master password."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        old_password = get_master_password(
            "Current master password: "
        )

        new_password = get_master_password(
            "New master password: "
        )

        confirm_password = get_master_password(
            "Confirm new master password: "
        )

        vault.change_master_password(
            old_password,
            new_password,
            confirm_password,
        )

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Master password changed successfully.")

    return 0


def command_generate(args: argparse.Namespace) -> int:
    """Generate a secure random password."""

    try:
        password = secure_random_password(
            length=args.length,
        )

    except VaultError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(password)

    return 0


def command_check(args: argparse.Namespace) -> int:
    """Verify that a vault can be opened."""

    database = VaultDatabase(args.vault)
    vault = SecureVault(database)

    try:
        vault_data, _ = load_unlocked_vault(vault)

    except VaultError as exc:
        print(f"Vault check failed: {exc}", file=sys.stderr)
        return 1

    entries = vault_data.get("entries", [])

    print("Vault authentication successful.")
    print(f"Entries: {len(entries)}")

    return 0


# ============================================================
# CLI parser
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Local encrypted password manager using "
            "Argon2id and AES-256-GCM."
        )
    )

    parser.add_argument(
        "--vault",
        type=Path,
        default=DEFAULT_VAULT,
        help=(
            "Path to the vault database "
            f"(default: {DEFAULT_VAULT})"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Create a new encrypted vault.",
    )
    init_parser.set_defaults(func=command_init)

    list_parser = subparsers.add_parser(
        "list",
        help="List stored credentials.",
    )
    list_parser.set_defaults(func=command_list)

    add_parser = subparsers.add_parser(
        "add",
        help="Add a credential.",
    )
    add_parser.set_defaults(func=command_add)

    show_parser = subparsers.add_parser(
        "show",
        help="Show a credential.",
    )
    show_parser.add_argument(
        "id",
        help="Credential ID.",
    )
    show_parser.add_argument(
        "--reveal",
        action="store_true",
        help="Reveal the stored password after confirmation.",
    )
    show_parser.set_defaults(func=command_show)

    search_parser = subparsers.add_parser(
        "search",
        help="Search credentials.",
    )
    search_parser.add_argument(
        "query",
        help="Search text.",
    )
    search_parser.set_defaults(func=command_search)

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a credential.",
    )
    delete_parser.add_argument(
        "id",
        help="Credential ID.",
    )
    delete_parser.set_defaults(func=command_delete)

    change_parser = subparsers.add_parser(
        "change-master",
        help="Change the master password.",
    )
    change_parser.set_defaults(func=command_change_master)

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a secure random password.",
    )
    generate_parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=24,
        help="Password length (default: 24).",
    )
    generate_parser.set_defaults(func=command_generate)

    check_parser = subparsers.add_parser(
        "check",
        help="Verify and inspect the vault.",
    )
    check_parser.set_defaults(func=command_check)

    return parser


# ============================================================
# Main
# ============================================================

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)

    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 130

    except EOFError:
        print("\nInput cancelled.", file=sys.stderr)
        return 130

    except sqlite3.Error as exc:
        print(
            f"Database error: {exc}",
            file=sys.stderr,
        )
        return 1

    except OSError as exc:
        print(
            f"File system error: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
