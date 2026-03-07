from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db # Hàm lấy session DB của bạn
from app.models import NguoiDung,QuenMatKhau
from app.schemas import UserCreate, UserLogin, TokenInfo
from app.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import secrets
from pydantic import BaseModel
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
class GoogleLoginRequest(BaseModel):
    credential: str

class ForgotPasswordEmail(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    mat_khau_moi: str
    
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email: str, otp: str):
    sender_email = "2224802010223@student.tdmu.edu.vn"
    sender_password = "lgrx fesf cmgb tbfm"

    subject = "Mã xác nhận đổi mật khẩu"
    body = f"""
        Xin chào,

        Mã xác nhận đổi mật khẩu của bạn là: {otp}

        Mã này sẽ hết hạn sau 5 phút.

        Nếu bạn không yêu cầu, hãy bỏ qua email này.
        """

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()


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

@router.post("/google", response_model=TokenInfo)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    GOOGLE_CLIENT_ID = "596162162962-hhajtorejulr1jr7sbub5pmqqv4jt8b7.apps.googleusercontent.com"

    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Google token không hợp lệ")

    email = idinfo.get("email")
    name = idinfo.get("name")
    google_sub = idinfo.get("sub")
    picture = idinfo.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Không lấy được email từ Google")

    # 1. ưu tiên tìm theo GoogleSub
    db_user = None
    if google_sub:
        db_user = db.query(NguoiDung).filter(NguoiDung.GoogleSub == google_sub).first()

    # 2. nếu chưa có thì tìm theo email
    if not db_user:
        db_user = db.query(NguoiDung).filter(NguoiDung.Email == email).first()

    # 3. nếu chưa có user thì tạo mới
    if not db_user:
        username = name if name else email.split("@")[0]

        # tránh trùng TenDangNhap
        base_username = username
        count = 1
        while db.query(NguoiDung).filter(NguoiDung.TenDangNhap == username).first():
            username = f"{base_username}{count}"
            count += 1

        db_user = NguoiDung(
            TenDangNhap=username,
            Email=email,
            MatKhau=None,              # vì account Google không cần mật khẩu local
            GoogleSub=google_sub,
            AnhDaiDien=picture,
            LoaiDangNhap="google"
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    else:
        # 4. nếu user đã có thì cập nhật thông tin Google
        if google_sub and not db_user.GoogleSub:
            db_user.GoogleSub = google_sub

        if picture:
            db_user.AnhDaiDien = picture

        db_user.LoaiDangNhap = "google"

        db.commit()
        db.refresh(db_user)

    # 5. tạo JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={
            "sub": str(db_user.MaND),
            "email": db_user.Email,
            "role": db_user.VaiTro
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": db_user.MaND,
            "name": db_user.TenDangNhap,
            "email": db_user.Email,
            "role": db_user.VaiTro,
            "avatar": db_user.AnhDaiDien,
            "login_type": db_user.LoaiDangNhap
        }
    }

@router.post("/forgot-password/send-otp")
def send_otp(data: ForgotPasswordEmail, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.Email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại.")

    if user.LoaiDangNhap == "google" and not user.MatKhau:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản này đăng nhập bằng Google, không thể đặt lại mật khẩu."
        )

    # Xóa hoặc vô hiệu hóa OTP cũ chưa dùng của user này
    db.query(QuenMatKhau).filter(
        QuenMatKhau.MaND == user.MaND,
        QuenMatKhau.DaSuDung == False
    ).delete(synchronize_session=False)

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    reset_record = QuenMatKhau(
        MaND=user.MaND,
        Token=otp,
        ThoiGianHetHan=expiry,
        DaSuDung=False
    )

    db.add(reset_record)
    db.commit()

    send_otp_email(user.Email, otp)

    return {"message": "Mã OTP đã được gửi tới email."}

@router.post("/forgot-password/verify-otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.Email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại.")

    otp_record = db.query(QuenMatKhau).filter(
        QuenMatKhau.MaND == user.MaND,
        QuenMatKhau.Token == data.otp,
        QuenMatKhau.DaSuDung == False
    ).order_by(QuenMatKhau.ThoiGianTao.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP không đúng.")

    if otp_record.ThoiGianHetHan < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP đã hết hạn.")

    return {"message": "Xác minh OTP thành công."}

@router.post("/forgot-password/reset")
@router.post("/forgot-password/reset")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.Email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại.")

    if len(data.mat_khau_moi) < 8:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 8 ký tự.")

    otp_record = db.query(QuenMatKhau).filter(
        QuenMatKhau.MaND == user.MaND,
        QuenMatKhau.Token == data.otp,
        QuenMatKhau.DaSuDung == False
    ).order_by(QuenMatKhau.ThoiGianTao.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP không hợp lệ.")

    if otp_record.ThoiGianHetHan < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP đã hết hạn.")

    user.MatKhau = get_password_hash(data.mat_khau_moi)
    otp_record.DaSuDung = True

    db.commit()

    return {"message": "Đổi mật khẩu thành công."}