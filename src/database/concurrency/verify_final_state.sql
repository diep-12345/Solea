-- Thay :variant_id bằng ID in từ log
SELECT variant_id, stock_quantity FROM product_variants WHERE variant_id = :variant_id;
SELECT COUNT(*) AS order_items_count FROM order_items WHERE variant_id = :variant_id;
SELECT o.order_id, o.user_id, o.status FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id WHERE oi.variant_id = :variant_id;