import random
import json
from db_connect import get_connection
from utils import batch_insert, random_datetime

TOTAL_LOGS = 100000
BATCH_SIZE = 5000

ACTIONS = [
    ('UPDATE_PRICE', 'products'),
    ('APPROVE_ORDER', 'orders'),
    ('REJECT_ORDER', 'orders'),
    ('APPROVE_RETURN', 'return_requests'),
    ('HIDE_REVIEW', 'reviews'),
    ('HIDE_BLOG', 'blogs'),
    ('ADD_PRODUCT', 'products'),
    ('DELETE_PRODUCT', 'products'),
]

def seed():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE role = 'admin'")
    admin_ids = [r[0] for r in cur.fetchall()]
    if not admin_ids:
        print("Chưa có admin.")
        return

    
    inserted = 0
    while inserted < TOTAL_LOGS:
        chunk = min(BATCH_SIZE, TOTAL_LOGS - inserted)
        batch = []
        for _ in range(chunk):
            action, table = random.choice(ACTIONS)
            batch.append((
                random.choice(admin_ids),
                action,
                table,
                random.randint(1, 500),
                json.dumps({"old_price": random.randint(100000, 500000)}),
                json.dumps({"new_price": random.randint(100000, 500000)}),
                random_datetime(365)
            ))
        batch_insert(cur, """
            INSERT INTO admin_logs (admin_id, action, target_table, target_id, old_data, new_data, created_at)
            VALUES %s
        """, batch, batch_size=chunk)
        conn.commit()
        inserted += chunk
        print(f"{inserted:,}/{TOTAL_LOGS:,}")

    print(f"Hoàn tất {TOTAL_LOGS:,} admin_logs!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()