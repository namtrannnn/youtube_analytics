from datetime import datetime, timedelta
from jose import jwt
import bcrypt

# Cấu hình chuỗi bí mật (Nên để trong file .env)
SECRET_KEY = "afafanyuyongyiafa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token sống được 7 ngày

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với DB không"""
    # Chuyển đổi chuỗi thành dạng byte để bcrypt đọc được
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def get_password_hash(password: str) -> str:
    """Băm mật khẩu trước khi lưu vào DB"""
    # Chuyển đổi chuỗi thành byte
    password_byte_enc = password.encode('utf-8')
    
    # Tạo chuỗi băm an toàn
    hashed_password = bcrypt.hashpw(password_byte_enc, bcrypt.gensalt())
    
    # Trả về dạng chuỗi (string) để lưu vào PostgreSQL
    return hashed_password.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Tạo JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt