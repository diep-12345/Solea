import random
import string
import unicodedata
import datetime
from faker import Faker
from psycopg2.extras import execute_values

Faker.seed(42)
random.seed(42)

# Faker tiếng Việt
fake = Faker('vi_VN')


# Đầu số di động VN
VN_PHONE_PREFIXES = [
    '032','033','034','035','036','037','038','039',
    '052','056','058','059',
    '070','076','077','078','079',
    '081','082','083','084','085','086','087','088','089',
    '090','091','092','093','094','095','096','097','098','099',
]

# Thành phố
VN_CITIES = [
    'Hà Nội','Hồ Chí Minh','Đà Nẵng','Hải Phòng','Cần Thơ',
    'Biên Hòa','Huế','Nha Trang','Buôn Ma Thuột','Vũng Tàu',
    'Đà Lạt','Quy Nhơn','Thái Nguyên','Nam Định','Vinh',
    'Bắc Ninh','Hạ Long','Thanh Hóa','Pleiku','Mỹ Tho',
    'Phan Thiết','Rạch Giá','Thủ Dầu Một','Long Xuyên',
]

# Đường
VN_STREETS = [
    'Nguyễn Trãi','Trần Hưng Đạo','Lê Lợi','Hai Bà Trưng',
    'Lý Tự Trọng','Nguyễn Huệ','Điện Biên Phủ','Võ Văn Tần',
    'Phan Đình Phùng','Bà Triệu','Trường Chinh','Giải Phóng',
    'Nguyễn Văn Linh','Lê Văn Việt','Đinh Tiên Hoàng','Pasteur',
    'Nguyễn Thị Minh Khai','Cách Mạng Tháng 8','Hoàng Diệu',
    'Lê Duẩn','Nguyễn Tri Phương','Xô Viết Nghệ Tĩnh',
    'Phạm Văn Đồng','Quang Trung','Tôn Đức Thắng',
]

# Quận
VN_DISTRICTS = [
    'Quận 1','Quận 3','Quận 5','Quận 7','Quận 10','Quận 11',
    'Quận Bình Thạnh','Quận Tân Bình','Quận Phú Nhuận','Quận Gò Vấp',
    'Quận Hoàn Kiếm','Quận Đống Đa','Quận Ba Đình','Quận Cầu Giấy',
    'Quận Thanh Xuân','Quận Hai Bà Trưng','Quận Hà Đông',
    'Quận Hải Châu','Quận Thanh Khê','Quận Sơn Trà',
    'Huyện Nhà Bè','Huyện Củ Chi','Huyện Hóc Môn',
]

# Phường
VN_WARDS = [
    'Phường Bến Nghé', 'Phường Bến Thành', 'Phường Thảo Điền', 'Phường 1',
    'Phường Dịch Vọng', 'Phường Trung Hòa', 'Phường Láng Hạ', 'Phường Hàng Bạc',
    'Phường Thạch Thang', 'Phường An Hải Bắc',
]

# Miền email
EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com']


def remove_vn_accents(text: str) -> str:
    # Bỏ dấu tiếng Việt để tạo username
    text = text.replace('đ', 'd').replace('Đ', 'D')
    nfkd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def random_vn_phone() -> str:
    # Sinh SĐT 
    prefix = random.choice(VN_PHONE_PREFIXES)               # 3 số đầu
    suffix = ''.join(random.choices(string.digits, k=7))    # 7 số còn lại
    return prefix + suffix                                  # tổng 10 số


def random_email(full_name: str = None) -> str:
    # Sinh email từ họ tên
    if not full_name:
        full_name = fake.name()
    uname = remove_vn_accents(full_name).lower()
    parts = [p for p in uname.split() if p]
    if not parts:
        parts = ['user']
    username = '.'.join(parts)
    username = ''.join(c for c in username if c.isalnum() or c == '.')
    username += str(random.randint(10, 9999))               # tránh trùng
    return f"{username}@{random.choice(EMAIL_DOMAINS)}"


def random_vn_address() -> tuple[str, str, str, str]:
    # Sinh địa chỉ
    house = random.randint(1, 999)
    if random.random() < 0.3:   # 30% có hẻm
        house = f"{house}/{random.randint(1, 50)}"
    street_address = f"Số {house} đường {random.choice(VN_STREETS)}"
    return (
        random.choice(VN_CITIES),
        random.choice(VN_DISTRICTS),
        random.choice(VN_WARDS),
        street_address,
    )


def fake_bcrypt_hash() -> str:
    # Sinh chuỗi giả có 60 ký tự
    alphabet = string.ascii_letters + string.digits + './'
    body = ''.join(random.choices(alphabet, k=53))
    return f"$2b$12${body}"


def batch_insert(cur, sql, data_list, batch_size=1000):
    # Insert nhiều dòng 1 lượt, chia theo batch để tránh quá tải.
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        execute_values(cur, sql, batch)


def random_datetime(days_back: int = 730) -> datetime.datetime:
    # Sinh ngày ngẫu nhiên trong N ngày về trước.
    return fake.date_time_between(start_date=f'-{days_back}d', end_date='now')