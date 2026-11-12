
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str):
    query = text("""
        SELECT *
        FROM users
        WHERE email = :email
        LIMIT 1
    """)
    return db.execute(query, {"email": email}).mappings().first()


def get_user_by_phone(db: Session, phone: str):
    query = text("""
        SELECT *
        FROM users
        WHERE phone = :phone
        LIMIT 1
    """)
    return db.execute(query, {"phone": phone}).mappings().first()


def create_user(
    db: Session,
    email: str,
    phone: str,
    password_hash: str,
    full_name: str
):
    query = text("""
        INSERT INTO users (
            email,
            phone,
            password_hash,
            full_name,
            role
        )
        VALUES (
            :email,
            :phone,
            :password_hash,
            :full_name,
            'user'
        )
        RETURNING user_id, email, phone, full_name, role, created_at
    """)

    result = db.execute(query, {
        "email": email,
        "phone": phone,
        "password_hash": password_hash,
        "full_name": full_name
    })

    db.commit()
    return result.mappings().first()
