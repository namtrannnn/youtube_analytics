from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class NguoiDung(Base):
    # 1. Ép tên bảng thành chữ thường chuẩn với PostgreSQL
    __tablename__ = "nguoidung" 

    # 2. Khai báo rõ tham số đầu tiên là tên cột (chữ thường) trong DB
    MaND = Column("mand", Integer, primary_key=True, index=True)
    TenDangNhap = Column("tendangnhap", String(100), unique=True, index=True, nullable=False)
    Email = Column("email", String(255), unique=True, index=True)
    MatKhau = Column("matkhau", String(255), nullable=False)
    VaiTro = Column("vaitro", String(50), default='user')
    TrangThai = Column("trangthai", String(20), default='active')
    ThoiGianTao = Column("thoigiantao", DateTime(timezone=True), server_default=func.now())
