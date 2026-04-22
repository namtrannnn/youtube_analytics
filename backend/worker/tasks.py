import numpy as np
import pandas as pd
import torch
import emoji
from collections import Counter
from celery import shared_task
from transformers import AutoTokenizer, AutoModel
from datetime import datetime, timedelta
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import re

from app.ml_models.custom_algorithms import KMeansTuyChinh, HoiQuyLogisticTuyChinh
# [CẬP NHẬT]: Import thêm lay_cam_xuc_soft, an_danh_ten_rieng_cho_bert_an_toan và hieu_chinh_cam_xuc_theo_luat
from app.ml_models.text_processing import (
    TU_LOAI_BO_TIENG_VIET, 
    lay_cam_xuc_soft, 
    an_danh_ten_rieng_cho_bert_an_toan, 
    hieu_chinh_cam_xuc_theo_luat
)
from app.ml_models.youtube_utils import lay_binh_luan
from app.video_summarizer.main_summarizer import SmartVideoSummarizer

bo_tach_tu = None
mo_hinh = None

def tai_mo_hinh():
    global bo_tach_tu, mo_hinh
    if bo_tach_tu is not None and mo_hinh is not None:
        return
    try:
        print("Đang tìm Mô hình trong cache...")
        bo_tach_tu = AutoTokenizer.from_pretrained('bert-base-multilingual-cased', local_files_only=True)
        mo_hinh = AutoModel.from_pretrained('bert-base-multilingual-cased', local_files_only=True)
        print("Đã tải Mô hình từ ổ cứng (Offline)!")
    except Exception:
        print("Không tìm thấy cache, đang tải...")
        bo_tach_tu = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        mo_hinh = AutoModel.from_pretrained('bert-base-multilingual-cased')
        print("Đã tải và lưu Mô hình xong!")

