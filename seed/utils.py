import random
from faker import Faker

Faker.seed(42)
# Khởi tạo Faker tiếng Việt
fake = Faker('vi_VN')

def batch_insert(cur, sql, data_list, batch_size=1000):
    # Insert nhiều dòng 1 lượt
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        from psycopg2.extras import execute_values
        execute_values(cur, sql, batch)  

def random_datetime(days_back=730):
    # Sinh ngày ngẫu nhiên trong khoảng N ngày về trước.
    import datetime
    return fake.date_time_between(start_date=f'-{days_back}d', end_date='now')