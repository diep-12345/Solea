import random
from db_connect import get_connection
from utils import fake, batch_insert, random_datetime

TOTAL_REVIEWS = 100000
BATCH_SIZE = 5000  # Commit từng 5000 dòng để tránh tràn RAM

RATING_DIST = [(5, 0.40), (4, 0.30), (3, 0.15), (2, 0.10), (1, 0.05)]

def weighted_rating():
    r = random.random()
    cum = 0
    for val, w in RATING_DIST:
        cum += w
        if r < cum:
            return val
    return 5

def seed():
    conn = get_connection()
    cur = conn.cursor()

    # Lấy các order_item thuộc đơn đã giao (điều kiện để đánh giá)
    cur.execute("""
        SELECT oi.order_item_id, o.user_id, pv.product_id
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        WHERE o.status = 'delivered'
    """)
    rows = cur.fetchall()
    print(f"Có {len(rows)} order_items có thể đánh giá")

    if not rows:
        print("Không có order_item nào.")
        return

    # Sinh 100.000 reviews
    print(f"Đang sinh {TOTAL_REVIEWS:,} reviews (commit mỗi {BATCH_SIZE:,} dòng)...")
    
    sql = """
        INSERT INTO reviews (user_id, product_id, order_item_id, rating, comment, status, created_at)
        VALUES %s
    """
    
    inserted = 0
    while inserted < TOTAL_REVIEWS:
        chunk_size = min(BATCH_SIZE, TOTAL_REVIEWS - inserted)
        batch = []
        for _ in range(chunk_size):
            oi_id, uid, pid = random.choice(rows)
            rating = weighted_rating()
            # Comment theo số sao
            if rating >= 4:
                comment = fake.sentence() + " Rất hài lòng!"
            elif rating == 3:
                comment = "Tạm ổn, " + fake.sentence().lower()
            else:
                comment = "Không hài lòng. " + fake.sentence()
            
            status = 'hidden' if random.random() < 0.05 else 'visible'  # 5% bị ẩn
            batch.append((uid, pid, oi_id, rating, comment[:500], status, random_datetime(365)))
        
        batch_insert(cur, sql, batch, batch_size=chunk_size)
        conn.commit()
        inserted += chunk_size
        print(f"Đã insert {inserted:,}/{TOTAL_REVIEWS:,}")

    print(f"Hoàn tất {TOTAL_REVIEWS:,} reviews!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()