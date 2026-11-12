BEGIN;

ALTER TABLE orders
    ADD COLUMN discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0
    CHECK (discount_amount >= 0);

COMMENT ON COLUMN orders.discount_amount IS 'Số tiền giảm giá áp dụng cho đơn hàng (VNĐ)';

-- Kiểm tra toàn vẹn: không có dòng nào NULL 
DO $$
DECLARE
    null_count INT;
BEGIN
    SELECT COUNT(*) INTO null_count FROM orders WHERE discount_amount IS NULL;
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Migration failed: % rows have NULL discount_amount', null_count;
    END IF;
END $$;

-- Đăng ký migration đã áp dụng
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT
);
INSERT INTO schema_migrations (version, description)
VALUES ('001', 'add discount_amount to orders')
ON CONFLICT (version) DO NOTHING;

COMMIT;