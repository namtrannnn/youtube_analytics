"""
Các hàm tiện ích chung
"""
import re
from datetime import timedelta
from collections import Counter

def get_safe_attr(item, key):
    """Lấy thuộc tính an toàn"""
    try:
        return item[key]
    except:
        return getattr(item, key, 0)

def format_timestamp(seconds):
    """Chuyển giây thành định dạng HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))[2:]

def clean_text_basic(text):
    """Làm sạch text cơ bản - xóa nhãn âm thanh, ký hiệu thừa"""
    # Xóa nhãn âm thanh nền dạng [âm nhạc], [vỗ tay], [cười], [Music]...
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    # Xóa ký hiệu >> của transcript tự động (speaker diarization)
    text = re.sub(r'>>\s*', '', text)
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_video_id(url):
    """Trích xuất video ID từ URL YouTube"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def reconstruct_sentences(transcript_data, silence_threshold=0.5, video_type='default'):
    """
    Nối các dòng subtitle rời rạc thành câu hoàn chỉnh
    dựa trên khoảng lặng giữa các từ
    """
    if not transcript_data:
        return []
    
    sentences = []
    current_text = ""
    current_start = get_safe_attr(transcript_data[0], 'start')
    
    for i in range(len(transcript_data) - 1):
        curr_item = transcript_data[i]
        next_item = transcript_data[i+1]
        
        text = clean_text_basic(get_safe_attr(curr_item, 'text'))
        if not text:
            continue
        
        current_text += " " + text
        
        curr_end = get_safe_attr(curr_item, 'start') + get_safe_attr(curr_item, 'duration')
        next_start = get_safe_attr(next_item, 'start')
        gap = next_start - curr_end
        
        # Điều kiện ngắt câu
        is_end_punct = text[-1] in '.!?'
        is_long = len(current_text.split()) > 50
        is_pause = gap > silence_threshold
        
        if is_pause or is_end_punct or is_long:
            clean = current_text.strip()
            if clean:
                clean = clean[0].upper() + clean[1:]
                sentences.append({
                    'text': clean,
                    'start': current_start,
                    'end': curr_end,
                    'words': clean.lower().split()
                })
            
            current_text = ""
            current_start = next_start
    
    return sentences

def clean_sentence(text, lang='vi'):
    """Làm sạch câu văn để tóm tắt"""
    # Danh sách từ cần xóa đầu câu
    prefixes = {
        'vi': ['và', 'thì', 'mà', 'nhưng', 'nên', 'rồi', 'còn', 'vì', 'nếu', 'khi', 'lúc'],
        'en': ['and', 'but', 'so', 'then', 'well', 'now', 'because', 'if', 'when']
    }
    
    prefix_list = prefixes.get(lang, prefixes['en'])
    
    # Xóa từ nối đầu câu
    for prefix in prefix_list:
        pattern = r'^' + re.escape(prefix) + r'\s+'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Xóa các cụm từ dư thừa
    junk_patterns = [
        r'^(Mình|Tôi|Bạn|Anh chị|Các bạn|Cô chú)\s+(nghĩ|thấy|nói|cho|dùng|sử dụng)\s+',
        r'\s+(nha|nè|nhé|nhá|ạ|dạ|à|ha)\s*$',
        r'^(Ừ|Ờ|À|Um|Uh|Er)\s+',
    ]
    
    for pattern in junk_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Xóa dấu câu cuối
    text = re.sub(r'[.!?]+$', '', text)
    
    # Viết hoa chữ cái đầu
    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    
    return text

def get_word_frequency(sentences, stop_words):
    """Tính tần suất từ trong danh sách câu"""
    all_words = []
    for sent in sentences:
        all_words.extend([
            w for w in sent['words'] 
            if w not in stop_words and w.isalnum() and len(w) > 2
        ])
    return Counter(all_words)

def truncate_text(text, max_words=100):
    """Cắt ngắn text theo số từ"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def merge_consecutive_duplicates(items, similarity_func, threshold=0.6):
    """
    Gộp các item liên tiếp có nội dung tương tự
    similarity_func: hàm tính độ tương đồng giữa 2 items
    """
    if len(items) <= 1:
        return items
    
    merged = [items[0]]
    
    for i in range(1, len(items)):
        current = items[i]
        previous = merged[-1]
        
        similarity = similarity_func(current, previous)
        
        if similarity < threshold:
            merged.append(current)
    
    return merged

def extract_numbers_with_units(text, pattern):
    """Trích xuất số liệu kèm đơn vị từ text"""
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [f"{num} {unit}" for num, unit in matches]

def find_keyword_contexts(text, keywords, context_size=3):
    """
    Tìm ngữ cảnh xung quanh keyword (lấy N từ trước và sau)
    """
    words = text.lower().split()
    contexts = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        try:
            idx = words.index(keyword_lower)
            start = max(0, idx - context_size)
            end = min(len(words), idx + context_size + 1)
            context = ' '.join(words[start:end])
            contexts.append(context)
        except ValueError:
            continue
    
    return contexts

def clean_text_advanced(text):
    """Làm sạch văn bản subtitle (xóa từ rác, chuẩn hóa)"""
    if not text:
        return ""
    
    # 1. Xóa ký tự rác
    text = re.sub(r'>>|--|\.\.|__', ' ', text)
    
    # 2. Xóa từ lặp ("rồi rồi rồi" -> "rồi")
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    
    # 3. Xóa từ rác đầu câu
    trash_starts = ['và', 'thì', 'mà', 'rồi', 'à', 'ừ']
    text = re.sub(r'^(' + '|'.join(trash_starts) + r')\s+', '', text, flags=re.IGNORECASE)
    
    # 4. Xóa từ rác cuối câu
    trash_ends = ['nha', 'nhé', 'nè', 'ha', 'á', 'luôn', 'thiệt', 'mọi người']
    text = re.sub(r'\s+(' + '|'.join(trash_ends) + r')\s*$', '', text, flags=re.IGNORECASE)
    
    # 5. Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 6. Viết hoa chữ cái đầu
    if text:
        text = text[0].upper() + text[1:]
    
    return text

def is_valid_sentence(text):
    """Kiểm tra câu có hợp lệ không"""
    if not text:
        return False
    
    words = text.split()
    
    # Quá ngắn
    if len(words) < 4:
        return False
    
    # Kiểm tra tỉ lệ từ viết hoa (tránh TITLE CASE)
    upper_count = sum(1 for w in words if w and w[0].isupper())
    if len(words) > 5 and upper_count / len(words) > 0.8:
        return False
    
    return True