import requests
import re
import pandas as pd
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
# Cập nhật tên file import và tên hàm theo bản Việt hóa trước đó
from .text_processing import lam_sach_van_ban, la_binh_luan_rac

def lay_thong_tin_chu_kenh_video(duong_dan):
    try:
        tieu_de_http = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        phan_hoi = requests.get(duong_dan, headers=tieu_de_http)
        if phan_hoi.status_code == 200:
            ma_html = phan_hoi.text
            cac_mau_id = [r'<meta itemprop="channelId" content="(.*?)">', r'"channelId":"(UC[\w-]+)"', r'"externalChannelId":"(UC[\w-]+)"']
            id_chu_kenh = None
            for mau in cac_mau_id:
                khop_id = re.search(mau, ma_html)
                if khop_id:
                    id_chu_kenh = khop_id.group(1)
                    break
            
            mau_ten = r'"ownerChannelName":"(.*?)"'
            khop_ten = re.search(mau_ten, ma_html)
            ten_chu_kenh = khop_ten.group(1) if khop_ten else "Unknown"
            return id_chu_kenh, ten_chu_kenh
    except Exception as e:
        print(f"Lỗi khi lấy thông tin chủ kênh: {e}")
    return None, None

def lay_binh_luan(duong_dan, gioi_han=100):
    cong_cu_tai = YoutubeCommentDownloader()
    danh_sach_binh_luan = []
    
    # Lấy thông tin chủ kênh để lọc
    id_chu_kenh, ten_chu_kenh = lay_thong_tin_chu_kenh_video(duong_dan)

    try:
        if "v=" in duong_dan:
            id_video = duong_dan.split("v=")[1].split("&")[0]
        elif "youtu.be" in duong_dan:
            id_video = duong_dan.split("/")[-1].split("?")[0]
        else:
            return pd.DataFrame()

        trinh_tao = cong_cu_tai.get_comments(id_video, sort_by=SORT_BY_POPULAR)
        dem = 0
        
        for binh_luan in trinh_tao:
            if dem >= gioi_han: break
            
            noi_dung = binh_luan['text']
            ten_tac_gia = binh_luan['author']
            id_tac_gia = binh_luan.get('channel')
            thoi_gian = binh_luan.get('time') or binh_luan.get('publishedAt') 

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