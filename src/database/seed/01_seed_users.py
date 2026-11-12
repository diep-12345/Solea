from db_connect import get_connection
from fashion_ecommerce.src.database.seed.utils import (
    fake,
    batch_insert,
    random_datetime,
    random_vn_phone,
    random_email,
    random_vn_address,
    fake_bcrypt_hash,
)

NUM_USERS = 500 # 500 users  
NUM_ADMINS = 5 # 5 admins
ADDRESS_PER_USER = 2 # Mỗi user có 2 địa chỉ

def seed():
    conn = get_connection()
    cur = conn.cursor()

    users_data = []
    used_phones = set()
    used_emails = set()
    
    # Tạo admins (role = 'admin')
    admin_hash = fake_bcrypt_hash()     # tất cả admin dùng chung 1 hash
    for i in range(NUM_ADMINS):
        # SĐT admin unique
        while True:
            phone = random_vn_phone()
            if phone not in used_phones:
                used_phones.add(phone)
                break

        email = f"admin{i}@gmail.com"
        used_emails.add(email)

        users_data.append((
            email,
            phone,
            admin_hash,
            fake.name(),
            None,                            
            "admin",
            random_datetime(730),   # tạo trong 2 năm qua
        ))
            
    #  Tạo users thường
    user_hash = fake_bcrypt_hash()      # tất cả user dùng chung 1 hash
    for i in range(NUM_USERS):
        full_name = fake.name()

        # SĐT unique
        while True:
            phone = random_vn_phone()
            if phone not in used_phones:
                used_phones.add(phone)
                break

        # Email unique
        while True:
            email = random_email(full_name)
            if email not in used_emails:
                used_emails.add(email)
                break

        avatar = (
            f"https://i.pravatar.cc/150?u={i}"
            if i % 10 != 0
            else None
        )

        users_data.append((
            email,
            phone,
            user_hash,
            full_name,
            avatar,
            "user",
            random_datetime(730),
        ))

    batch_insert(cur, """
        INSERT INTO users (email, phone, password_hash, full_name, avatar_url, role, created_at)
        VALUES %s
    """, users_data)
    conn.commit()
    print(f"Đã tạo {len(users_data)} users")

    # Tạo địa chỉ cho mỗi user
    cur.execute("SELECT user_id FROM users WHERE role = 'user' ORDER BY user_id")
    user_ids = [r[0] for r in cur.fetchall()]

    addr_data = []
    for uid in user_ids:
        for j in range(ADDRESS_PER_USER):
            province, district, ward, street_address = random_vn_address()
            addr_data.append((
                uid,
                fake.name(),
                random_vn_phone(),
                province,
                district,
                ward,
                street_address,
                j == 0,
            ))

    batch_insert(cur, """
        INSERT INTO user_addresses
            (user_id, receiver_name, receiver_phone, province, district, ward, street_address, is_default)
        VALUES %s
    """, addr_data)
    conn.commit()
    print(f"Đã tạo {len(addr_data)} addresses cho {len(user_ids)} users")

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed()