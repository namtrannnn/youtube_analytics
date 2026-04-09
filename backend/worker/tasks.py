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
from app.ml_models.text_processing import phan_tich_cam_xuc_theo_luat, TU_LOAI_BO_TIENG_VIET
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

    #kiểm tra Cuda để tăng tốc (nếu server có GPU)
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
            vector_cls = dau_ra.last_hidden_state[:, 0, :].cpu().numpy()
            cac_vector.extend(vector_cls)
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

    # Chỉ cần chuẩn hóa tọa độ 2D đã được PCA xử lý từ trước
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
    
def an_danh_ten_rieng_cho_bert_an_toan(van_ban):
    """
    Tìm và thay thế các từ viết hoa chữ cái đầu (tên riêng) thành 'ai_đó'
    giúp BERT không bị thành kiến (bias) với các tên cụ thể.
    """
    if not isinstance(van_ban, str): 
        return ""
    
    # Regex tìm các từ viết hoa chữ cái đầu tiếng Việt
    pattern_hoa = r'\b[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ][a-zàáâãèéêìíòóôõùúăđĩũơưăạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]*\b'
    
    # Thay tên riêng bằng token 'ai_đó'
    cau_da_che = re.sub(pattern_hoa, 'ai_đó', van_ban)
    
    # Gom các chữ 'ai_đó' đứng cạnh nhau thành 1 chữ duy nhất cho tự nhiên
    cau_hoan_thien = re.sub(r'(ai_đó\s*)+', 'ai_đó ', cau_da_che)
    
    return cau_hoan_thien.strip()

def hieu_chinh_cam_xuc_theo_luat(cau_goc, nhan_may_doan):
    if not isinstance(cau_goc, str): return nhan_may_doan
    cau_thuong = cau_goc.lower()
    
    cac_tu = cau_thuong.split()
    if not cac_tu: return nhan_may_doan
    if cac_tu[-1] == 'ạ': return "Positive"
    
    kinh_ngu = ['dạ', 'vâng', 'thưa', 'xin mời', 'mời']
    if any(tu in cac_tu for tu in kinh_ngu): 
        return "Positive"

    cum_tu_tich_cuc_manh = ["không thua kém", "không kém", 'chúc', 'cảm ơn', 'cám ơn', 'hi vọng']
    if any(cum in cau_thuong for cum in cum_tu_tich_cuc_manh):
        return "Positive"
        
    return nhan_may_doan

# ===================================================================================
# CELERY TASK CHÍNH
# ===================================================================================
@shared_task(bind=True)
def analyze_video_task(self, url_youtube, so_luong_binh_luan):
    tai_mo_hinh()
    
    # Hàm callback để cập nhật % tiến trình từ các module bên ngoài
    def report_progress(percent, message):
        self.update_state(state='PROGRESS', meta={'progress': percent, 'status': message})
    # ---------------------------------------------------------
    # BƯỚC 1: TRÍCH XUẤT VÀ TÓM TẮT NỘI DUNG VIDEO
    # ---------------------------------------------------------
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
    
    # ---------------------------------------------------------
    # BƯỚC 2: CRAWL BÌNH LUẬN YOUTUBE
    # ---------------------------------------------------------
    self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Đang quét thông tin kênh và bình luận...'})
    
    df = lay_binh_luan(url_youtube, gioi_han=so_luong_binh_luan)
    if df.empty:
        # Nếu không có bình luận, vẫn trả về tóm tắt video và các mảng rỗng
         return {
            "video_url": url_youtube,
            "total_comments": 0,
            "video_summary": video_summary_data, # Vẫn giữ lại bản tóm tắt
            "time_series": [],
            "sentiment_chart": [],
            "emoji_stats": [],
            "word_cloud": [],
             "all_comments": [],
            "top_users": [],
             "scatter_clusters": [],
            "warning": "Không tìm thấy bình luận nào, nhưng tóm tắt video đã được tạo thành công." # Gửi kèm cảnh báo cho frontend
        }
    
    self.update_state(state='PROGRESS', meta={'progress': 50, 'status': f'Đã tải {len(df)} bình luận. Đang phân tích...'})

    # ---------------------------------------------------------
    # BƯỚC 3: VECTOR HÓA VÀ ML CUSTOM
    # ---------------------------------------------------------
    try:
        danh_sach_cho_bert = [an_danh_ten_rieng_cho_bert_an_toan(txt) for txt in df['ban_goc'].tolist()]
        
        X_goc = lay_vector_bert(danh_sach_cho_bert)
        # Giảm từ 768 chiều của BERT xuống 2 chiều
        pca = PCA(n_components=2)
        X_pca_2d = pca.fit_transform(X_goc)

    except Exception as e:
        return {"error": f"Lỗi xử lý ngôn ngữ tự nhiên: {str(e)}"}
    
    self.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'Đang chạy thuật toán phân cụm & đánh giá cảm xúc...'})

    # Chạy K-Means
    kmeans = KMeansTuyChinh(so_cum=3, so_vong_lap_toi_da=100)
    df['cum'] = kmeans.huan_luyen_va_du_doan(X_pca_2d).tolist()

    # Chạy Gán Nhãn Bằng Luật + Weak Supervision Logistic Regression
    nhan_rule_based_list = []
    is_confident_list = []

    for txt in df['ban_goc']:
        nhan, is_conf = phan_tich_cam_xuc_theo_luat(txt, return_confidence=True)
        nhan_rule_based_list.append(nhan)
        is_confident_list.append(is_conf)
        
    df['nhan_rule_based'] = nhan_rule_based_list
    df['is_confident'] = is_confident_list

    # Lọc mẫu tin cậy để train
    chi_so_tin_cay = df[df['is_confident'] == True].index.tolist()
    
    if len(chi_so_tin_cay) > 0:
        X_train_weak = X_goc[chi_so_tin_cay]
        y_train_weak = df.loc[chi_so_tin_cay, 'nhan_rule_based'].values
        
        mo_hinh_lr = HoiQuyLogisticTuyChinh(toc_do_hoc=0.1, so_vong_lap=3000, lamda=1.0)
        mo_hinh_lr.huan_luyen(X_train_weak, y_train_weak)
        
        df['cam_xuc_du_doan'] = mo_hinh_lr.du_doan(X_goc).tolist()
    else:
        # Nếu không có câu nào đạt tin cậy cao, dùng nhãn bộ luật
        df['cam_xuc_du_doan'] = df['nhan_rule_based']

    # Lớp khiên cuối cùng: IF-ELSE vớt những câu máy dự đoán sai
    df['cam_xuc_du_doan'] = df.apply(
        lambda row: hieu_chinh_cam_xuc_theo_luat(row['ban_goc'], row['cam_xuc_du_doan']), 
        axis=1
    )

    self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Đang tổng hợp báo cáo...'})

    # ---------------------------------------------------------
    # BƯỚC 4: TỔNG HỢP TOÀN BỘ KẾT QUẢ ĐỂ TRẢ VỀ FRONTEND
    # ---------------------------------------------------------
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