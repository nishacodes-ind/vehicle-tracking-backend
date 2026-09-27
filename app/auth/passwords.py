from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain password into a password hash for database storage."""
    return password_hash.hash(password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Check a login password against the hash saved for the user."""
    return password_hash.verify(plain_password, stored_hash)
