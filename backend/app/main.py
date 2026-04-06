from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult
from typing import Optional
import os
from app.routers import auth_router
from app.routers import chat_router
from worker.celery_app import celery_app 
from app.database import get_db
from app.models import Video, CongViecXuLy, BinhLuan, PhanTichCamXuc, HoiDap
from app.auth import get_optional_current_user
from sqlalchemy.orm import Session
from datetime import datetime
import re
from app.ml_models.youtube_utils import lay_thong_tin_video

app = FastAPI()

# --- CẤU HÌNH CORS ---
cac_nguon_cho_phep = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chat_router.router, prefix="/api", tags=["Chatbot"])

class YeuCauPhanTich(BaseModel):
    duong_dan: str
    so_luong: int = 100

class YeuCauTroChuyen(BaseModel):
    ma_tac_vu: str
    cau_hoi: str

def trích_xuat_youtube_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else "unknown"

@app.get("/")
def doc_trang_chu():
    return {"thong_bao": "Chào mừng đến với API Phân tích YouTube"}

@app.post("/api/analyze")
async def bat_dau_phan_tich(
    yeu_cau: YeuCauPhanTich, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    try:
        # 1. Gửi tác vụ cho Celery chạy ngầm (Khách hay User đều được chạy)
        tac_vu = celery_app.send_task(
            "worker.tasks.analyze_video_task", 
            args=[yeu_cau.duong_dan, yeu_cau.so_luong]
        )
        
        # 2. Chỉ lưu db khi có đăng nhập
        if current_user:
            # Trích xuất ID video
            yt_id = trích_xuat_youtube_id(yeu_cau.duong_dan)
            
            # Tìm hoặc tạo mới Video
            video = db.query(Video).filter(Video.YouTubeID == yt_id).first()
            if not video:
                thong_tin = lay_thong_tin_video(yeu_cau.duong_dan)
                
                video = Video(
                    YouTubeID=yt_id, 
                    LinkVideo=yeu_cau.duong_dan,
                    TieuDe=thong_tin.get("tieu_de"),
                    Kenh=thong_tin.get("ten_chu_kenh"),
                    ThoiLuong=thong_tin.get("thoi_luong"),
                    NgayDang=thong_tin.get("ngay_dang")
                )
                db.add(video)
                db.commit()
                db.refresh(video)

            # Lưu Công Việc Xử Lý
            cong_viec_moi = CongViecXuLy(
                TaskID=tac_vu.id,
                MaVideo=video.MaVideo,
                SoLuongBLYeuCau=yeu_cau.so_luong,
                TrangThai='PENDING',
                MaND=current_user.MaND  # Gán ID người dùng
            )
            db.add(cong_viec_moi)
            db.commit()

        # Trả về ID tác vụ ngay lập tức
        return {"ma_tac_vu": tac_vu.id}
    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{ma_tac_vu}")
async def lay_trang_thai(ma_tac_vu: str, db: Session = Depends(get_db)):
    ket_qua_tac_vu = AsyncResult(ma_tac_vu, app=celery_app)
    
    if ket_qua_tac_vu.state == 'SUCCESS':
        cong_viec = db.query(CongViecXuLy).filter(CongViecXuLy.TaskID == ma_tac_vu).first()
        
        if cong_viec and cong_viec.TrangThai != 'SUCCESS':
            ket_qua_data = ket_qua_tac_vu.result
            
            try:
                # 1. CẬP NHẬT THÔNG TIN CÔNG VIỆC (Chưa commit)
                cong_viec.TrangThai = 'SUCCESS'
                cong_viec.KetQuaDashboard = ket_qua_data
                cong_viec.ThoiGianKetThuc = datetime.now()

                # 2. CẬP NHẬT TÓM TẮT VIDEO (Chưa commit)
                video = db.query(Video).filter(Video.MaVideo == cong_viec.MaVideo).first()
                if video and not video.NoiDungTomTat:
                    video.NoiDungTomTat = ket_qua_data.get('video_summary', {})
                    video.NoiDungGoc = ket_qua_data.get('original_transcript', '')

                # 3. LƯU BÌNH LUẬN & PHÂN TÍCH
                danh_sach_bl = ket_qua_data.get('all_comments', [])

                for bl_data in danh_sach_bl:
                    binh_luan_id_hien_tai = str(bl_data.get('id', '')) 
                    
                    # Tìm bình luận đã có trong DB chưa
                    binh_luan = db.query(BinhLuan).filter(
                        BinhLuan.BinhLuanID == binh_luan_id_hien_tai,
                        BinhLuan.MaVideo == cong_viec.MaVideo
                    ).first()

                    if not binh_luan:
                        binh_luan = BinhLuan(
                            MaVideo=cong_viec.MaVideo,
                            BinhLuanID=binh_luan_id_hien_tai,
                            NoiDung=bl_data.get('ban_goc', ''),
                            TacGia=bl_data.get('tac_gia', 'Ẩn danh'),
                            ThoiGianDang=datetime.now(), 
                            SoLike=bl_data.get('so_like', 0)
                        )
                        db.add(binh_luan)
                        # Dùng flush() thay cho commit(). Giúp sinh ra MaBinhLuan ngay lập tức mà không đóng transaction, tăng tốc độ xử lý vòng lặp lên gấp 10 lần.
                        db.flush() 

                    # Chống trùng lặp (Duplicate Entry) cho bảng Phân tích cảm xúc
                    phan_tich_ton_tai = db.query(PhanTichCamXuc).filter(
                        PhanTichCamXuc.MaBinhLuan == binh_luan.MaBinhLuan,
                        PhanTichCamXuc.MaCongViec == cong_viec.MaCongViec
                    ).first()

                    if not phan_tich_ton_tai:
                        phan_tich = PhanTichCamXuc(
                            MaBinhLuan=binh_luan.MaBinhLuan,
                            MaCongViec=cong_viec.MaCongViec,
                            NhanCamXuc=bl_data.get('cam_xuc_du_doan', 'Trung tính'),
                            DiemCamXuc=float(bl_data.get('diem_cam_xuc', 0.0)), 
                            CumChuDe=f"Cụm {bl_data.get('cum', 0)}"
                        )
                        db.add(phan_tich)

                # 4. THỰC HIỆN COMMIT TOÀN BỘ CÙNG MỘT LÚC (Atomic Transaction)
                db.commit()

            except Exception as e:
                # Nếu có bất kỳ lỗi gì xảy ra trong vòng lặp, rollback toàn bộ để database không bị rác
                db.rollback()
                print(f"Lỗi khi lưu DB: {str(e)}")
                raise HTTPException(status_code=500, detail="Đã xảy ra lỗi khi lưu kết quả vào CSDL.")

        return {
            "trang_thai": "SUCCESS", 
            "tien_do": 100, 
            "tin_nhan": "Hoàn thành",
            "ket_qua": ket_qua_tac_vu.result
        }
    
    # Các trạng thái khác (PENDING, PROGRESS, FAILURE)
    if ket_qua_tac_vu.state == 'PENDING':
        return {"trang_thai": "PENDING", "tien_do": 0, "tin_nhan": "Đang chờ xử lý..."}
    elif ket_qua_tac_vu.state == 'PROGRESS':
        return {"trang_thai": "PROGRESS", "tien_do": ket_qua_tac_vu.info.get('progress', 0), "tin_nhan": ket_qua_tac_vu.info.get('status', '')}
    elif ket_qua_tac_vu.state == 'FAILURE':
        return {"trang_thai": "FAILURE", "loi": str(ket_qua_tac_vu.info)}
    else:
        return {"trang_thai": ket_qua_tac_vu.state}
    
@app.get("/api/history")
async def lay_danh_sach_lich_su(
    current_user = Depends(get_optional_current_user), 
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để xem lịch sử.")
    
    # Lấy danh sách task kèm thông tin video từ DB (Sắp xếp mới nhất lên đầu)
    danh_sach = db.query(CongViecXuLy, Video).join(Video, CongViecXuLy.MaVideo == Video.MaVideo)\
                  .filter(CongViecXuLy.MaND == current_user.MaND, CongViecXuLy.TrangThai == 'SUCCESS')\
                  .order_by(CongViecXuLy.ThoiGianKetThuc.desc()).all()
    
    ket_qua = []
    for cv, vd in danh_sach:
        ket_qua.append({
            "taskId": cv.TaskID,
            "linkVideo": vd.LinkVideo,
            "title": vd.TieuDe or "Video không xác định",
            "soLuongBinhLuan": cv.SoLuongBLYeuCau,
            "ngayTao": cv.ThoiGianKetThuc.isoformat() + "Z" if cv.ThoiGianKetThuc else cv.ThoiGianBatDau.isoformat() + "Z",
            "status": cv.TrangThai
        })
    return ket_qua

@app.get("/api/history/{task_id}")
async def lay_chi_tiet_lich_su(
    task_id: str, 
    current_user = Depends(get_optional_current_user), 
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập.")
    
    # 1. Lấy Công việc
    cong_viec = db.query(CongViecXuLy).filter(
        CongViecXuLy.TaskID == task_id, 
        CongViecXuLy.MaND == current_user.MaND
    ).first()
    
    if not cong_viec or not cong_viec.KetQuaDashboard:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu phân tích.")
    
    # 2. Lấy Lịch sử Chatbot liên quan đến Công việc này
    lich_su_chat_db = db.query(HoiDap).filter(HoiDap.MaCongViec == cong_viec.MaCongViec)\
                        .order_by(HoiDap.ThoiGianHoi.asc()).all()
    
    # Định dạng lại chat cho Frontend dễ đọc (1 câu hỏi user đi kèm 1 câu trả lời bot)
    chat_history_formatted = []
    for chat in lich_su_chat_db:
        chat_history_formatted.append({"role": "user", "content": chat.CauHoi})
        chat_history_formatted.append({"role": "bot", "content": chat.CauTraLoi})
        
    # 3. Trả về cả 2 phần
    return {
        "dashboard_data": cong_viec.KetQuaDashboard,
        "chat_history": chat_history_formatted
    }

@app.delete("/api/history/{task_id}")
async def xoa_lich_su(
    task_id: str, 
    current_user = Depends(get_optional_current_user), 
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập.")
    
    # 1. Tìm công việc cần xóa
    cong_viec = db.query(CongViecXuLy).filter(
        CongViecXuLy.TaskID == task_id, 
        CongViecXuLy.MaND == current_user.MaND
    ).first()
    
    if not cong_viec:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử này hoặc bạn không có quyền xóa.")
    
    try:
        ma_cong_viec = cong_viec.MaCongViec
        ma_video = cong_viec.MaVideo

        # BƯỚC 1: XÓA DỮ LIỆU NHÁNH (CON)         
        # Xóa Phân tích Cảm xúc của công việc này
        db.query(PhanTichCamXuc).filter(PhanTichCamXuc.MaCongViec == ma_cong_viec).delete()

        # BƯỚC 2: KIỂM TRA VÀ XÓA VIDEO & BÌNH LUẬN
        # Kiểm tra xem có người dùng/công việc nào KHÁC đang xài chung Video này không
        cong_viec_khac_dung_video = db.query(CongViecXuLy).filter(
            CongViecXuLy.MaVideo == ma_video,
            CongViecXuLy.MaCongViec != ma_cong_viec
        ).first()

        # 1. Xóa Công Việc hiện tại
        db.delete(cong_viec)

        # 2. Nếu KHÔNG CÒN AI dùng Video này nữa -> Xóa luôn Video và Bình luận cho sạch Database
        if not cong_viec_khac_dung_video:
            # Xóa toàn bộ bình luận thô
            db.query(BinhLuan).filter(BinhLuan.MaVideo == ma_video).delete()
            
            # Xóa Video
            video_can_xoa = db.query(Video).filter(Video.MaVideo == ma_video).first()
            if video_can_xoa:
                db.delete(video_can_xoa)

        # Lưu mọi thay đổi xuống Database
        db.commit()
        return {"thong_bao": "Đã xóa lịch sử phân tích thành công."}
        
    except Exception as e:
        db.rollback() # Hoàn tác nếu có lỗi (đảm bảo an toàn dữ liệu)
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa: {str(e)}")