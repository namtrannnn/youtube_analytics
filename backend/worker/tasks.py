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

# Import các module tự viết (cập nhật tên đã Việt hóa)
from app.ml_models.custom_algorithms import KMeansTuyChinh, HoiQuyLogisticTuyChinh
from app.ml_models.text_processing import phan_tich_cam_xuc_theo_luat, TU_LOAI_BO_TIENG_VIET
from app.ml_models.youtube_utils import lay_binh_luan

# --- SỬA ĐỔI: KHÔNG TẢI MODEL NGAY LẬP TỨC ---
# Khai báo biến toàn cục là None để không chiếm Ram khi vừa import file
bo_tach_tu = None
mo_hinh = None

def tai_mo_hinh():
    global bo_tach_tu, mo_hinh
    if bo_tach_tu is not None and mo_hinh is not None:
        return
    try:
        # Thử tải từ cache local trước (Offline mode)
        print("Đang tìm Mô hình trong cache...")
        bo_tach_tu = AutoTokenizer.from_pretrained('bert-base-multilingual-cased', local_files_only=True)
        mo_hinh = AutoModel.from_pretrained('bert-base-multilingual-cased', local_files_only=True)
        print("Đã tải Mô hình từ ổ cứng (Offline)!")
    except Exception:
        # Nếu chưa có thì mới tải từ mạng
        print("Không tìm thấy cache, đang tải...")
        bo_tach_tu = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        mo_hinh = AutoModel.from_pretrained('bert-base-multilingual-cased')
        print("Đã tải và lưu Mô hình xong!")

def lay_vector_bert(danh_sach_van_ban):
    # Đảm bảo model đã được tải
    tai_mo_hinh()
    
    cac_vector = []
    mo_hinh.eval()
    with torch.no_grad():
        kich_thuoc_lo = 32
        for i in range(0, len(danh_sach_van_ban), kich_thuoc_lo):
            lo_van_ban = danh_sach_van_ban[i:i+kich_thuoc_lo]
            dau_vao = bo_tach_tu(lo_van_ban, return_tensors="pt", padding=True, truncation=True, max_length=128)
            dau_ra = mo_hinh(**dau_vao)
            vector_cls = dau_ra.last_hidden_state[:, 0, :].numpy()
            cac_vector.extend(vector_cls)
    return np.array(cac_vector)

def tao_du_lieu_dam_may_tu(danh_sach_van_ban):
    # 1. Nối toàn bộ comment thành 1 chuỗi lớn
    toan_bo_van_ban = " ".join(danh_sach_van_ban)
    
    # 2. Tách từ
    cac_tu = toan_bo_van_ban.split()
    
    # 3. [SỬA ĐỔI] Lọc "Rác" Triệt Để
    cac_tu_sach = []
    for tu in cac_tu:
        # Điều kiện giữ lại từ:
        # - Không nằm trong Stopwords
        # - Không phải là số (để loại bỏ '1', '2', '2025'...)
        # - Độ dài lớn hơn 1 (để loại bỏ các ký tự rác 'u', 'a', '-')
        # - HOẶC giữ lại số nếu đó là năm quan trọng (tùy chọn, ở đây mình lọc hết số cho sạch)
        if (tu not in TU_LOAI_BO_TIENG_VIET) and (not tu.isdigit()) and (len(tu) > 1):
            cac_tu_sach.append(tu)
            
    # 4. Đếm tần suất
    bo_dem = Counter(cac_tu_sach)
    
    # 5. Trả về format cho Frontend
    return [{"text": k, "value": v} for k, v in bo_dem.most_common(50)]

# --- HÀM BỔ SUNG: TOP USERS ---
def phan_tich_nguoi_dung_hang_dau(df_binh_luan):
    if 'tac_gia' not in df_binh_luan.columns:
        return []
        
    so_luong_nguoi_dung = df_binh_luan['tac_gia'].value_counts().head(5).reset_index()
    so_luong_nguoi_dung.columns = ['ten', 'so_luong']
    
    # Lấy thêm sentiment trung bình của user đó (nếu có)
    # Ở đây ta lấy sentiment của comment mới nhất làm đại diện cho đơn giản
    nguoi_dung_hang_dau = []
    for _, hang in so_luong_nguoi_dung.iterrows():
        ten_nguoi_dung = hang['ten']
        # Lấy sentiment của comment đầu tiên tìm thấy của user này
        cam_xuc_nguoi_dung = df_binh_luan[df_binh_luan['tac_gia'] == ten_nguoi_dung]['cam_xuc_du_doan'].iloc[0]
        nguoi_dung_hang_dau.append({
            "name": ten_nguoi_dung, 
            "count": int(hang['so_luong']), # Convert numpy int to python int
            "sentiment": cam_xuc_nguoi_dung
        })
        
    return nguoi_dung_hang_dau

