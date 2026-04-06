import re
import emoji

# --- TỪ ĐIỂN TEENCODE ---
TU_DIEN_TEENCODE = {
    # Phủ định
    'ko': 'không', 'k': 'không', 'kh': 'không', 'khong': 'không', 'kg': 'không', 
    'hong': 'không', 'hok': 'không', 'khum': 'không', 'k0': 'không', 'hem': 'không',
    'hông': 'không', 'kô': 'không', 'nô': 'không', 'chư': 'chưa', 'chửa': 'chưa',
            
    # Đồng ý/Khẳng định
    'dc': 'được', 'đc': 'được', 'dk': 'được', 'dx': 'được', 'đx': 'được',
    'oki': 'ok', 'oke': 'ok', 'uk': 'ừ', 'ukm': 'ừ', 'uh': 'ừ', 'okela': 'ok',
    'dạk': 'dạ', 'vângg': 'vâng', 'đúm': 'đúng', 'chuẩn': 'đúng', 'đg': 'đúng',
            
    # Đại từ nhân xưng & Các mối quan hệ
    'mik': 'mình', 'mk': 'mình', 'mjnh': 'mình', 'm': 'mình', 't': 'tôi', 'toy': 'tôi', 'toi': 'tôi',
    'b': 'bạn', 'bn': 'bạn', 'pạn': 'bạn', 'mem': 'thành viên', 'ad': 'quản trị viên',
    'mn': 'mọi người', 'm.n': 'mọi người', 'ngta': 'người ta', 'ngt': 'người ta',
    'ae': 'anh em', 'ce': 'chị em', 'a': 'anh', 'e': 'em', 'cj': 'chị',
    'vk': 'vợ', 'ck': 'chồng', 'cr': 'crush', 'ny': 'người yêu', 'ex': 'người yêu cũ', 'nyc': 'người yêu cũ',
    'bff': 'bạn thân', 'gđ': 'gia đình', 'hs': 'học sinh', 'sv': 'sinh viên', 'gv': 'giáo viên', 'ngk':'người khác',
            
    # Hành động/Tính từ/Trạng từ (Giao tiếp cơ bản)
    'bt': 'bình thường', 'bth': 'bình thường', 'bthg': 'bình thường',
    'nt': 'nhắn tin', 'ib': 'nhắn tin', 'rep': 'trả lời', 'tl': 'trả lời', 'cmt': 'bình luận',
    'iu': 'yêu', 'yeu': 'yêu', 'thik': 'thích', 'chê': 'không thích',
    'j': 'gì', 'zì': 'gì', 'gì z': 'gì vậy', 'z': 'vậy', 'zay': 'vậy', 'zậy': 'vậy', 'v': 'vậy',
    'tks': 'cảm ơn', 'thanks': 'cảm ơn', 'tk': 'cảm ơn', 'cam on': 'cảm ơn', 'cảm mơn': 'cảm ơn',
    'xl': 'xin lỗi', 'srr': 'xin lỗi', 'sori': 'xin lỗi','sr': 'xin lỗi', 'sory': 'xin lỗi',
    'ng': 'người', 'n': 'người',
    'ms': 'mới', 'lm': 'làm', 'bik': 'biết', 'bit': 'biết', 'hỉu': 'hiểu',
    'h': 'giờ', 'p': 'phút',
    'cx': 'cũng', 'lun': 'luôn', 'luân': 'luôn',
    'ak': 'à', 'ah': 'à', 'ha': 'hả', 'há': 'hả',
    'vs': 'với', 'wa': 'quá', 'wá': 'quá', 
    'r': 'rồi', 'roi': 'rồi', 'rùi': 'rồi', 'gòi': 'rồi', 'gòy': 'rồi',
    'bh': 'bây giờ', 'hqa': 'hôm qua', 'hnay': 'hôm nay', 'mai': 'ngày mai',
    
    # Từ nối / Câu hỏi thường gặp
    'nma': 'nhưng mà', 'nvay': 'như vậy', 'ntn': 'như thế nào', 'tnao': 'thế nào',
    'đk': 'đúng không', 'ns': 'nói', 'nhiu': 'nhiêu', 'nhìu': 'nhiều',
    'bnhiu': 'bao nhiêu', 'kb': 'không biết', 'thui': 'thôi', 'thoai': 'thôi',
    'lquan': 'liên quan', 'klq': 'không liên quan', 'ncl': 'nói chung là', 
    'nx': 'nữa', 'mún': 'muốn', 'nc': 'nước', 'cs':'có', 'snvv': 'sinh nhật vui vẻ',

    # Thể hiện cảm xúc / Cảm thán / Miêu tả
    'vcl': 'vãi', 'vl': 'vãi', 'vler': 'vãi', 'vđ': 'vãi',
    'gato': 'ghen tị', 'ato': 'ảo tưởng', 'chảnh': 'kiêu ngạo',
    'tr': 'trời', 'trùi': 'trời', 'chời': 'trời', 'ui': 'ôi', 'qtqd': 'quá trời quá đất',
    'cít': 'cứt', 'cucws': 'cứt', 'hnhu': 'hình như',
    'dth': 'dễ thương', 'dzth': 'dễ thương', 'xjh': 'xinh', 'dz': 'đẹp trai', 'đz': 'đẹp trai',
    'bùn': 'buồn', 'zui': 'vui', 'xu': 'xui xẻo', 'xucana': 'xui xẻo',
    
    # Thuật ngữ MXH
    'stt': 'trạng thái', 'avt': 'ảnh đại diện', 'in4': 'thông tin', 'link': 'đường dẫn', 'font': 'phông chữ',
}

