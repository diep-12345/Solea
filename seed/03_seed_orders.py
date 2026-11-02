import random
from db_connect import get_connection
from utils import fake, batch_insert, random_datetime

NUM_ORDERS = 2000
STATUS_DIST = [
    ('pending', 0.10), ('confirmed', 0.15), ('shipping', 0.20),
    ('delivered', 0.45), ('cancelled', 0.05), ('returned', 0.05)
]

def weighted_choice(dist):
    r = random.random()
    cum = 0
    for val, weight in dist:
        cum += weight
        if r < cum:
            return val
    return dist[-1][0]

def seed():
    conn = get_connection()
    cur = conn.cursor()

    # Lấy danh sách user_id và address
    cur.execute("SELECT user_id FROM users WHERE role = 'user'")
    user_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT address_id, user_id FROM user_addresses")
    addresses_by_user = {}
    for aid, uid in cur.fetchall():
        addresses_by_user.setdefault(uid, []).append(aid)

    cur.execute("SELECT variant_id, product_id FROM product_variants WHERE stock_quantity > 0")
    variants = cur.fetchall()

    # Giỏ hàng: mỗi user có 1 giỏ
    cart_data = [(uid,) for uid in user_ids]
    batch_insert(cur, "INSERT INTO carts (user_id) VALUES %s", cart_data)
    conn.commit()

    cur.execute("SELECT cart_id, user_id FROM carts")
    cart_map = {uid: cid for cid, uid in cur.fetchall()}

    # Thêm 0-5 item mỗi giỏ
    cart_item_data = []
    for uid, cid in cart_map.items():
        for _ in range(random.randint(0, 5)):
            vid, _ = random.choice(variants)
            cart_item_data.append((cid, vid, random.randint(1, 3)))
    
    if cart_item_data:
        try:
            batch_insert(cur, "INSERT INTO cart_items (cart_id, variant_id, quantity) VALUES %s", cart_item_data)
            conn.commit()
        except Exception:
            conn.rollback()  # Bỏ qua nếu vi phạm UNIQUE
    print(f"Đã tạo {len(cart_item_data)} cart_items")

    # Tạo orders
    orders_data = []
    order_items_temp = []  # order_index, variant_id, quantity, unit_price

    for i in range(NUM_ORDERS):
        uid = random.choice(user_ids)
        addr = random.choice(addresses_by_user[uid])
        status = weighted_choice(STATUS_DIST)

        # Chọn 1-4 sản phẩm
        n_items = random.randint(1, 4)
        chosen = random.sample(variants, min(n_items, len(variants)))

        total = 0
        items_for_this_order = []
        for vid, pid in chosen:
            cur.execute("SELECT base_price, sale_price FROM products WHERE product_id = %s", (pid,))
            base, sale = cur.fetchone()
            unit_price = sale if sale else base
            qty = random.randint(1, 3)
            total += unit_price * qty
            items_for_this_order.append((vid, qty, unit_price))
        
        shipping = random.choice([0, 20000, 30000, 50000])
        total += shipping

        orders_data.append((uid, addr, total, shipping, 'COD', status, random_datetime()))
        order_items_temp.append(items_for_this_order)

    # Insert orders trước để lấy order_id
    from psycopg2.extras import execute_values
    sql_orders = """
        INSERT INTO orders (user_id, address_id, total_amount, shipping_fee, payment_method, status, created_at)
        VALUES %s RETURNING order_id
    """
    order_ids = []
    for i in range(0, len(orders_data), 500):
        batch = orders_data[i:i+500]
        ids = execute_values(cur, sql_orders, batch, fetch=True)
        order_ids.extend([r[0] for r in ids])
    conn.commit()

    # Insert order_items
    oi_data = []
    for order_id, items in zip(order_ids, order_items_temp):
        for vid, qty, price in items:
            oi_data.append((order_id, vid, qty, price))
    
    batch_insert(cur, """
        INSERT INTO order_items (order_id, variant_id, quantity, unit_price)
        VALUES %s
    """, oi_data)
    conn.commit()
    print(f"Đã tạo {len(oi_data)} order_items")

    # Yêu cầu hoàn hàng (chỉ với đơn delivered/returned)
    cur.execute("SELECT order_id FROM orders WHERE status IN ('delivered', 'returned')")
    eligible = [r[0] for r in cur.fetchall()]
    
    reasons = ['Sản phẩm bị lỗi', 'Giao sai size', 'Không đúng mô tả', 'Đổi ý không muốn mua']
    banks = ['Vietcombank', 'Techcombank', 'MB Bank', 'ACB', 'BIDV']
    
    returns_data = []
    for oid in random.sample(eligible, min(200, len(eligible))):
        returns_data.append((
            oid,
            random.choice(reasons),
            fake.paragraph()[:200],
            f"https://picsum.photos/seed/ret{oid}/300/300",
            random.choice(banks),
            f"{random.randint(10**9, 10**12)}",
            fake.name(),
            weighted_choice([('pending', 0.3), ('approved', 0.5), ('rejected', 0.2)]),
            weighted_choice([('not_refunded', 0.4), ('refunded', 0.6)])
        ))
    
    batch_insert(cur, """
        INSERT INTO return_requests (order_id, reason, description, evidence_image_url, 
                                     bank_name, bank_account_number, bank_account_name, status, refund_status)
        VALUES %s
    """, returns_data)
    conn.commit()
    print(f"Đã tạo {len(returns_data)} return requests")

    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()