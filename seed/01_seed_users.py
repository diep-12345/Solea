from db_connect import get_connection
from utils import fake, batch_insert, random_datetime
import random

NUM_USERS = 500 # 500 users  
NUM_ADMINS = 5 # 5 admins
ADDRESS_PER_USER = 2 # Mỗi user có 2 địa chỉ

def seed():
    conn = get_connection()
    cur = conn.cursor()

    users_data = []
    
    # Tạo admins (role = 'admin')
    for i in range(NUM_ADMINS):
        users_data.append((
            f"admin{i}@fashion.com",    #email
            f"0901{i:06d}",     #sđt
            "$2b$12$FAKEHASH_admin",    # Hash giả
            f"Admin {i}",      # tên
            None,       # avatar
            "admin",     # role
        ))
            
    #  Tạo users thường
    used_phones = set()
    for i in range(NUM_USERS):
    # Đảm bảo phone unique
        while True:
            phone = fake.phone_number()[:15]
            if phone not in used_phones:
                used_phones.add(phone)
                break
                
        users_data.append((
            fake.unique.email(),    # email
            phone,      # sđt
            "$2b$12$FAKEHASH_user",   # pass giả
            fake.name(),    # tên
            f"https://i.pravatar.cc/150?u={i}",  # Ảnh avatar thật từ pravatar
            "user",      #role
        ))

    batch_insert(cur, """
        INSERT INTO users (email, phone, password_hash, full_name, avatar_url, role)
        VALUES %s
    """, users_data)
    conn.commit()
    print(f"Đã tạo {len(users_data)} users")

    # Tạo địa chỉ cho mỗi user
    cur.execute("SELECT user_id FROM users ORDER BY user_id")
    user_ids = [r[0] for r in cur.fetchall()]

    addr_data = []
    for uid in user_ids:
        for j in range(ADDRESS_PER_USER):
            addr_data.append((
                uid,
                fake.name(),
                fake.phone_number()[:15],
                f"{fake.street_address()}, {fake.city()}",
                j == 0  # Địa chỉ đầu là mặc định
            ))
    
    batch_insert(cur, """
        INSERT INTO user_addresses (user_id, receiver_name, receiver_phone, address_detail, is_default)
        VALUES %s
    """, addr_data)
    conn.commit()
    print(f"Đã tạo {len(addr_data)} addresses")

    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()