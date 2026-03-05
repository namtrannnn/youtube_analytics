from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db # Hàm lấy session DB của bạn
from app.models import NguoiDung
from app.schemas import UserCreate, UserLogin, TokenInfo
from app.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # KIỂM TRA ĐỘ DÀI MẬT KHẨU TỐI THIỂU 8 KÝ TỰ 
    if len(user.mat_khau) < 8:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 8 ký tự.")
    # 1. Kiểm tra Email hoặc Tên đăng nhập đã tồn tại chưa
    db_user_email = db.query(NguoiDung).filter(NguoiDung.Email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký.")
        
    db_user_name = db.query(NguoiDung).filter(NguoiDung.TenDangNhap == user.ten_dang_nhap).first()
    if db_user_name:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại.")

    # 2. Băm mật khẩu
    hashed_password = get_password_hash(user.mat_khau)

    # 3. Tạo user mới và lưu vào DB
    new_user = NguoiDung(
        TenDangNhap=user.ten_dang_nhap,
        Email=user.email,
        MatKhau=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Đăng ký tài khoản thành công!", "user_id": new_user.MaND}

@router.post("/login", response_model=TokenInfo)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Tìm user bằng Email
    db_user = db.query(NguoiDung).filter(NguoiDung.Email == user.email).first()
    
    # 2. Kiểm tra user có tồn tại và mật khẩu có đúng không
    if not db_user or not verify_password(user.mat_khau, db_user.MatKhau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db_user.TrangThai != 'active':
         raise HTTPException(status_code=403, detail="Tài khoản của bạn đã bị khóa.")

    # 3. Tạo JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.MaND), "email": db_user.Email, "role": db_user.VaiTro},
        expires_delta=access_token_expires
    )

    # 4. Trả về Token và thông tin cơ bản cho React hiển thị lên Header
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": db_user.MaND,
            "name": db_user.TenDangNhap,
            "email": db_user.Email,
            "role": db_user.VaiTro
        }
    }