# --- TỪ KHÓA ---
TU_KHOA_TICH_CUC = [
    # Khen ngợi chung
    'hay', 'tuyệt', 'đỉnh', 'thích', 'yêu', 'ngon', 'quá đã', 'xuất sắc', '10 điểm', 
    'mê', 'đẹp', 'giỏi', 'cảm ơn', 'ý nghĩa', 'siêu', 'hóng', 'vui', 'xịn', 'tốt',
    'support', 'ủng hộ', 'fighting', 'best', 'nhất', 'thấm', 'cuốn', 'chất', 'mượt', 'lót dép', 'chu đáo',
            
    # Slang tích cực/Gen Z
    'cháy', 'mlem', 'bén', 'dính', 'keo', 'slay', 'bánh cuốn', 'gét gô', 'đỉnh chóp',
    'hết nước chấm', 'uy tín', 'đáng yêu', 'cute', 'dễ thương', 'ngầu', 'xin vía',
            
    # Cảm xúc/Hài hước
    'hài', 'cười', 'giải trí', 'thư giãn', 'hạnh phúc', 'xúc động', 'khóc', 
    'ngưỡng mộ', 'respect', 'nể', 'tâm huyết', 'đầu tư', 'sâu sắc', 'nhân văn', 'hy vọng', 'truyền cảm hứng',
    'động lực', 'đáng mơ ước', 'đã ghê', 'chúc', 'may mắn', 'tuyệt vời', 'yêu lắm', 
]

TU_KHOA_TIEU_CUC = [
    # Chê bai chung
    'chán', 'dở', 'tệ', 'buồn', 'xấu', 'lag', 'rác', 'nhạt', 'phế', 'cứt', 'đần', 
    'ghét', 'phẫn nộ', 'kém', 'thất vọng', 'xàm', 'bịp', 'lừa', 'dislike', 'tắt',
    'ồn', 'đau', 'kém', 'xấu', 'kinh', 'phí', 'tiếc',
            
    # Slang tiêu cực/Chửi bới
    'ngu', 'óc', 'trẩu', 'súc vật', 'chó', 'điên', 'khùng', 'biến',
    'nhảm', 'xàm xí', 'xàm lờ', 'câu view', 'câu like', 'bú fame', 'lố', 'ô dề',
    'giả trân', 'flop', 'xu cà na', 'toxic', 'hãm', 'chấn bé đù',
            
    # Phản đối/Kỹ thuật
    'phản đối', 'tẩy chay', 'xóa', 'report', 'mờ', 'giật', 'quảng cáo', 'spam', 
    'không hay', 'phí tiền', 'phí thời gian', 'đừng xem', 'đổ lỗi', 'xúc phạm IQ người xem',
    'não tàn', 'não', 'cũng chịu','làm ăn thế này', 'cẩu thả', 'nội dung thối não', 'chả khác gì coi thường',
    'coi thường', 'nát', 'cẩu','xúc phạm người xem','ăn chửi', 'chỉ đến mức này thôi à','nhục nhã','vẫn sai hoàn sai',
    'thấy ngứa mắt', 'nghiện','ma túy','trộm', 'ảo tưởng',
]

