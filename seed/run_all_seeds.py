import subprocess
import sys

SCRIPTS = [

    "seed/02_seed_products.py",
    "seed/03_seed_orders.py",
    "seed/04_seed_reviews.py",
    "seed/05_seed_blog_chat.py",
    "seed/06_seed_admin_logs.py",
]

for script in SCRIPTS:
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Lỗi ở {script}. Dừng lại.")
        sys.exit(1)

print("Đã seed toàn bộ dữ liệu.")