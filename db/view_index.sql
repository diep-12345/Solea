-- Tạo view

-- View thống kê doanh thu theo tháng 
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    TO_CHAR(created_at, 'YYYY-MM') AS month,
    COUNT(order_id) AS total_orders,
    SUM(total_amount) AS revenue
FROM orders
WHERE status = 'delivered'
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY month DESC;

-- Tạo index

-- Mỗi user chỉ có tối đa 1 địa chỉ mặc định
CREATE UNIQUE INDEX uq_user_default_address ON user_addresses (user_id) WHERE is_default = TRUE;
CREATE INDEX idx_user_addresses_user ON user_addresses (user_id);

-- Index phục vụ tra cứu log
CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_target ON admin_logs(target_table, target_id);
CREATE INDEX idx_admin_logs_time ON admin_logs(created_at DESC);


-- Index phục vụ tìm kiếm đơn hàng theo user và trạng thái
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Index phục vụ báo cáo Top sản phẩm bán chạy
CREATE INDEX idx_order_items_variant ON order_items(variant_id);

-- Index phục vụ lọc sản phẩm theo danh mục và trạng thái (Trang chủ)
CREATE INDEX idx_products_category_status ON products(category_id, status);

-- Index phục vụ truy vấn đánh giá theo sản phẩm (Hiển thị trang chi tiết)
CREATE INDEX idx_reviews_product ON reviews(product_id) WHERE status = 'visible';