TU_LOAI_BO_TIENG_VIET = {
    'là', 'và', 'của', 'thì', 'mà', 'có', 'nhưng', 'với', 'những', 'này', 
    'cho', 'được', 'cũng', 'đã', 'trong', 'để', 'các', 'một', 'làm', 'người',
    'tại', 'bởi', 'vì', 'rằng', 'nếu', 'dù', 'hoặc', 'tuy', 
    'em', 'anh', 'mình', 'bạn', 'tôi', 'tao', 'mày', 'nó', 'họ', 'chị', 'chú', 'bác',
    'admin', 'kênh', 'video', 'clip', 'xem', 'kênh', 'vid', 'tui', 'ad', 'ta',
    'ạ', 'ơi', 'nha', 'ôi', 'ủa', 'ae', 'nhé', 'nhỉ', 'ha', 'hả', 'hở', 'á', 'cơ', 
    'đâu', 'đấy', 'đó', 'kia', 'nọ', 'rồi', 'vậy', 'thôi', 'luôn', 'ngay',
    'không', 'ko', 'k', 'kh', 'khong', # Phủ định
    'năm', 'nay', 'hôm', 'ngày', 'giờ', 'phút', 'năm nay','năm ngoái', # Thời gian
    'phải', 'đến', 'ra', 'vào', 'lên', 'xuống', # Động từ chỉ hướng/trạng thái
    'quá', 'lắm', 'thật', 'thiệt', 'rất', 'hơi', # Trạng từ mức độ
    'ông', 'bà', 'anh', 'chị', 'em', 'tui', 'mình', 'nó', 'họ', 'bạn', # Xưng hô
    'cái', 'con', 'chiếc', 'vụ', 'việc', 'điều', 'thứ', # Loại từ
    'thấy', 'biết', 'nói', 'bảo', 'nghe', 'nhìn', # Động từ giác quan
    'rồi', 'xong', 'chưa', 'vẫn', 'còn', 'cứ', # Trạng thái
    'đâu', 'đó', 'đây', 'kia','ai', # Chỉ định từ
    'nhỉ', 'nhé', 'nha', 'hả', 'luôn', 'ngay', # Từ đệm
    'chắc', 'tưởng', 'ngỡ', 'hình', 'như', # Phỏng đoán
    'từ', 'theo', 'do', 'bị', 'khi', 'lúc', 'nào', # Giới từ khác
    'video','chỉ','nè',
}

def lam_sach_van_ban(van_ban, xoa_tu_loai_bo=False): 
    if not isinstance(van_ban, str): return ""
    
    # 1. Chuyển chữ thường
    van_ban = van_ban.lower()
    
    # 2. Xóa URL & Mention
    van_ban = re.sub(r'http\S+', '', van_ban)
    van_ban = re.sub(r'@[\w\.-]+', '', van_ban)
    
    # 3. Xóa ký tự đặc biệt (Giữ lại chữ và số)
    van_ban = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ0-9]', ' ', van_ban)
    
    # XỬ LÝ TIẾNG CƯỜI VÀ VÀI KÝ TỰ ĐẶC BIỆT TRƯỚC KHI RÚT GỌN KÝ TỰ
    van_ban = re.sub(r'\bk{2,}\b', ' haha ', van_ban)
    van_ban = re.sub(r'\bh{2,}\b', ' haha ', van_ban)
    van_ban = re.sub(r'\b(ha){2,}(h)?\b', ' haha ', van_ban)
    van_ban = re.sub(r'\b(he){2,}(h)?\b', ' haha ', van_ban)
    van_ban = re.sub(r'\b(hi){2,}(h)?\b', ' haha ', van_ban)
    van_ban = re.sub(r'\bz{2,}\b', ' khò ', van_ban)
    van_ban = re.sub(r'\ba{2,}\b', ' á ', van_ban)
    van_ban = re.sub(r'\bp{2,}\b', ' tạm biệt ', van_ban)
    
    # 4. Xóa ký tự kéo dài
    van_ban = re.sub(r'([a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ])\1{2,}', r'\1', van_ban)
    
    # 5. Tách từ
    cac_tu = van_ban.split()
    
    # 6. Chuẩn hóa Teencode
    cac_tu = [TU_DIEN_TEENCODE.get(tu, tu) for tu in cac_tu]
    
    # 7. Lọc Stopwords (Chỉ áp dụng cho WordCloud hoặc khi cần)
    if xoa_tu_loai_bo:
        cac_tu = [tu for tu in cac_tu if tu not in TU_LOAI_BO_TIENG_VIET and not tu.isdigit()] 
        
    van_ban = ' '.join(cac_tu)
    van_ban = re.sub(r'\s+', ' ', van_ban).strip()
    return van_ban

