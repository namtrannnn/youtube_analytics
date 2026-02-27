import google.generativeai as genai
import os
import pandas as pd
from itertools import islice
from youtube_comment_downloader import *

# Cấu hình Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def cao_binh_luan(duong_dan, so_luong=100):
    cong_cu_tai = YoutubeCommentDownloader()
    danh_sach_binh_luan = []
    # Logic lấy comment (giả lập hoặc dùng thư viện)
    trinh_tao = cong_cu_tai.get_comments_from_url(duong_dan, sort_by=SORT_BY_POPULAR)
    for binh_luan in islice(trinh_tao, so_luong):
        danh_sach_binh_luan.append({
            "noi_dung": binh_luan['text'],
            "tac_gia": binh_luan['author'],
            "thoi_gian": binh_luan['time'], # Cần xử lý chuẩn hóa time để vẽ biểu đồ
            "so_luot_thich": binh_luan.get('votes', 0)
        })
    return danh_sach_binh_luan

def phan_tich_bang_gemini(du_lieu_binh_luan):
    mo_hinh = genai.GenerativeModel('gemini-1.5-flash') # Dùng bản Flash cho nhanh và rẻ
    
    # Gom text lại để phân tích (lưu ý giới hạn token, nếu quá nhiều phải chia batch)
    toan_bo_van_ban = "\n".join([binh_luan['noi_dung'] for binh_luan in du_lieu_binh_luan])
    
    cau_lenh = f"""
    Phân tích danh sách bình luận YouTube dưới đây. Trả về JSON với định dạng:
    {{
        "sentiment_summary": {{"positive": 0, "neutral": 0, "negative": 0}},
        "top_emojis": ["emoji1", "emoji2"],
        "video_summary": "Tóm tắt nội dung dựa trên bình luận",
        "key_themes": ["chủ đề 1", "chủ đề 2"]
    }}
    
    Bình luận:
    {toan_bo_van_ban[:30000]} 
    """
    # Lưu ý: Cắt chuỗi để tránh lỗi token nếu quá dài
    
    phan_hoi = mo_hinh.generate_content(cau_lenh)
    return phan_hoi.text # Cần xử lý chuỗi trả về thành JSON object