def lay_vector_bert(danh_sach_van_ban):
    tai_mo_hinh()
    cac_vector = []

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mo_hinh.to(device)
    mo_hinh.eval()

    with torch.no_grad():
        kich_thuoc_lo = 32
        for i in range(0, len(danh_sach_van_ban), kich_thuoc_lo):
            lo_van_ban = danh_sach_van_ban[i:i+kich_thuoc_lo]
            dau_vao = bo_tach_tu(lo_van_ban, return_tensors="pt", padding=True, truncation=True, max_length=128)
            dau_vao = {k: v.to(device) for k, v in dau_vao.items()}
            dau_ra = mo_hinh(**dau_vao)
            
            # [CẬP NHẬT BƯỚC 3]: Áp dụng Mean Pooling thay vì chỉ lấy CLS token
            token_embeddings = dau_ra.last_hidden_state 
            attention_mask = dau_vao['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
            
            sum_embeddings = torch.sum(token_embeddings * attention_mask, 1)
            sum_mask = torch.clamp(attention_mask.sum(1), min=1e-9)
            mean_pooled = sum_embeddings / sum_mask
            
            vector_batch = mean_pooled.cpu().numpy()
            cac_vector.extend(vector_batch)
            
    return np.array(cac_vector)

def tao_du_lieu_dam_may_tu(danh_sach_van_ban):
    toan_bo_van_ban = " ".join(danh_sach_van_ban)
    cac_tu = toan_bo_van_ban.split()
    
    cac_tu_sach = []
    for tu in cac_tu:
        if (tu not in TU_LOAI_BO_TIENG_VIET) and (not tu.isdigit()) and (len(tu) > 1):
            cac_tu_sach.append(tu)
            
    bo_dem = Counter(cac_tu_sach)
    return [{"text": k, "value": v} for k, v in bo_dem.most_common(50)]

def phan_tich_nguoi_dung_hang_dau(df_binh_luan):
    if 'tac_gia' not in df_binh_luan.columns:
        return []
        
    so_luong_nguoi_dung = df_binh_luan['tac_gia'].value_counts().head(5).reset_index()
    so_luong_nguoi_dung.columns = ['ten', 'so_luong']
    
    nguoi_dung_hang_dau = []
    for _, hang in so_luong_nguoi_dung.iterrows():
        ten_nguoi_dung = hang['ten']
        cam_xuc_nguoi_dung = df_binh_luan[df_binh_luan['tac_gia'] == ten_nguoi_dung]['cam_xuc_du_doan'].iloc[0]
        nguoi_dung_hang_dau.append({
            "name": ten_nguoi_dung, 
            "count": int(hang['so_luong']),
            "sentiment": cam_xuc_nguoi_dung
        })
        
    return nguoi_dung_hang_dau

def tao_du_lieu_bieu_do_phan_tan(df, toa_do_2d):
    if len(df) < 2:
        return []

    bo_chuan_hoa = MinMaxScaler(feature_range=(0, 100))
    toa_do_da_chuan_hoa = bo_chuan_hoa.fit_transform(toa_do_2d)

    du_lieu_phan_tan = []
    for i, hang in df.iterrows():
        x = toa_do_da_chuan_hoa[i][0]
        y = toa_do_da_chuan_hoa[i][1]
        
        du_lieu_phan_tan.append({
            "x": round(float(x), 2),
            "y": round(float(y), 2),
            "z": 100,
            "cluster": f"Nhóm {hang['cum']}",
            "author": hang['tac_gia'],
            "content": hang['ban_goc'][:50] + "..."
        })
    
    return du_lieu_phan_tan

def phan_tich_ngay_tuong_doi(chuoi_ngay):
    hien_tai = datetime.now()
    if not isinstance(chuoi_ngay, str): 
        return hien_tai
    
    chuoi_ngay = chuoi_ngay.lower().strip()
    if '(' in chuoi_ngay: chuoi_ngay = chuoi_ngay.split('(')[0].strip()
    
    try:
        tim_gia_tri = re.search(r'\d+', chuoi_ngay)
        gia_tri = int(tim_gia_tri.group()) if tim_gia_tri else 1
        
        if any(x in chuoi_ngay for x in ['second ago', 'giây trước']): 
            khoang_thoi_gian = timedelta(seconds=gia_tri)
        elif any(x in chuoi_ngay for x in ['minute ago', 'phút trước']): 
            khoang_thoi_gian = timedelta(minutes=gia_tri)
        elif any(x in chuoi_ngay for x in ['hour ago', 'giờ trước']): 
            khoang_thoi_gian = timedelta(hours=gia_tri)
        elif any(x in chuoi_ngay for x in ['day ago', 'ngày trước']): 
            khoang_thoi_gian = timedelta(days=gia_tri)
        elif any(x in chuoi_ngay for x in ['week ago', 'tuần trước']): 
            khoang_thoi_gian = timedelta(weeks=gia_tri)
        elif any(x in chuoi_ngay for x in ['month ago', 'tháng trước']): 
            khoang_thoi_gian = timedelta(days=gia_tri * 30)
        elif any(x in chuoi_ngay for x in ['year ago', 'năm trước']): 
            khoang_thoi_gian = timedelta(days=gia_tri * 365)
        else:
            khoang_thoi_gian = timedelta(seconds=0)
            
        return hien_tai - khoang_thoi_gian

    except Exception:
        return hien_tai

def phan_tich_chuoi_thoi_gian(df):
    ten_cot = 'thoi_gian_dang' if 'thoi_gian_dang' in df.columns else 'time'
    if ten_cot not in df.columns: return []
    
    try:
        df['thoi_gian_thuc'] = pd.to_datetime(df[ten_cot].apply(phan_tich_ngay_tuong_doi), errors='coerce')
        df = df.dropna(subset=['thoi_gian_thuc'])
        if df.empty: return []

        thoi_gian_nho_nhat = df['thoi_gian_thuc'].min()
        thoi_gian_lon_nhat = df['thoi_gian_thuc'].max()
        chenh_lech_thoi_gian = thoi_gian_lon_nhat - thoi_gian_nho_nhat

        if chenh_lech_thoi_gian.days < 1: 
            df['khoa_nhom'] = df['thoi_gian_thuc'].dt.floor('H')
        else:
            df['khoa_nhom'] = df['thoi_gian_thuc'].dt.floor('D')

        truc_thoi_gian = df.groupby('khoa_nhom').size().reset_index(name='so_luong_binh_luan')
        truc_thoi_gian = truc_thoi_gian.sort_values('khoa_nhom')

        truc_thoi_gian['date'] = truc_thoi_gian['khoa_nhom'].dt.strftime('%Y-%m-%d %H:%M')
        truc_thoi_gian.rename(columns={'so_luong_binh_luan': 'comments'}, inplace=True)
        return truc_thoi_gian[['date', 'comments']].to_dict(orient='records')

    except Exception as e:
        print(f"Lỗi Chuỗi Thời Gian: {e}")
        return []

# ĐÃ XÓA hàm an_danh_ten_rieng_cho_bert_an_toan() và hieu_chinh_cam_xuc_theo_luat() ở đây 
# vì đã được import từ text_processing.py để tránh trùng lặp code.

# ===================================================================================
# CELERY TASK CHÍNH
# ===================================================================================
@shared_task(bind=True)
def analyze_video_task(self, url_youtube, so_luong_binh_luan):
    tai_mo_hinh()
    
    def report_progress(percent, message):
        self.update_state(state='PROGRESS', meta={'progress': percent, 'status': message})

    # TRÍCH XUẤT VÀ TÓM TẮT NỘI DUNG VIDEO
    self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Đang tải phụ đề và tóm tắt nội dung video...'})
    
    try:
        summarizer = SmartVideoSummarizer()
        video_summary_data = summarizer.process_video(url_youtube, progress_callback=report_progress)
    except Exception as e:
        print(f"Lỗi Tóm Tắt Video: {e}")
        video_summary_data = {
            "type": "TEXT",
            "category": "ERROR",
            "content": "Có lỗi xảy ra trong quá trình trích xuất tóm tắt video."
        }
    
    # CRAWL BÌNH LUẬN YOUTUBE
    self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Đang quét thông tin kênh và bình luận...'})
    
    df = lay_binh_luan(url_youtube, gioi_han=so_luong_binh_luan)
    if df.empty:
         return {
            "video_url": url_youtube,
            "total_comments": 0,
            "video_summary": video_summary_data,
            "time_series": [],
            "sentiment_chart": [],
            "emoji_stats": [],
            "word_cloud": [],
             "all_comments": [],
            "top_users": [],
             "scatter_clusters": [],
            "warning": "Không tìm thấy bình luận nào, nhưng tóm tắt video đã được tạo thành công." 
        }
    
    self.update_state(state='PROGRESS', meta={'progress': 50, 'status': f'Đã tải {len(df)} bình luận. Đang phân tích...'})

   
    # VECTOR HÓA VÀ ML CUSTOM
    try:
        # Lấy nhúng Vector với hàm ẩn danh tên riêng
        danh_sach_cho_bert = [an_danh_ten_rieng_cho_bert_an_toan(txt) for txt in df['ban_goc'].tolist()]
        X_goc = lay_vector_bert(danh_sach_cho_bert)
        
        # Giảm chiều PCA cho Biểu đồ Scatter 2D
        pca = PCA(n_components=2)
        X_pca_2d = pca.fit_transform(X_goc)
    except Exception as e:
        return {"error": f"Lỗi xử lý ngôn ngữ tự nhiên: {str(e)}"}
    
    self.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'Đang chạy thuật toán phân cụm & đánh giá cảm xúc...'})

    # Chạy K-Means
    kmeans = KMeansTuyChinh(so_cum=3, so_vong_lap_toi_da=100)
    df['cum'] = kmeans.huan_luyen_va_du_doan(X_pca_2d).tolist()

    # Áp dụng Soft Labels thay vì Weak Supervision nhãn cứng
    y_soft_list = []
    nhan_rule_based_list = []
    cac_lop = np.array(['Negative', 'Neutral', 'Positive'])

    for txt in df['ban_goc']:
        soft_prob = lay_cam_xuc_soft(txt)
        y_soft_list.append(soft_prob)
        nhan_rule_based_list.append(cac_lop[np.argmax(soft_prob)])
        
    df['nhan_rule_based'] = nhan_rule_based_list
    y_train_soft = np.array(y_soft_list)

    # Huấn luyện LR Custom trực tiếp trên toàn bộ Soft Labels
    mo_hinh_lr = HoiQuyLogisticTuyChinh(toc_do_hoc=0.01, so_vong_lap=3000, lamda=5.0, batch_size=64, patience=50)
    mo_hinh_lr.huan_luyen(X_goc, y_train_soft)
    
    # Dự đoán bằng mô hình LR đã học
    df['cam_xuc_du_doan'] = mo_hinh_lr.du_doan(X_goc).tolist()

    # Lớp khiên cuối cùng: IF-ELSE vớt những câu máy dự đoán sai
    df['cam_xuc_du_doan'] = df.apply(
        lambda row: hieu_chinh_cam_xuc_theo_luat(row['ban_goc'], row['cam_xuc_du_doan']), 
        axis=1
    )

    self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Đang tổng hợp báo cáo...'})

    # TỔNG HỢP TOÀN BỘ KẾT QUẢ ĐỂ TRẢ VỀ FRONTEND
    so_luong_cam_xuc = df['cam_xuc_du_doan'].value_counts().to_dict()
    du_lieu_bieu_do_cam_xuc = [
        {"name": "Tích cực", "value": so_luong_cam_xuc.get("Positive", 0), "color": "#22c55e"},
        {"name": "Tiêu cực", "value": so_luong_cam_xuc.get("Negative", 0), "color": "#ef4444"},
        {"name": "Trung tính", "value": so_luong_cam_xuc.get("Neutral", 0), "color": "#94a3b8"}
    ]

    tat_ca_emoji = []
    for van_ban in df['ban_goc']:
        tat_ca_emoji.extend([c['emoji'] for c in emoji.emoji_list(van_ban)])
    emoji_hang_dau = Counter(tat_ca_emoji).most_common(10)
    du_lieu_emoji = [{"emoji": e[0], "count": e[1]} for e in emoji_hang_dau]

    df['diem_cam_xuc'] = df['cam_xuc_du_doan'].map({"Positive": 1.0, "Negative": -1.0, "Neutral": 0.0})

    # Giả định cột 'da_lam_sach' chưa được tạo trong task mới (nên ta sẽ chạy tạm nếu nó vắng mặt)
    if 'da_lam_sach' not in df.columns:
        # Nếu hàm lay_binh_luan chưa sinh ra cột này, sử dụng hàm an_danh để chạy wordcloud
        df['da_lam_sach'] = df['ban_goc'].apply(an_danh_ten_rieng_cho_bert_an_toan)

    du_lieu_dam_may_tu = tao_du_lieu_dam_may_tu(df['da_lam_sach'].tolist())
    du_lieu_toan_bo_binh_luan = df[['id', 'tac_gia', 'ban_goc', 'cam_xuc_du_doan', 'so_like', 'cum', 'diem_cam_xuc']].to_dict(orient='records')
    du_lieu_chuoi_thoi_gian = phan_tich_chuoi_thoi_gian(df)
    du_lieu_nguoi_dung_hang_dau = phan_tich_nguoi_dung_hang_dau(df)
    du_lieu_phan_tan = tao_du_lieu_bieu_do_phan_tan(df, X_pca_2d)

    # TRẢ VỀ DỮ LIỆU ĐẦY ĐỦ
    return {
        "video_url": url_youtube,
        "total_comments": len(df),
        "video_summary": video_summary_data,
        "original_transcript": video_summary_data.get("original_transcript", ""),
        "time_series": du_lieu_chuoi_thoi_gian,
        "sentiment_chart": du_lieu_bieu_do_cam_xuc,
        "emoji_stats": du_lieu_emoji,
        "word_cloud": du_lieu_dam_may_tu,
        "all_comments": du_lieu_toan_bo_binh_luan,
        "top_users": du_lieu_nguoi_dung_hang_dau,
        "scatter_clusters": du_lieu_phan_tan
    }