import random
from db_connect import get_connection
from utils import fake, batch_insert, random_datetime

NUM_BLOGS = 50
COMMENTS_PER_BLOG = 10
LIKES_PER_BLOG = 100

def seed():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE role = 'user'")
    user_ids = [r[0] for r in cur.fetchall()]

    # Blogs
    blog_titles = [
        "Cách mix áo cardigan mùa thu", "5 kiểu chân váy hot trend 2026",
        "Bí quyết chọn size áo sơ mi", "Phối đồ với quần jeans baggy",
        "Màu sắc hợp mệnh cho người tuổi Mão", "Xu hướng thời trang bền vững",
    ]
    blogs_data = []
    for i in range(NUM_BLOGS):
        title = random.choice(blog_titles) + f" - Phần {i+1}"
        content = " ".join([fake.paragraph() for _ in range(5)])
        blogs_data.append((
            random.choice(user_ids),
            title[:250],
            content,
            f"https://picsum.photos/seed/blog{i}/800/400",
            'published' if random.random() > 0.1 else 'hidden',
            random_datetime(365)
        ))
    batch_insert(cur, """
        INSERT INTO blogs (user_id, title, content, thumbnail_url, status, created_at)
        VALUES %s
    """, blogs_data)
    conn.commit()

    cur.execute("SELECT blog_id FROM blogs")
    blog_ids = [r[0] for r in cur.fetchall()]
    print(f"Đã tạo {len(blog_ids)} blogs")

    # Comments
    comments_data = []
    for bid in blog_ids:
        for _ in range(random.randint(3, COMMENTS_PER_BLOG)):
            comments_data.append((
                bid,
                random.choice(user_ids),
                None,  # Không reply
                fake.sentence()[:300],
                random_datetime(180)
            ))
    batch_insert(cur, """
        INSERT INTO blog_comments (blog_id, user_id, parent_id, content, created_at)
        VALUES %s
    """, comments_data)
    conn.commit()
    print(f"Đã tạo {len(comments_data)} comments")

    # Likes
    likes_data = set()
    for bid in blog_ids:
        for _ in range(min(LIKES_PER_BLOG, len(user_ids))):
            uid = random.choice(user_ids)
            likes_data.add((bid, uid))  # Set loại trùng
    
    batch_insert(cur, "INSERT INTO blog_likes (blog_id, user_id) VALUES %s", list(likes_data))
    conn.commit()
    print(f"Đã tạo {len(likes_data)} likes")

    # Chat sessions + messages
    chat_questions = [
        "Áo này còn size M không shop?",
        "Tư vấn size cho mình cao 1m65 nặng 55kg",
        "Ship về Hà Nội mất mấy ngày?",
        "Có được đổi trả không ạ?",
        "Chất liệu vải này là gì?",
        "Đơn hàng #123 của mình tới đâu rồi?",
    ]
    chat_answers = [
        "Dạ shop còn size M ạ. Bạn đặt luôn nhé!",
        "Với số đo của bạn, size M sẽ vừa nhất ạ.",
        "Ship Hà Nội 2-3 ngày ạ. Phí 30.000đ.",
        "Dạ shop hỗ trợ đổi trả trong 7 ngày ạ.",
        "Vải cotton 100% thoáng mát ạ.",
        "Bạn vui lòng đăng nhập để tra cứu đơn ạ.",
    ]

    session_data = [(random.choice(user_ids), random_datetime(60)) for _ in range(200)]
    from psycopg2.extras import execute_values
    sids = execute_values(
        cur,
        "INSERT INTO chat_sessions (user_id, started_at) VALUES %s RETURNING session_id",
        session_data, fetch=True
    )
    conn.commit()
    session_ids = [r[0] for r in sids]

    msg_data = []
    for sid in session_ids:
        n_turns = random.randint(2, 8)
        for _ in range(n_turns // 2):
            idx = random.randint(0, len(chat_questions) - 1)
            msg_data.append((sid, 'user', chat_questions[idx], random_datetime(60)))
            msg_data.append((sid, 'bot', chat_answers[idx], random_datetime(60)))
    
    batch_insert(cur, """
        INSERT INTO chat_messages (session_id, role, content, created_at) VALUES %s
    """, msg_data)
    conn.commit()
    print(f"Đã tạo {len(msg_data)} chat messages")

    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()