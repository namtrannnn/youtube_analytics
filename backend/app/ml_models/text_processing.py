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
    'vk': 'vợ', 'ck': 'chồng', 'cr': 'crush', 'ny': 'người yêu', 'ex': 'người yêu cũ',
    'bff': 'bạn thân', 'gđ': 'gia đình', 'hs': 'học sinh', 'sv': 'sinh viên', 'gv': 'giáo viên',
            
    # Hành động/Tính từ/Trạng từ (Giao tiếp cơ bản)
    'bt': 'bình thường', 'bth': 'bình thường', 'bthg': 'bình thường',
    'nt': 'nhắn tin', 'ib': 'nhắn tin', 'rep': 'trả lời', 'tl': 'trả lời', 'cmt': 'bình luận',
    'iu': 'yêu', 'yeu': 'yêu', 'thik': 'thích', 'chê': 'không thích',
    'j': 'gì', 'zì': 'gì', 'gì z': 'gì vậy', 'z': 'vậy', 'zay': 'vậy', 'zậy': 'vậy', 'v': 'vậy',
    'tks': 'cảm ơn', 'thanks': 'cảm ơn', 'tk': 'cảm ơn', 'cam on': 'cảm ơn', 'cảm mơn': 'cảm ơn',
    'xl': 'xin lỗi', 'srr': 'xin lỗi', 'sori': 'xin lỗi','sr': 'xin lỗi',
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
    'đk': 'đúng không', 'ns': 'nói', 'nhiu': 'nhiều', 'nhìu': 'nhiều',
    'bnhiu': 'bao nhiêu', 'kb': 'không biết', 'thui': 'thôi', 'thoai': 'thôi',
    'lquan': 'liên quan', 'klq': 'không liên quan', 'ncl': 'nói chung là', 
    'nx': 'nữa', 'mún': 'muốn', 'nc': 'nước',

    # Thể hiện cảm xúc / Cảm thán / Miêu tả
    'vcl': 'vãi', 'vl': 'vãi', 'vler': 'vãi', 'vđ': 'vãi',
    'gato': 'ghen tị', 'ato': 'ảo tưởng', 'chảnh': 'kiêu ngạo',
    'tr': 'trời', 'trùi': 'trời', 'chời': 'trời', 'ui': 'ôi', 'qtqd': 'quá trời quá đất',
    'cít': 'cứt', 'cucws': 'cứt', 'hnhu': 'hình như',
    'dth': 'dễ thương', 'dzth': 'dễ thương', 'xjh': 'xinh', 'dz': 'đẹp trai', 'đz': 'đẹp trai',
    'bùn': 'buồn', 'zui': 'vui', 'xu': 'xui xẻo', 'xucana': 'xui xẻo',
    
    # Thuật ngữ MXH
    'stt': 'trạng thái', 'avt': 'ảnh đại diện', 'in4': 'thông tin', 'link': 'đường dẫn'
}

# --- TỪ KHÓA ---
TU_KHOA_TICH_CUC = [
    # Khen ngợi chung
    'hay', 'tuyệt', 'đỉnh', 'thích', 'yêu', 'ngon', 'quá đã', 'xuất sắc', '10 điểm', 
    'mê', 'đẹp', 'giỏi', 'cảm ơn', 'ý nghĩa', 'siêu', 'hóng', 'vui', 'xịn', 'tốt',
    'support', 'ủng hộ', 'fighting', 'best', 'nhất', 'thấm', 'cuốn', 'chất', 'mượt',
            
    # Slang tích cực/Gen Z
    'cháy', 'mlem', 'bén', 'dính', 'keo', 'slay', 'bánh cuốn', 'gét gô', 'đỉnh chóp',
    'hết nước chấm', 'uy tín', 'đáng yêu', 'cute', 'dễ thương', 'ngầu',
            
    # Cảm xúc/Hài hước
    'hài', 'cười', 'giải trí', 'thư giãn', 'hạnh phúc', 'xúc động', 'khóc', 
    'ngưỡng mộ', 'respect', 'nể', 'tâm huyết', 'đầu tư', 'sâu sắc', 'nhân văn',
]