# --- HÀM BỔ SUNG: SCATTER DATA TỪ CLUSTER ---
def tao_du_lieu_bieu_do_phan_tan(df, mang_vector_X):
    """
    Sử dụng PCA để giảm chiều vector từ 768 chiều -> 2 chiều (x, y)
    để vẽ biểu đồ phân bố thực tế.
    """
    if len(df) < 2:
        return []

    # 1. Giảm chiều dữ liệu (768 -> 2)
    pca = PCA(n_components=2)
    toa_do = pca.fit_transform(mang_vector_X)

    # 2. Chuẩn hóa dữ liệu về khoảng [0, 100] để dễ vẽ trên biểu đồ
    # Vì PCA có thể ra số âm hoặc số rất lẻ, ta scale lại cho đẹp
    bo_chuan_hoa = MinMaxScaler(feature_range=(0, 100))
    toa_do_da_chuan_hoa = bo_chuan_hoa.fit_transform(toa_do)

    du_lieu_phan_tan = []
    
    # 3. Gép tọa độ vào thông tin bài viết
    # toa_do_da_chuan_hoa là mảng numpy [[x1, y1], [x2, y2], ...]
    for i, hang in df.iterrows():
        # Lấy tọa độ tương ứng
        x = toa_do_da_chuan_hoa[i][0]
        y = toa_do_da_chuan_hoa[i][1]
        
        du_lieu_phan_tan.append({
            "x": round(float(x), 2),
            "y": round(float(y), 2),
            "z": 100, # Kích thước điểm ảnh (có thể thay đổi theo số like nếu muốn)
            "cluster": f"Nhóm {hang['cum']}", # Để tô màu theo nhóm
            "author": hang['tac_gia'],
            "content": hang['ban_goc'][:50] + "..." # Trích đoạn nội dung để hiển thị tooltip
        })
    
    return du_lieu_phan_tan

# --- HÀM PHỤ TRỢ: CHUYỂN ĐỔI "2 ngày trước" -> DATETIME ---
def phan_tich_ngay_tuong_doi(chuoi_ngay):
    """
    Chuyển đổi thời gian tương đối: '2 seconds ago', '5 phút trước' -> datetime object
    Hỗ trợ đầy đủ: Giây, Phút, Giờ, Ngày, Tuần, Tháng, Năm
    """
    # Mặc định trả về hiện tại nếu input lỗi
    hien_tai = datetime.now()
    
    if not isinstance(chuoi_ngay, str): 
        return hien_tai
    
    # Chuẩn hóa chuỗi: chữ thường, bỏ khoảng trắng thừa
    chuoi_ngay = chuoi_ngay.lower().strip()
    
    # Xử lý các trường hợp "(edited)" hoặc "(đã chỉnh sửa)"
    if '(' in chuoi_ngay: chuoi_ngay = chuoi_ngay.split('(')[0].strip()
    
    try:
        # 1. Tìm số lượng (Ví dụ: lấy số 8 từ "8 năm")
        tim_gia_tri = re.search(r'\d+', chuoi_ngay)
        gia_tri = int(tim_gia_tri.group()) if tim_gia_tri else 1
        
        # 2. Xử lý Logic thời gian (Dựa trên từ khóa đơn vị)        
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
            # 1 tháng ~ 30 ngày
            khoang_thoi_gian = timedelta(days=gia_tri * 30)
            
        elif any(x in chuoi_ngay for x in ['year ago', 'năm trước']): 
            # 1 năm ~ 365 ngày
            khoang_thoi_gian = timedelta(days=gia_tri * 365)
            
        else:
            # Trường hợp không tìm thấy đơn vị nào (VD: "vừa xong", "just now")
            khoang_thoi_gian = timedelta(seconds=0)
            
        # Trả về datetime object để pandas dễ xử lý
        return hien_tai - khoang_thoi_gian

    except Exception:
        # Nếu lỗi bất kỳ, trả về thời gian hiện tại
        return hien_tai

