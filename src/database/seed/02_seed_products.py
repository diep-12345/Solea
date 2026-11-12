# Dataset: https://huggingface.co/datasets/arturayupov/womens-fashion-catalog

import random
from collections import defaultdict
from slugify import slugify
import pandas as pd
from datasets import load_dataset
from database.db.db_connect import get_connection
from utils import fake, batch_insert
import pandas as pd

NUM_PRODUCTS   = 200    # Số sản phẩm
USD_TO_VND     = 25_000          # tỷ giá quy đổi
FALLBACK_IMG = "https://picsum.photos/seed/{seed}/600/800"

# Ánh xạ product_type/category sang danh mục tiếng Việt Váy / Áo / Quần
CATEGORY_VI = {
    "Váy": [
        "dress", "skirt", "gown", "frock", "sundress",
        "maxi", "midi", "mini", "jumpsuit", "romper",
    ],
    "Áo": [
        "top", "shirt", "blouse", "sweater", "sweatshirt",
        "jacket", "coat", "cardigan", "hoodie", "vest",
        "bodysuit", "tee", "t-shirt", "polo", "tunic",
        "crop", "bralette", "bra", "camisole", "cami",
        "kimono", "shacket", "poncho", "cape", "pullover",
    ],
    "Quần": [
        "pants", "jeans", "trousers", "shorts", "leggings",
        "chinos", "joggers", "culottes", "skort", "overalls",
        "dungarees", "cargo",
    ],
}

DEFAULT_CATEGORY = "Khác"

_CATEGORY_PRIORITY = ["Váy", "Áo", "Quần"]

COLOR_MAP = {
    "white": "Trắng", "black": "Đen", "red": "Đỏ", "blue": "Xanh dương", "navy": "Xanh navy", "green": "Xanh lá", "yellow": "Vàng",
    "pink": "Hồng", "purple": "Tím", "orange": "Cam", "brown": "Nâu", "grey": "Xám", "gray": "Xám",
    "beige": "Be", "cream": "Kem", "ivory": "Ngà", "gold": "Vàng kim", "silver": "Bạc", "black/pewter": "Đen xám",
    "black rhinestone": "Đen đính đá", "rose gold": "ồng kim", "charcoal": "Xám than", "dusty pink": "Hồng tro",
    "dusty blue": "Xanh tro", "dusty teal": "Xanh mòng két tro", "dust storm": "Nâu xám", "pastel blue": "Xanh pastel", "light blue": "Xanh nhạt", "sky blue": "Xanh da trời",
    "cloudy blue": "Xanh mây", "deep red": "Đỏ đậm", "dark brown": "Nâu đậm", "dark green": "Xanh lá đậm", "dark gray": "Xám đậm",
    "fuchsia pink": "Hồng sen", "hot pink": "Hồng nóng", "blush pink": "Hồng phấn", "light mauve": "Tím nhạt", "mid green": "Xanh lá trung",
    "camel": "Nâu lạc đà", "cognac": "Nâu cognac", "caramel": "Nâu caramel",
    "mocha": "Nâu cà phê", "taupe": "Be xám", "khaki": "Kaki", "tan": "Nâu nhạt", "whisky": "Nâu whisky",
    "nude": "Da người", "olive": "Xanh oliu", "teal": "Xanh mòng két", "cerulean": "Xanh thiên thanh", "mint": "Xanh bạc hà",
    "lavender": "Oải hương", "burgundy": "Đỏ rượu", "maroon": "Đỏ mận", "mustard": "Vàng mù tạt",
    "coral": "San hô", "peach": "Đào", "rose": "Hồng phấn", "strawberry": "Đỏ dâu",
    "cerise": "Đỏ anh đào", "rainbow": "Nhiều màu", "multi": "Nhiều màu", "multicolor": "Nhiều màu", "leopard": "Họa tiết báo",
}

FALLBACK_COLORS = [
    "Đen", "Trắng", "Be", "Xanh navy", "Đỏ", "Hồng",
    "Xám", "Nâu", "Xanh lá", "Vàng", "Kem", "Đỏ rượu",
]

