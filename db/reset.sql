-- Chỉ chạy khi muốn xóa sạch và làm lại từ đầu
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;