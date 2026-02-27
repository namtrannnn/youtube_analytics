from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult
from typing import Optional
import os

# --- THAY ĐỔI Ở ĐÂY: Import celery_app thay vì import tasks ---
# Điều này giúp Backend không phải load model AI nặng nề
from worker.celery_app import celery_app 

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

class YeuCauPhanTich(BaseModel):
    duong_dan: str
    so_luong: int = 100

class YeuCauTroChuyen(BaseModel):
    ma_tac_vu: str
    cau_hoi: str

@app.get("/")
def doc_trang_chu():
    return {"thong_bao": "Chào mừng đến với API Phân tích YouTube"}

@app.post("/api/analyze")
async def bat_dau_phan_tich(yeu_cau: YeuCauPhanTich):
    try:
        # --- THAY ĐỔI Ở ĐÂY: Dùng send_task ---
        # Gửi tên task dưới dạng chuỗi (String), Backend không cần biết nội dung task là gì
        tac_vu = celery_app.send_task(
            "worker.tasks.analyze_video_task", 
            args=[yeu_cau.duong_dan, yeu_cau.so_luong]
        )
        return {"ma_tac_vu": tac_vu.id}
    except Exception as e:
        # In lỗi ra log để dễ debug
        print(f"Lỗi khi gửi tác vụ: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{ma_tac_vu}")
async def lay_trang_thai(ma_tac_vu: str):
    ket_qua_tac_vu = AsyncResult(ma_tac_vu, app=celery_app) # Truyền app vào để check đúng
    
    if ket_qua_tac_vu.state == 'PENDING':
        return {"trang_thai": "PENDING", "tien_do": 0, "tin_nhan": "Đang chờ xử lý..."}
    elif ket_qua_tac_vu.state == 'PROGRESS':
        return {
            "trang_thai": "PROGRESS", 
            "tien_do": ket_qua_tac_vu.info.get('progress', 0),
            "tin_nhan": ket_qua_tac_vu.info.get('status', '')
        }
    elif ket_qua_tac_vu.state == 'SUCCESS':
        return {
            "trang_thai": "SUCCESS", 
            "tien_do": 100, 
            "tin_nhan": "Hoàn thành",
            "ket_qua": ket_qua_tac_vu.result
        }
    elif ket_qua_tac_vu.state == 'FAILURE':
        return {"trang_thai": "FAILURE", "loi": str(ket_qua_tac_vu.info)}
    else:
        return {"trang_thai": ket_qua_tac_vu.state}