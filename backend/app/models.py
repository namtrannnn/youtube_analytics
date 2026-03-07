from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class NguoiDung(Base):
    __tablename__ = "nguoidung"

    MaND = Column("mand", Integer, primary_key=True, index=True)
    TenDangNhap = Column("tendangnhap", String(100), unique=True, index=True, nullable=False)
    Email = Column("email", String(255), unique=True, index=True, nullable=True)
    MatKhau = Column("matkhau", String(255), nullable=True)  # Google login có thể không có mật khẩu

    GoogleSub = Column("googlesub", String(100), unique=True, index=True, nullable=True)
    AnhDaiDien = Column("anhdaidien", Text, nullable=True)
    LoaiDangNhap = Column("loaidangnhap", String(20), default="local")

    VaiTro = Column("vaitro", String(50), default="user")
    TrangThai = Column("trangthai", String(20), default="active")
    ThoiGianTao = Column("thoigiantao", DateTime(timezone=True), server_default=func.now())

    # Quan hệ với bảng quên mật khẩu
    ds_token_quen_mat_khau = relationship(
        "QuenMatKhau",
        back_populates="nguoi_dung",
        cascade="all, delete-orphan"
    )


class QuenMatKhau(Base):
    __tablename__ = "quenmatkhau"

    MaReset = Column("mareset", Integer, primary_key=True, index=True)
    MaND = Column("mand", Integer, ForeignKey("nguoidung.mand", ondelete="CASCADE"), nullable=False)
    Token = Column("token", String(255), unique=True, index=True, nullable=False)
    ThoiGianTao = Column("thoigiantao", DateTime(timezone=True), server_default=func.now())
    ThoiGianHetHan = Column("thoigianhethan", DateTime(timezone=True), nullable=False)
    DaSuDung = Column("dasudung", Boolean, default=False)

    nguoi_dung = relationship("NguoiDung", back_populates="ds_token_quen_mat_khau")