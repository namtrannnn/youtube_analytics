from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Float
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

class Video(Base):
    __tablename__ = "video"

    MaVideo = Column("mavideo", Integer, primary_key=True, index=True)
    YouTubeID = Column("youtubeid", String(50), unique=True, nullable=False)
    LinkVideo = Column("linkvideo", String(500), nullable=False)
    TieuDe = Column("tieude", Text, nullable=True)
    Kenh = Column("kenh", String(255), nullable=True)
    ThoiLuong = Column("thoiluong", Integer, nullable=True)
    NgayDang = Column("ngaydang", DateTime, nullable=True)
    NoiDungGoc = Column("noidunggoc", Text, nullable=True)
    NoiDungTomTat = Column("noidungtomtat", JSONB, nullable=True)
    ThoiGianThem = Column("thoigianthem", DateTime(timezone=True), server_default=func.now())

class CongViecXuLy(Base):
    __tablename__ = "congviec_xuly"

    MaCongViec = Column("macongviec", Integer, primary_key=True, index=True)
    TaskID = Column("taskid", String(255), unique=True, nullable=False) # Celery Task ID
    MaVideo = Column("mavideo", Integer, ForeignKey("video.mavideo", ondelete="CASCADE"))
    MaND = Column("mand", Integer, ForeignKey("nguoidung.mand", ondelete="CASCADE"), nullable=True)
    SoLuongBLYeuCau = Column("soluongblyeucau", Integer, nullable=True)
    TrangThai = Column("trangthai", String(50), default="PENDING")
    KetQuaDashboard = Column("ketquadashboard", JSONB, nullable=True)
    ThoiGianBatDau = Column("thoigianbatdau", DateTime(timezone=True), server_default=func.now())
    ThoiGianKetThuc = Column("thoigianketthuc", DateTime(timezone=True), nullable=True)

class HoiDap(Base):
    __tablename__ = "hoidap"

    MaHoiDap = Column("mahoidap", Integer, primary_key=True, index=True)
    MaVideo = Column("mavideo", Integer, ForeignKey("video.mavideo", ondelete="CASCADE"), nullable=True)
    MaND = Column("mand", Integer, ForeignKey("nguoidung.mand", ondelete="CASCADE"), nullable=True)
    MaCongViec = Column("macongviec", Integer, ForeignKey("congviec_xuly.macongviec", ondelete="CASCADE"), nullable=True)
    CauHoi = Column("cauhoi", Text, nullable=False)
    CauTraLoi = Column("cautraloi", Text, nullable=False)
    NguonDuLieu = Column("nguondulieu", JSONB, nullable=True)
    ThoiGianHoi = Column("thoigianhoi", DateTime(timezone=True), server_default=func.now())

class BinhLuan(Base):
    __tablename__ = "binhluan"

    MaBinhLuan = Column("mabinhluan", Integer, primary_key=True, index=True)
    MaVideo = Column("mavideo", Integer, ForeignKey("video.mavideo", ondelete="CASCADE"))
    BinhLuanID = Column("binhluanid", String(100))
    NoiDung = Column("noidung", Text, nullable=False)
    TacGia = Column("tacgia", String(255))
    ThoiGianDang = Column("thoigiandang", DateTime, nullable=False)
    SoLike = Column("solike", Integer, default=0)
    ThoiGianThuThap = Column("thoigianthuthap", DateTime(timezone=True), server_default=func.now())

class PhanTichCamXuc(Base):
    __tablename__ = "phantich_camxuc"

    MaPhanTich = Column("maphantich", Integer, primary_key=True, index=True)
    MaBinhLuan = Column("mabinhluan", Integer, ForeignKey("binhluan.mabinhluan", ondelete="CASCADE"))
    MaCongViec = Column("macongviec", Integer, ForeignKey("congviec_xuly.macongviec", ondelete="CASCADE"))
    NhanCamXuc = Column("nhancamxuc", String(20))
    DiemCamXuc = Column("diemcamxuc", Float)
    CumChuDe = Column("cumchude", String(50))
    ThoiGianPhanTich = Column("thoigianphantich", DateTime(timezone=True), server_default=func.now())