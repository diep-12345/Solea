-- Tạo DATABASE
--CREATE DATABASE web_tmdt;

-- Bảng 1: Người dùng (Quản lý tài khoản, phân quyền)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE, -- Email duy nhất
    phone VARCHAR(20) NOT NULL UNIQUE,  -- SĐT duy nhất khi đăng ký
    password_hash VARCHAR(255) NOT NULL, -- Lưu hash Argon2/bcrypt, không lưu plain text
    full_name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')), -- Phân quyền
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 2: Địa chỉ nhận hàng
CREATE TABLE user_addresses (
    address_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    address_detail TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE
);

-- Bảng 3: Nhật ký quản trị 
CREATE TABLE admin_logs (
    log_id BIGSERIAL PRIMARY KEY, -- Dùng BIGSERIAL vì bảng này sẽ sinh 100.000 dòng
    admin_id INT NOT NULL REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    target_table VARCHAR(50),
    target_id INT,
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 4: Danh mục sản phẩm (Áo, Quần, Váy,...)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Bảng 5: Sản phẩm 
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES categories(category_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price NUMERIC(12, 2) NOT NULL CHECK (base_price >= 0),
    sale_price NUMERIC(12, 2) CHECK (sale_price >= 0 AND sale_price <= base_price),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'hidden', 'out_of_stock')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 6: Biến thể sản phẩm (Size, Màu, Tồn kho)
CREATE TABLE product_variants (
    variant_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    size VARCHAR(10) NOT NULL,
    color VARCHAR(50) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0), -- Không được âm kho
    UNIQUE(product_id, size, color)
);

CREATE TABLE product_images (
    image_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE
);

-- Bảng 7: Giỏ hàng
CREATE TABLE carts (
    cart_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE, -- Mỗi user 1 giỏ
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(variant_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    UNIQUE(cart_id, variant_id)
);

-- Bảng 8: Đơn hàng và Chi tiết đơn hàng 
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    address_id INT NOT NULL REFERENCES user_addresses(address_id),
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    shipping_fee NUMERIC(12, 2) DEFAULT 0 CHECK (shipping_fee >= 0),
    payment_method VARCHAR(20) DEFAULT 'COD' CHECK (payment_method = 'COD'),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipping', 'delivered', 'cancelled', 'returned')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id BIGSERIAL PRIMARY KEY, -- BIGSERIAL để dễ sinh 100.000 dòng
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(variant_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0) -- Lưu giá tại thời điểm mua
);

-- Bảng 9: Yêu cầu hoàn hàng
CREATE TABLE return_requests (
    return_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    reason TEXT NOT NULL,
    description TEXT,
    evidence_image_url TEXT,
    bank_name VARCHAR(100),
    bank_account_number VARCHAR(50),
    bank_account_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    refund_status VARCHAR(20) DEFAULT 'not_refunded' CHECK (refund_status IN ('not_refunded', 'refunded')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 10: Đánh giá sản phẩm
CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY, -- BIGSERIAL để sinh 100.000 dòng
    user_id INT NOT NULL REFERENCES users(user_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    order_item_id BIGINT NOT NULL REFERENCES order_items(order_item_id), -- Xác thực đã mua
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    status VARCHAR(20) DEFAULT 'visible' CHECK (status IN ('visible', 'hidden')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_images (
    image_id SERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    image_url TEXT NOT NULL
);

-- Bảng 11: Blog và Cộng đồng
CREATE TABLE blogs (
    blog_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    thumbnail_url TEXT,
    status VARCHAR(20) DEFAULT 'published' CHECK (status IN ('published', 'hidden')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_comments (
    comment_id SERIAL PRIMARY KEY,
    blog_id INT NOT NULL REFERENCES blogs(blog_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(user_id),
    parent_id INT REFERENCES blog_comments(comment_id) ON DELETE CASCADE, -- Hỗ trợ reply
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_likes (
    like_id SERIAL PRIMARY KEY,
    blog_id INT NOT NULL REFERENCES blogs(blog_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(user_id),
    UNIQUE(blog_id, user_id) -- Chống spam like
);

-- Bảng 12: Chatbot
CREATE TABLE chat_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id), -- Có thể NULL nếu khách vãng lai
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    message_id BIGSERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'bot')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);