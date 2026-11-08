DROP INDEX IF EXISTS idx_order_items_variant;

EXPLAIN (ANALYZE, BUFFERS)
SELECT p.product_id, p.name,
       SUM(oi.quantity * oi.unit_price) AS revenue,
       SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.name
ORDER BY revenue DESC LIMIT 10;