# --- HÀM CHÍNH
def phan_tich_chuoi_thoi_gian(df):
    ten_cot = 'thoi_gian_dang' if 'thoi_gian_dang' in df.columns else 'time'
    
    # Nếu không có dữ liệu thời gian -> Trả về rỗng (chấp nhận biểu đồ trống)
    if ten_cot not in df.columns:
        return []
    print("👉 Mẫu dữ liệu thời gian gốc:", df[ten_cot].unique()[:5])
    try:
        # 1. Parse ra datetime đầy đủ (Ngày + Giờ)
        # Sử dụng hàm phan_tich_ngay_tuong_doi đã viết ở bước trước
        df['thoi_gian_thuc'] = pd.to_datetime(df[ten_cot].apply(phan_tich_ngay_tuong_doi), errors='coerce')
        
        # Bỏ các dòng lỗi
        df = df.dropna(subset=['thoi_gian_thuc'])
        if df.empty: return []

        # 2. Tính khoảng cách thời gian (Span)
        thoi_gian_nho_nhat = df['thoi_gian_thuc'].min()
        thoi_gian_lon_nhat = df['thoi_gian_thuc'].max()
        chenh_lech_thoi_gian = thoi_gian_lon_nhat - thoi_gian_nho_nhat

        # 3. QUYẾT ĐỊNH CHẾ ĐỘ HIỂN THỊ
        # Nếu khoảng cách giữa cmt đầu và cuối < 24 giờ -> Nhóm theo GIỜ
        if chenh_lech_thoi_gian.days < 1: 
            # Làm tròn xuống theo giờ (Floor Hour). VD: 14:15 -> 14:00
            df['khoa_nhom'] = df['thoi_gian_thuc'].dt.floor('H')
            la_che_do_theo_gio = True
        else:
            # Nhóm theo NGÀY (Floor Day). VD: 2023-10-25 14:00 -> 2023-10-25
            df['khoa_nhom'] = df['thoi_gian_thuc'].dt.floor('D')
            la_che_do_theo_gio = False

        # 4. GroupBy và Đếm
        truc_thoi_gian = df.groupby('khoa_nhom').size().reset_index(name='so_luong_binh_luan')
        truc_thoi_gian = truc_thoi_gian.sort_values('khoa_nhom')

        # 5. Format dữ liệu trả về cho Frontend
        # Nếu theo giờ: Trả về đầy đủ "YYYY-MM-DD HH:mm" để Frontend dễ parse
        truc_thoi_gian['date'] = truc_thoi_gian['khoa_nhom'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Đổi tên cột về comments để đồng bộ format cho FrontEnd
        truc_thoi_gian.rename(columns={'so_luong_binh_luan': 'comments'}, inplace=True)
        return truc_thoi_gian[['date', 'comments']].to_dict(orient='records')

    except Exception as e:
        print(f"Lỗi Chuỗi Thời Gian: {e}")
        return []

@shared_task(bind=True)
def analyze_video_task(self, url_youtube, so_luong_binh_luan):
    # --- GỌI HÀM TẢI MODEL Ở ĐÂY ---
    # Lúc này code đang chạy ở Container Worker (có DNS 8.8.8.8), nên sẽ tải được
    tai_mo_hinh()
    
    self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Đang quét thông tin kênh...'})
    
    # 1. Crawl Data
    df = lay_binh_luan(url_youtube, gioi_han=so_luong_binh_luan)
    if df.empty:
        return {"error": "Không tìm thấy bình luận hoặc lỗi tải."}
    
    self.update_state(state='PROGRESS', meta={'progress': 40, 'status': f'Đã tải {len(df)} bình luận. Đang vector hóa...'})

    # 2. Vector hóa (BERT)
    try:
        X = lay_vector_bert(df['da_lam_sach'].tolist())
    except Exception as e:
        return {"error": f"Lỗi xử lý: {str(e)}"}
    
    self.update_state(state='PROGRESS', meta={'progress': 60, 'status': 'Đang chạy thuật toán...'})

    # 3. Chạy thuật toán tự viết (Custom ML)
    kmeans = KMeansTuyChinh(so_cum=3, so_vong_lap_toi_da=50)
    # Convert numpy array thành list chuẩn Python để tránh lỗi JSON
    df['cum'] = kmeans.huan_luyen_va_du_doan(X).tolist()

    mo_hinh_lr = HoiQuyLogisticTuyChinh(toc_do_hoc=0.1, so_vong_lap=1000)
    y_gia = np.array([phan_tich_cam_xuc_theo_luat(txt) for txt in df['ban_goc']])
    mo_hinh_lr.huan_luyen(X, y_gia)
    df['cam_xuc_du_doan'] = mo_hinh_lr.du_doan(X).tolist()

    self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Đang tổng hợp thống kê...'})

    # 4. Tổng hợp kết quả
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

    du_lieu_dam_may_tu = tao_du_lieu_dam_may_tu(df['da_lam_sach'].tolist())

    du_lieu_toan_bo_binh_luan = df[['tac_gia', 'ban_goc', 'cam_xuc_du_doan']].to_dict(orient='records')
    
    # 1. Time Series
    du_lieu_chuoi_thoi_gian = phan_tich_chuoi_thoi_gian(df)

    # 2. Top Users
    du_lieu_nguoi_dung_hang_dau = phan_tich_nguoi_dung_hang_dau(df)

    # 3. Scatter Plot Data
    du_lieu_phan_tan = tao_du_lieu_bieu_do_phan_tan(df, X)

    # Trả về kết quả (Lưu ý: Giữ nguyên key tiếng Anh để Frontend không bị lỗi)
    return {
        "time_series": du_lieu_chuoi_thoi_gian,
        "video_url": url_youtube,
        "total_comments": len(df),
        "sentiment_chart": du_lieu_bieu_do_cam_xuc,
        "emoji_stats": du_lieu_emoji,
        "word_cloud": du_lieu_dam_may_tu,
        "all_comments": du_lieu_toan_bo_binh_luan,
        "top_users": du_lieu_nguoi_dung_hang_dau,
        "scatter_clusters": du_lieu_phan_tan
    }