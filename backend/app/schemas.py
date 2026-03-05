from pydantic import BaseModel, EmailStr, Field

# Data React gửi lên khi Đăng ký
class UserCreate(BaseModel):
    ten_dang_nhap: str
    email: EmailStr
    # Ràng buộc mật khẩu: tối thiểu 8, tối đa 50 ký tự
    mat_khau: str = Field(..., min_length=8, max_length=50)

# Data React gửi lên khi Đăng nhập
class UserLogin(BaseModel):
    email: EmailStr
    mat_khau: str = Field(..., min_length=8, max_length=50)

# Data trả về khi đăng nhập thành công
class TokenInfo(BaseModel):
    access_token: str
    token_type: str
    user_info: dict