TU_KHOA_TIEU_CUC = [
    # Chê bai chung
    'chán', 'dở', 'tệ', 'buồn', 'xấu', 'lag', 'rác', 'nhạt', 'phế', 'cứt', 'đần', 
    'ghét', 'phẫn nộ', 'kém', 'thất vọng', 'xàm', 'bịp', 'lừa', 'dislike', 'tắt',
    'ồn', 'đau', 'kém', 'xấu', 'kinh', 'phí', 'tiếc',
            
    # Slang tiêu cực/Chửi bới
    'ngu', 'óc', 'trẩu', 'súc vật', 'chó', 'điên', 'khùng', 'biến',
    'nhảm', 'xàm xí', 'xàm lờ', 'câu view', 'câu like', 'bú fame', 'lố', 'ô dề',
    'giả trân', 'flop', 'xu cà na', 'toxic', 'hãm',
            
    # Phản đối/Kỹ thuật
    'phản đối', 'tẩy chay', 'xóa', 'report', 'mờ', 'giật', 'quảng cáo', 'spam', 
    'không hay', 'phí tiền', 'phí thời gian', 'đừng xem', 'đổ lỗi', 'xúc phạm IQ người xem',
    'não tàn', 'não', 'cũng chịu','làm ăn thế này', 'cẩu thả', 'nội dung thối não', 'chả khác gì coi thường'
]

TU_LOAI_BO_TIENG_VIET = {
    # 1. Từ hư từ/quan hệ từ cũ
    'là', 'và', 'của', 'thì', 'mà', 'có', 'nhưng', 'với', 'những', 'này', 
    'cho', 'được', 'cũng', 'đã', 'trong', 'để', 'các', 'một', 'làm', 'người',
    'tại', 'bởi', 'vì', 'rằng', 'nếu', 'dù', 'hoặc', 'tuy', 
    # Từ ngữ xưng hô/ngôi thứ 
    'em', 'anh', 'mình', 'bạn', 'tôi', 'tao', 'mày', 'nó', 'họ', 'chị', 'chú', 'bác',
    'admin', 'kênh', 'video', 'clip', 'xem', 'kênh', 'vid', 'tui', 'ad', 'ta',
            
    # Từ đệm cuối câu
    'ạ', 'ơi', 'nha', 'ôi', 'ủa', 'ae', 'nhé', 'nhỉ', 'ha', 'hả', 'hở', 'á', 'cơ', 
    'đâu', 'đấy', 'đó', 'kia', 'nọ', 'rồi', 'vậy', 'thôi', 'luôn', 'ngay',
            
    # 2. [QUAN TRỌNG] Bổ sung các từ rác từ Log của bạn
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
    
    # 4. Xóa ký tự kéo dài
    van_ban = re.sub(r'([a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ])\1{2,}', r'\1', van_ban)
    
    # 5. Tách từ
    cac_tu = van_ban.split()
    
    # 6. Chuẩn hóa Teencode
    cac_tu = [TU_DIEN_TEENCODE.get(tu, tu) for tu in cac_tu]
    
    # 7. [QUAN TRỌNG] Lọc Stopwords (Chỉ áp dụng cho WordCloud hoặc khi cần)
    if xoa_tu_loai_bo:
        cac_tu = [tu for tu in cac_tu if tu not in TU_LOAI_BO_TIENG_VIET and not tu.isdigit()] 
        
    van_ban = ' '.join(cac_tu)
    van_ban = re.sub(r'\s+', ' ', van_ban).strip()
    return van_ban

def phan_tich_cam_xuc_theo_luat(van_ban):
    van_ban_chu_thuong = van_ban.lower()
    diem_so = 0
    for tu in TU_KHOA_TICH_CUC:
        if tu in van_ban_chu_thuong: diem_so += 1
    for tu in TU_KHOA_TIEU_CUC:
        if tu in van_ban_chu_thuong: diem_so -= 1
        
    danh_sach_emoji = [bieu_tuong['emoji'] for bieu_tuong in emoji.emoji_list(van_ban)]
    bieu_tuong_tich_cuc = ['❤', '🥰', '😍', '👍', '😂', '🔥', '😘', '😊', '😁', '❤️', '💕', '😁', '👍', '🤣', '😆', '😋', '😎', '😚', '🤗', '🤑','🍀']
    bieu_tuong_tieu_cuc = ['💔', '👎', '😭', '😢', '😡', '🤬', '😞', '😒', '🤦‍♀️','🤦‍♂️','😑','🙄','😔','😓','☹️','🙁','😟','😰','😱','💀','☠️','💩','🙏']
    
    for bieu_tuong in danh_sach_emoji:
        if bieu_tuong in bieu_tuong_tich_cuc: diem_so += 1
        if bieu_tuong in bieu_tuong_tieu_cuc: diem_so -= 1

    if diem_so > 0: return "Positive"
    if diem_so < 0: return "Negative"
    return "Neutral"

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