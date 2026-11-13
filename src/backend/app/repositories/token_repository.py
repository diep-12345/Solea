from sqlalchemy import text
from sqlalchemy.orm import Session


def revoke_token(db: Session, token: str, expires_at):
    query = text("""
        INSERT INTO revoked_tokens (token, expires_at)
        VALUES (:token, :expires_at)
        ON CONFLICT (token) DO NOTHING
    """)

    db.execute(query, {
        "token": token,
        "expires_at": expires_at
    })

    db.commit()


def is_token_revoked(db: Session, token: str):
    query = text("""
        SELECT id
        FROM revoked_tokens
        WHERE token = :token
        LIMIT 1
    """)

    return db.execute(
        query,
        {"token": token}
    ).first() is not None