def tinh_diem_cam_xuc_tho(van_ban):
    van_ban_thuong = van_ban.lower()
    diem_pos = 0
    diem_neg = 0
    
    #1. Xử lý từ phủ định
    tu_phu_dinh = ['không ', 'ko ', 'k ', 'kh ', 'khong ', 'chưa ', 'chả ', 'chẳng ']
    
    for pd in tu_phu_dinh:
        for tc in TU_KHOA_TICH_CUC:
            cum_tu = pd + tc
            if cum_tu in van_ban_thuong:
                diem_neg += 1 
                van_ban_thuong = van_ban_thuong.replace(cum_tu, "")
        for tc in TU_KHOA_TIEU_CUC:
            cum_tu = pd + tc
            if cum_tu in van_ban_thuong:
                diem_pos += 1 
                van_ban_thuong = van_ban_thuong.replace(cum_tu, "")
                
    # 3. Đếm từ đơn
    for tu in TU_KHOA_TIEU_CUC:
        if tu in van_ban_thuong: 
            diem_neg += 1
            van_ban_thuong = van_ban_thuong.replace(tu, "")
    for tu in TU_KHOA_TICH_CUC:
        if tu in van_ban_thuong: 
            diem_pos += 1
            van_ban_thuong = van_ban_thuong.replace(tu, "")
            
    return diem_pos, diem_neg

def phan_tich_cam_xuc_theo_luat(van_ban, return_confidence=False):
    diem_pos, diem_neg = tinh_diem_cam_xuc_tho(van_ban)
        
    ds_bieu_tuong = [c['emoji'] for c in emoji.emoji_list(van_ban)]
    icon_tich_cuc = ['❤', '🥰', '😍', '👍', '😂', '🔥', '😘', '😊', '😁', '❤️', '💕', '🤣', '😆', '😋', '😎', '😚', '🤗', '🤑', '🍀', '🌹', '🎊']
    icon_tieu_cuc = ['💔', '👎', '😭', '😢', '😡', '🤬', '😞', '😒', '🤦‍♀️','🤦‍♂️','😑','🙄','😔','😓','☹️','🙁','😟','😰','😱','💀','☠️','💩','🙏']
    
    for icon in ds_bieu_tuong:
        if icon in icon_tich_cuc: diem_pos += 1
        if icon in icon_tieu_cuc: diem_neg += 1

    # GHI ĐÈ EMOJI: Vô hiệu hóa điểm tích cực từ mặt cười nếu text chửi quá gắt (>=2 lỗi)
    _, diem_tu_text_chi_dinh = tinh_diem_cam_xuc_tho(van_ban)
    if diem_tu_text_chi_dinh >= 2 and diem_pos > 0:
        diem_pos = 0 

    tong_diem = diem_pos - diem_neg
    
    # Đánh giá độ tin cậy (Dùng cho phương pháp Weak Supervision)
    is_high_confidence = False
    if (diem_pos > 0 and diem_neg == 0) or (diem_neg > 0 and diem_pos == 0) or (diem_pos == 0 and diem_neg == 0):
        is_high_confidence = True

    nhan = "Neutral"
    if tong_diem > 0: nhan = "Positive"
    elif tong_diem < 0: nhan = "Negative"
    
    if return_confidence:
        return nhan, is_high_confidence
    return nhan

def la_binh_luan_rac(van_ban):
    van_ban = van_ban.lower().strip()
    
    # 1. Comment quá ngắn (dưới 2 ký tự)
    if len(van_ban) < 2: return True
    
    # 2. Comment chỉ toàn số (VD: "2025")
    if van_ban.isdigit(): return True
    
    # 3. Comment điểm danh (VD: "Ai 2025?", "2025 điểm danh")
    mau_binh_luan_rac = [
        r'^ai xem.*202\d.*',      # Ai xem... 202x
        r'^202\d\s*điểm danh',    # 202x điểm danh
        r'^có ai.*202\d.*',       # Có ai... 202x
        r'^202\d\s*👇',            # 202x + icon chỉ tay
        r'^202\d\s*chấm'          # 202x chấm
    ]
    for mau in mau_binh_luan_rac:
        if re.search(mau, van_ban):
            return True
            
    return False