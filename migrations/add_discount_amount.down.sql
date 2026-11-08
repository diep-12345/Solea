-- Rollback Migration 001
BEGIN;

ALTER TABLE orders DROP COLUMN IF EXISTS discount_amount;

DELETE FROM schema_migrations WHERE version = '001';

COMMIT;