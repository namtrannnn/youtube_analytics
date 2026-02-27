-- Kích hoạt extension để sinh UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. BẢNG NGƯỜI DÙNG
CREATE TABLE NGUOIDUNG (
    MaND SERIAL PRIMARY KEY,
    TenDangNhap VARCHAR(100) UNIQUE NOT NULL,
    Email VARCHAR(255) UNIQUE,
    MatKhau VARCHAR(255) NOT NULL,
    VaiTro VARCHAR(50) DEFAULT 'user',
    TrangThai VARCHAR(20) DEFAULT 'active',
    ThoiGianTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. BẢNG VIDEO YOUTUBE
CREATE TABLE VIDEO (
    MaVideo SERIAL PRIMARY KEY,
    YouTubeID VARCHAR(50) UNIQUE NOT NULL,
    LinkVideo VARCHAR(500) NOT NULL,
    TieuDe TEXT,
    Kenh VARCHAR(255),
    ThoiLuong INTEGER,
    NgayDang TIMESTAMP,
    ThoiGianThem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BẢNG CÔNG VIỆC XỬ LÝ (TASK HISTORY) - QUAN TRỌNG NHẤT
CREATE TABLE CONGVIEC_XULY (
    MaCongViec SERIAL PRIMARY KEY,
    TaskID UUID UNIQUE NOT NULL,
    MaVideo INTEGER REFERENCES VIDEO(MaVideo) ON DELETE CASCADE,
    MaND INTEGER REFERENCES NGUOIDUNG(MaND) ON DELETE CASCADE,
    SoLuongBLYeuCau INTEGER,
    TrangThai VARCHAR(50), -- VD: PENDING, PROCESSING, SUCCESS, FAILED
    
    -- LƯU TOÀN BỘ DỮ LIỆU BIỂU ĐỒ VÀ TÓM TẮT VÀO ĐÂY (Tốc độ query bàn thờ)
    -- Bao gồm: sentiment_chart, emoji_stats, word_cloud, time_series, top_users, scatter_clusters, video_summary
    KetQuaDashboard JSONB, 
    
    ThoiGianBatDau TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ThoiGianKetThuc TIMESTAMP
);

-- 4. BẢNG BÌNH LUẬN THÔ (Phục vụ cho Chatbot RAG đọc lại)
CREATE TABLE BINHLUAN (
    MaBinhLuan SERIAL PRIMARY KEY,
    MaVideo INTEGER REFERENCES VIDEO(MaVideo) ON DELETE CASCADE,
    BinhLuanID VARCHAR(100), -- ID gốc từ YouTube
    NoiDung TEXT NOT NULL,
    TacGia VARCHAR(255),
    ThoiGianDang TIMESTAMP NOT NULL,
    SoLike INTEGER DEFAULT 0,
    ThoiGianThuThap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT UQ_Video_BinhLuan UNIQUE (MaVideo, BinhLuanID)
);

-- 5. BẢNG PHÂN TÍCH CẢM XÚC (Chi tiết từng comment)
CREATE TABLE PHANTICH_CAMXUC (
    MaPhanTich SERIAL PRIMARY KEY,
    MaBinhLuan INTEGER UNIQUE REFERENCES BINHLUAN(MaBinhLuan) ON DELETE CASCADE,
    MaCongViec INTEGER REFERENCES CONGVIEC_XULY(MaCongViec) ON DELETE CASCADE,
    NhanCamXuc VARCHAR(20), -- Positive, Negative, Neutral
    DiemCamXuc FLOAT, -- Nếu model của bạn có xuất ra xác suất (Probability)
    CumChuDe VARCHAR(50), -- Nhóm 0, Nhóm 1, Nhóm 2 (Dành cho Scatter plot)
    ThoiGianPhanTich TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. BẢNG LỊCH SỬ HỎI ĐÁP (CHATBOT)
CREATE TABLE HOIDAP (
    MaHoiDap SERIAL PRIMARY KEY,
    MaVideo INTEGER REFERENCES VIDEO(MaVideo) ON DELETE CASCADE,
    MaND INTEGER REFERENCES NGUOIDUNG(MaND) ON DELETE CASCADE,
    MaCongViec INTEGER REFERENCES CONGVIEC_XULY(MaCongViec) ON DELETE SET NULL,
    CauHoi TEXT NOT NULL,
    CauTraLoi TEXT NOT NULL,
    NguonDuLieu JSONB, -- Lưu mảng [MaBinhLuan1, MaBinhLuan2] AI đã dùng để trả lời
    ThoiGianHoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Đánh Index để tối ưu truy vấn
CREATE INDEX idx_binhluan_video ON BINHLUAN(MaVideo);
CREATE INDEX idx_congviec_nd ON CONGVIEC_XULY(MaND);
CREATE INDEX idx_phantich_nhan ON PHANTICH_CAMXUC(NhanCamXuc);