def load_parquet(config: str) -> pd.DataFrame:
    """Đọc trực tiếp file Parquet từ HuggingFace Hub."""
    url = (
        "hf://datasets/arturayupov/womens-fashion-catalog/"
        f"{config}.parquet"
    )
    return pd.read_parquet(url)

def _safe_int(value, default=0):
    try:
        if value is None or pd.isna(value):
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _safe_float(value, default=0.0):
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _price_vnd(usd_value) -> int:
    # Chuyển USD sang VND
    usd = _safe_float(usd_value, 0.0)
    vnd = usd * USD_TO_VND
    return int(round(vnd / 1000) * 1000)

def pick_category(product_type, category=None) -> str:
    # Ánh xạ category sang tiếng việt
    for raw in (product_type, category):
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            continue
        text = str(raw).lower().strip()
        if not text:
            continue
        for cat_vi in _CATEGORY_PRIORITY:
            for kw in CATEGORY_VI[cat_vi]:
                if kw in text:
                    return cat_vi
    return DEFAULT_CATEGORY

def normalize_color(raw) -> str | None:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip().lower()
    if not text:
        return None

    # Sort theo độ dài giảm dần
    for key in sorted(COLOR_MAP.keys(), key=len, reverse=True):
        if key in text:
            return COLOR_MAP[key]
    # Không nhận diện được thì giữ nguyên
    return text.title()[:50]

def diversify_colors(colors: set, min_colors: int = 3) -> set:
    colors = set(colors)
    if len(colors) >= min_colors:
        return colors
    candidates = [c for c in FALLBACK_COLORS if c not in colors]
    random.shuffle(candidates)
    while len(colors) < min_colors and candidates:
        colors.add(candidates.pop())
    return colors

def ensure_images(pid: int, img_rows: list) -> list[str]:
    urls = [str(r["image_url"]) for r in img_rows if r.get("image_url")]
    if len(urls) == 0:
        urls = [FALLBACK_IMG.format(seed=pid)]
    if len(urls) == 1:
        urls.append(FALLBACK_IMG.format(seed=f"{pid}-2"))
    return urls


