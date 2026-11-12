import sys, time, threading, logging
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import psycopg2
from db_connect import get_connection

LOG_DIR = Path(__file__).parent / "logs"; LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"concurrency.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-8s] %(levelname)-7s: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

INITIAL_STOCK = 1
QTY = 1

def setup():
    conn = get_connection(); cur = conn.cursor(); ts = int(time.time())
    cur.execute("""INSERT INTO categories(name,slug,is_active) VALUES('Test Cat','test-cat',true)
                   ON CONFLICT(slug) DO UPDATE SET name=EXCLUDED.name RETURNING category_id""")
    cat_id = cur.fetchone()[0]
    cur.execute("""INSERT INTO products(category_id,name,description,base_price,status)
                   VALUES(%s,'Test Product','x',250000,'active') RETURNING product_id""", (cat_id,))
    pid = cur.fetchone()[0]
    cur.execute("""INSERT INTO product_variants(product_id,size,color,sku,stock_quantity)
                   VALUES(%s,'M','Đen',%s,%s) RETURNING variant_id""", (pid, f"TEST-{ts}", INITIAL_STOCK))
    vid = cur.fetchone()[0]
    uids, aids = [], []
    for i in range(2):
        cur.execute("""INSERT INTO users(email,phone,password_hash,full_name,role)
                       VALUES(%s,%s,'$2b$12$FAKEHASH',%s,'user') RETURNING user_id""",
                    (f"c{i}_{ts}@t.com", f"09{ts%10**8:08d}{i}", f"U{i}"))
        uids.append(cur.fetchone()[0])
        cur.execute("""INSERT INTO user_addresses(user_id,receiver_name,receiver_phone,address_detail,is_default)
                       VALUES(%s,'R','0909','Addr',true) RETURNING address_id""", (uids[-1],))
        aids.append(cur.fetchone()[0])
    conn.commit(); cur.close(); conn.close()
    log.info(f"SETUP variant={vid} stock={INITIAL_STOCK} users={uids}")
    return vid, uids, aids

def place_order(uid, aid, vid, qty, barrier):
    conn = get_connection()
    tname = threading.current_thread().name
    try:
        with conn.cursor() as cur:
            barrier.wait()
            cur.execute("""SELECT p.base_price FROM products p
                           JOIN product_variants pv ON p.product_id=pv.product_id
                           WHERE pv.variant_id=%s""", (vid,))
            price = cur.fetchone()[0]
            cur.execute("""INSERT INTO orders(user_id,address_id,total_amount,shipping_fee,status)
                           VALUES(%s,%s,%s,0,'pending') RETURNING order_id""", (uid, aid, price*qty))
            oid = cur.fetchone()[0]
            cur.execute("""INSERT INTO order_items(order_id,variant_id,quantity,unit_price)
                           VALUES(%s,%s,%s,%s)""", (oid, vid, qty, price))
            cur.execute("""UPDATE product_variants SET stock_quantity=stock_quantity-%s
                           WHERE variant_id=%s AND stock_quantity>=%s""", (qty, vid, qty))
            if cur.rowcount == 0:
                conn.rollback()
                log.warning(f"[{tname}] FAILED hết hàng (order {oid})")
                return ("FAILED", oid)
            conn.commit()
            log.info(f"[{tname}] SUCCESS order {oid}")
            return ("SUCCESS", oid)
    except Exception as e:
        conn.rollback()
        log.error(f"[{tname}] ERROR {e}")
        return ("ERROR", None)
    finally:
        conn.close()

def verify(vid):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT stock_quantity FROM product_variants WHERE variant_id=%s", (vid,))
    stock = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM order_items WHERE variant_id=%s", (vid,))
    n_items = cur.fetchone()[0]
    cur.execute("""SELECT COUNT(DISTINCT oi.order_id) FROM order_items oi
                   JOIN orders o ON oi.order_id=o.order_id WHERE oi.variant_id=%s""", (vid,))
    n_orders = cur.fetchone()[0]
    cur.close(); conn.close()
    log.info(f"VERIFY stock={stock} items={n_items} orders={n_orders}")
    return stock == 0 and n_items == 1 and n_orders == 1

def main():
    log.info("=== TEST CONCURRENCY ===")
    vid, uids, aids = setup()
    barrier = threading.Barrier(2)
    results = {}
    def worker(i):
        results[i] = place_order(uids[i], aids[i], vid, QTY, barrier)
    t1 = threading.Thread(target=worker, args=(0,), name="UserA")
    t2 = threading.Thread(target=worker, args=(1,), name="UserB")
    t1.start(); t2.start(); t1.join(); t2.join()
    statuses = [r[0] for r in results.values()]
    log.info(f"Statuses: {statuses}")
    if statuses.count("SUCCESS") != 1 or statuses.count("FAILED") != 1:
        log.error("FAIL: không đúng 1 SUCCESS + 1 FAILED"); return 1
    if not verify(vid):
        log.error("FAIL: verify sai"); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())