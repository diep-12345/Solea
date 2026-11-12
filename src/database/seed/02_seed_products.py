import random
from datasets import load_dataset
from slugify import slugify
from db_connect import get_connection
from utils import fake, batch_insert

# Cấu hình
NUM_PRODUCTS_TO_SEED = 2000  # Số lượng sản phẩm
SIZES = ['S', 'M', 'L', 'XL', 'XXL']
COLORS = ['Đen', 'Trắng', 'Đỏ', 'Xanh navy', 'Be', 'Hồng', 'Xám']

# Map masterCategory/subCategory của dataset sang danh mục tiếng Việt
CATEGORY_MAP = {
    'Topwear': 'Áo',
    'Bottomwear': 'Quần',
    'Dresses': 'Váy',
    'Innerwear': 'Đồ lót',
    'Saree': 'Váy',
    'Apparel Set': 'Bộ đồ',
    'Loungewear and Nightwear': 'Đồ mặc nhà',
    'Socks': 'Phụ kiện',
}


def seed():
    conn = get_connection()
    cur = conn.cursor()
    
        # Tạo categories từ CATEGORY_MAP
    cat_data = []
    for master_cat in set(CATEGORY_MAP.values()):
        cat_data.append((master_cat, slugify(master_cat), True))
        
    batch_insert(cur, "INSERT INTO categories (name, slug, is_active) VALUES %s ON CONFLICT (slug) DO NOTHING", cat_data)
    conn.commit()
    
    cur.execute("SELECT category_id, name FROM categories")
    cat_id_map = {name: cid for cid, name in cur.fetchall()}
    print(f"Đã tạo {len(cat_id_map)} categories")

    # Tải dataset từ HuggingFace
    ds = load_dataset(
        'ceyda/fashion-products-small', 
        split=f'train[:{NUM_PRODUCTS_TO_SEED * 3}]',
        columns=['id', 'link', 'masterCategory', 'subCategory', 'gender']
    )
        # Lấy quần áo và váy
    ds = ds.filter(lambda x: x['masterCategory'] == 'Apparel')

    ds = ds.select(range(min(NUM_PRODUCTS_TO_SEED, len(ds))))
    print(f"Đã tải {len(ds)} dòng dữ liệu.")

    # Xử lý Products
    prod_data = []
    product_links = {} # Lưu link ảnh theo id sản phẩm (tạm)
    for row in ds:
        # Lấy category tiếng Việt, nếu không có thì mặc định là 'Khác'
        master = row['subCategory']
        category_name = CATEGORY_MAP.get(master, 'Khác')
            
        # Nếu chưa có category 'Khác', tạo mới
        if category_name not in cat_id_map:
            cur.execute("INSERT INTO categories (name, slug, is_active) VALUES (%s, %s, %s) RETURNING category_id", 
                        (category_name, slugify(category_name), True))
            cat_id_map[category_name] = cur.fetchone()[0]
            conn.commit()
            
            # Tạo tên sản phẩm từ subCategory
        product_name = f"{row['subCategory']} {row['gender']}".strip()
        base_price = random.randint(150, 800) * 1000
            
        prod_data.append((
            cat_id_map[category_name],
            product_name[:250], # Giới hạn độ dài
            f"Sản phẩm {product_name} chất liệu cao cấp.",
            base_price,
            None, # Tạm thời không có sale_price
            'active'
        ))
        product_links[row['id']] = row['link'] # Lưu link ảnh theo ID gốc

        # Insert products và lấy lại ID đã tạo
    from psycopg2.extras import execute_values
    inserted_products = execute_values(
        cur,
        """
        INSERT INTO products (category_id, name, description, base_price, sale_price, status)
        VALUES %s RETURNING product_id
        """,
        prod_data,
        fetch=True
    )
    conn.commit()
    new_product_ids = [r[0] for r in inserted_products]
    print(f"Đã tạo {len(new_product_ids)} products")

    # 4. Tạo Variants và Product Images
    variant_data = []
    image_data = []
        
    # Lấy lại ID gốc của dataset để map với link ảnh
    original_ids = list(product_links.keys())

    for new_pid, original_id in zip(new_product_ids, original_ids):
        # Tạo 2-3 biến thể ngẫu nhiên cho mỗi sản phẩm
        n_variants = random.randint(2, 4)
        used_combos = set()
        for _ in range(n_variants):
            size = random.choice(SIZES)
            color = random.choice(COLORS)
            if (size, color) in used_combos: continue
            used_combos.add((size, color))
            sku = f"SP{new_pid}-{size}-{color.replace(' ','')}"
            stock = random.choice([0, 5, 10, 20, 50, 100])
            variant_data.append((new_pid, size, color, sku, stock))
        
        # Insert link ảnh vào bảng product_images
        image_url = product_links[original_id]
        image_data.append((new_pid, image_url, True)) # True = ảnh chính

    batch_insert(cur, """
        INSERT INTO product_variants (product_id, size, color, sku, stock_quantity)
        VALUES %s
    """, variant_data)

    batch_insert(cur, """
        INSERT INTO product_images (product_id, image_url, is_primary)
        VALUES %s
    """, image_data)
    conn.commit()
    print(f"Đã tạo {len(variant_data)} variants và {len(image_data)} images.")


if __name__ == "__main__":
    seed()