import requests
import re
import json
import pandas as pd
from datetime import datetime
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
from .text_processing import lam_sach_van_ban, la_binh_luan_rac

def lay_thong_tin_video(duong_dan):
    """Lấy toàn bộ thông tin cơ bản của video bằng YouTube InnerTube API"""
    thong_tin = {
        "id_chu_kenh": None,
        "ten_chu_kenh": "Unknown",
        "tieu_de": None,
        "thoi_luong": None,
        "ngay_dang": None
    }

    # 1. Trích xuất ID từ URL
    match = re.search(r'(?:v=|/|youtu\.be/)([0-9A-Za-z_-]{11})', duong_dan)
    if not match:
        print("Không tìm thấy Video ID hợp lệ.")
        return thong_tin
    
    video_id = match.group(1)

    # 2. Gọi InnerTube API
    url = "https://www.youtube.com/youtubei/v1/player"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    payload = {
        "videoId": video_id,
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20210721.00.00"
            }
        }
    }

    try:
        # Dùng tham số json=payload
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            # --- LẤY THÔNG TIN CƠ BẢN TỪ videoDetails ---
            video_details = data.get("videoDetails", {})
            thong_tin["tieu_de"] = video_details.get("title")
            thong_tin["ten_chu_kenh"] = video_details.get("author")
            thong_tin["id_chu_kenh"] = video_details.get("channelId")
            
            if "lengthSeconds" in video_details:
                thong_tin["thoi_luong"] = int(video_details["lengthSeconds"])
            # --- LẤY NGÀY ĐĂNG TỪ microformat ---
            micro = data.get("microformat", {}).get("playerMicroformatRenderer", {})
            publish_date = micro.get("publishDate") or micro.get("uploadDate")
        
            if publish_date:
                # Python 3.7+ có hàm fromisoformat tự động xử lý chuỗi "2026-02-06T04:00:40-08:00"
                # Cắt bỏ múi giờ (phần sau dấu + hoặc - cuối cùng) để lưu vào database cho đồng nhất
                thong_tin["ngay_dang"] = datetime.fromisoformat(publish_date).replace(tzinfo=None)
                
    except Exception as e:
        print(f"Lỗi khi gọi InnerTube API: {e}")

    return thong_tin

def lay_binh_luan(duong_dan, gioi_han=100):
    cong_cu_tai = YoutubeCommentDownloader()
    danh_sach_binh_luan = []
    
    # Lấy thông tin chủ kênh để lọc
    thong_tin_video = lay_thong_tin_video(duong_dan)
    id_chu_kenh = thong_tin_video["id_chu_kenh"]
    ten_chu_kenh = thong_tin_video["ten_chu_kenh"]

    try:
        if "v=" in duong_dan:
            id_video = duong_dan.split("v=")[1].split("&")[0]
        elif "youtu.be" in duong_dan:
            id_video = duong_dan.split("/")[-1].split("?")[0]
        else:
            return pd.DataFrame()

        trinh_tao = cong_cu_tai.get_comments(id_video, sort_by=SORT_BY_RECENT)
        dem = 0
        
        for binh_luan in trinh_tao:
            if dem >= gioi_han: break
            
            noi_dung = binh_luan['text']
            ten_tac_gia = binh_luan['author']
            id_tac_gia = binh_luan.get('channel')
            thoi_gian = binh_luan.get('time') or binh_luan.get('publishedAt')
            id_binh_luan = binh_luan.get('cid', '') 
            so_luot_thich = binh_luan.get('votes', 0)

            # --- 1. LỌC SPAM/RÁC ---
            # Kiểm tra ngay trên text gốc, nếu là spam thì bỏ qua luôn
            if la_binh_luan_rac(noi_dung): 
                continue 

            # --- 2. LỌC CHỦ KÊNH ---
            la_chu_kenh = False
            if id_chu_kenh and id_tac_gia == id_chu_kenh: la_chu_kenh = True
            if not la_chu_kenh and ten_chu_kenh and ten_tac_gia.strip().lower() == ten_chu_kenh.strip().lower(): la_chu_kenh = True
            
            if la_chu_kenh: continue

            # --- 3. LÀM SẠCH VÀ LƯU ---
            # Lưu ý: xoa_tu_loai_bo=True để tốt cho WordCloud
            da_lam_sach = lam_sach_van_ban(noi_dung, xoa_tu_loai_bo=True) 
            
            if da_lam_sach and len(da_lam_sach) > 1:
                # Các cột (keys) cho DataFrame cũng đã được Việt hóa
                danh_sach_binh_luan.append({
                    'id': id_binh_luan, 
                    'so_like': so_luot_thich,
                    'tac_gia': ten_tac_gia,
                    'ban_goc': noi_dung, 
                    'da_lam_sach': da_lam_sach,
                    'thoi_gian_dang': thoi_gian
                })
                dem += 1
        
        return pd.DataFrame(danh_sach_binh_luan)
        
    except Exception as e:
        print(f"Lỗi khi cào bình luận: {e}")
        return pd.DataFrame()