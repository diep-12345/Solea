
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

def get_user_by_id(db: Session, user_id: int):
    query = text("""
        SELECT
            user_id,
            email,
            phone,
            full_name,
            avatar_url,
            role,
            token_version,
            created_at
        FROM users
        WHERE user_id = :user_id
        LIMIT 1
    """)

    return db.execute(
        query,
        {"user_id": user_id}
    ).mappings().first()

def update_user_profile(db: Session, user_id: int, data: dict):
    query = text("""
        UPDATE users
        SET
            full_name = :full_name,
            phone = :phone,
            avatar_url = :avatar_url
        WHERE user_id = :user_id
        RETURNING
            user_id, email, phone, full_name,
            avatar_url, role, created_at
    """)

    result = db.execute(
        query,
        {**data, "user_id": user_id}
    ).mappings().first()

    db.commit()
    return result


def update_user_password(
    db: Session,
    user_id: int,
    new_password_hash: str
):
    query = text("""
        UPDATE users
        SET
            password_hash = :password_hash,
            token_version = token_version + 1
        WHERE user_id = :user_id
    """)

    db.execute(query, {
        "password_hash": new_password_hash,
        "user_id": user_id
    })

    db.commit()
def get_password_hash_by_user_id(db: Session, user_id: int):
    query = text("""
        SELECT password_hash
        FROM users
        WHERE user_id = :user_id
        LIMIT 1
    """)

    result = db.execute(
        query, {"user_id": user_id}
    ).mappings().first()

    return result["password_hash"] if result else None
