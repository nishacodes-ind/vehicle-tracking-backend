import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "local-development-only-change-this-secret"
)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)


def create_access_token(user_id: int) -> str:
    """Create a signed token that identifies one user and expires after a time limit."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token_data = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