def seed():
    conn = get_connection()
    cur = conn.cursor()

    # Load dataset 
    print("Đang tải dataset")
    df_products = load_parquet("products")
    df_images = load_parquet("images")
    df_variants = load_parquet("variants")

    # Chỉ giữ sản phẩm có ảnh và biến thể
    valid_ids = set(df_images["product_id"].unique()) & set(
        df_variants["product_id"].unique()
    )
    df_products = df_products[df_products["id"].isin(valid_ids)]

    # Lấy mẫu ngẫu nhiên 200 sản phẩm
    random.seed(42)
    sample_ids = random.sample(
        list(df_products["id"]), min(NUM_PRODUCTS, len(df_products))
    )
    df_products = df_products[df_products["id"].isin(sample_ids)].reset_index(
        drop=True
    )
    print(f"Đã chọn {len(df_products)} sản phẩm để seed.")

    # Gom ảnh và biến thể theo product_id
    images_by_pid = defaultdict(list)
    for _, row in df_images.iterrows():
        if row["product_id"] in sample_ids:
            images_by_pid[row["product_id"]].append(row)

    variants_by_pid = defaultdict(list)
    for _, row in df_variants.iterrows():
        if row["product_id"] in sample_ids:
            variants_by_pid[row["product_id"]].append(row)

    # Tạo categories 
    cat_names = {pick_category(r.get("product_type"), r.get("category"))for _, r in df_products.iterrows()}
    cat_data = [(name, slugify(name), True) for name in cat_names]

    batch_insert(
        cur,
        "INSERT INTO categories (name, slug, is_active) VALUES %s "
        "ON CONFLICT (slug) DO NOTHING",
        cat_data,
    )
    conn.commit()

    cur.execute("SELECT category_id, name FROM categories")
    cat_id_map = {name: cid for cid, name in cur.fetchall()}
    print(f"Đã đảm bảo {len(cat_id_map)} categories tồn tại.")

    # Chuẩn bị dữ liệu 
    prod_rows     = []   # (category_id, name, description, base_price, sale_price, status)
    prod_meta     = []   # lưu metadata tạm để map sau khi có product_id

    for idx, row in df_products.iterrows():
        pid = row["id"]
        category_vi = pick_category(row.get("product_type"), row.get("category"))
        category_id = cat_id_map[category_vi]

        # Tên và mô tả từ dataset
        name = str(row.get("title", "Sản phẩm"))[:255]
        description = str(row.get("description", f"Sản phẩm {name}"))
        # Giá: ưu tiên price_min, nếu không có thì price_max
        base_price = _price_vnd(row.get("price_min") or row.get("price_max") or 0)
        if base_price <= 0:
            base_price = random.randint(150, 800) * 1000

        # Sale price cho 40% sản phẩm
        sale_price = None
        if random.random() < 0.4:
            discount = random.uniform(0.7, 0.9)
            sale_price = int(round(base_price * discount / 1000) * 1000)

        prod_rows.append(
            (category_id, name, description, base_price, sale_price, "active")
        )
        prod_meta.append(
            {
                "temp_id": idx,
                "original_id": pid,
                "images": images_by_pid.get(pid, []),
                "variants": variants_by_pid.get(pid, []),
            }
        )
        

    from psycopg2.extras import execute_values

    inserted = execute_values(
        cur, """
        INSERT INTO products
            (category_id, name, description, base_price, sale_price, status)
        VALUES %s RETURNING product_id
        """, prod_rows, fetch=True,
    )
    conn.commit()
    new_pids = [r[0] for r in inserted]
    print(f"Đã tạo {len(new_pids)} products.")

    # Map temp_id đến product_id thật
    temp_to_real = {meta["temp_id"]: real_pid for meta, real_pid in zip(prod_meta, new_pids)}

    # Tạo variants 
    for meta in prod_meta:
        real_pid = temp_to_real[meta["temp_id"]]
        variants = meta["variants"]
        used_combos = set()
          
        variant_rows = []  
        colors_by_temp = {} 
        
        for meta in prod_meta:
            real_pid = temp_to_real[meta["temp_id"]]
            used      = set()
            colors_norm = set()

            for v in meta["variants"]:
                size  = str(v.get("size") or "M").strip()[:10]
                color = normalize_color(v.get("color")) or random.choice(FALLBACK_COLORS)
                colors_norm.add(color)

                if (size, color) in used:
                    continue
                used.add((size, color))
                in_stock = v.get("in_stock")
                stock = ( 0 if in_stock is False or in_stock == 0
                    else random.choice([5, 10, 20, 50, 100]))
                sku = f"SP{real_pid}-{slugify(size)}-{slugify(color)}"[:50]
                variant_rows.append((real_pid, size, color, sku, stock))

            # Bổ sung màu nếu sản phẩm có < 3 màu
            colors_by_temp[meta["temp_id"]] = diversify_colors(colors_norm, min_colors=3)


    batch_insert(
        cur, """
        INSERT INTO product_variants
            (product_id, size, color, sku, stock_quantity)
        VALUES %s
        """, variant_rows,
    )
    conn.commit()
    print(f"Đã thêm {len(variant_rows)} variants.")

    #  Tạo images
    image_rows = []
    for meta in prod_meta:
        real_pid = temp_to_real[meta["temp_id"]]
        sorted_imgs = sorted(meta["images"], key=lambda r: _safe_int(r.get("image_index")))
        urls = ensure_images(real_pid, sorted_imgs)

        image_rows.append((real_pid, urls[0], True,  None))
        image_rows.append((real_pid, urls[1], False, None))
        for extra in urls[2:]:
            image_rows.append((real_pid, extra, False, None))

        for color in colors_by_temp.get(meta["temp_id"], set()):
            color_url = f"{urls[0]}?color={slugify(color)}"
            image_rows.append((real_pid, color_url, False, color))

    batch_insert(
        cur, """
        INSERT INTO product_images
            (product_id, image_url, is_primary, color)
        VALUES %s
        """, image_rows,
    )
    conn.commit()
    print(f"Đã thêm {len(image_rows)} images.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()