from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# =========================================================================
# CẤU HÌNH KẾT NỐI POSTGRESQL
# Bạn hãy thay đổi User, Password, Host và Tên DB cho khớp với cấu hình của bạn
# Ví dụ: postgresql://<user>:<password>@<host>:<port>/<db_name>
# Nếu chạy Docker, host có thể là 'db' hoặc 'postgres'. Nếu chạy ở ngoài, host là 'localhost'
# =========================================================================
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@db:5432/yt_analyzer_db" 
)

# Tạo Engine kết nối tới CSDL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo Session để thực hiện các truy vấn (CRUD)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để các file Models kế thừa
Base = declarative_base()

# Hàm lấy DB Session (Dùng làm Dependency Injection trong FastAPI)
def get_db():
    db = SessionLocal()
    try:
        # Thử test kết nối ngay khi vừa mở
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI DATABASE: {e}")
        raise e
    finally:
        db.close()