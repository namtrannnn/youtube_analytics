from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ai_service import get_chatbot_response 
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CongViecXuLy, HoiDap
from app.auth import get_optional_current_user

# Import celery_app để lấy kết quả phân tích dựa trên ma_tac_vu
from worker.celery_app import celery_app 

router = APIRouter()

# Schema khớp với dữ liệu từ Frontend gửi lên
class ChatRequest(BaseModel):
    ma_tac_vu: str
    cau_hoi: str

@router.post("/chat")
async def chat_with_gemini(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)
):
    if not request.cau_hoi.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")
    
    # 1. TRÍCH XUẤT DỮ LIỆU ĐÃ PHÂN TÍCH
    # Lấy kết quả task từ Celery/Redis thông qua ma_tac_vu
    ket_qua_tac_vu = AsyncResult(request.ma_tac_vu, app=celery_app)
    
    # Kiểm tra xem task đã phân tích xong chưa
    if ket_qua_tac_vu.state != 'SUCCESS':
        raise HTTPException(
            status_code=400, 
            detail="Dữ liệu phân tích chưa sẵn sàng hoặc video chưa được phân tích xong."
        )
    
    # Lấy data dictionary mà worker đã trả về sau khi cào và phân tích
    du_lieu = ket_qua_tac_vu.result 
    
    # 2. GỌI AI XỬ LÝ
    # Truyền cả câu hỏi và dữ liệu phân tích vào AI
    bot_reply = get_chatbot_response(request.cau_hoi, du_lieu)

    # 3. Lưu lịch sử vào bảng HOIDAP nếu User đã đăng nhập
    if current_user:
        cong_viec = db.query(CongViecXuLy).filter(CongViecXuLy.TaskID == request.ma_tac_vu).first()
        
        chat_moi = HoiDap(
            MaND=current_user.MaND,
            MaCongViec=cong_viec.MaCongViec if cong_viec else None,
            MaVideo=cong_viec.MaVideo if cong_viec else None,
            CauHoi=request.cau_hoi,
            CauTraLoi=bot_reply
        )
        db.add(chat_moi)
        db.commit()
    
    # 4. TRẢ VỀ FRONTEND
    # Trả về key 'answer' vì frontend đang hứng res.data.answer
    return {"answer": bot_reply}