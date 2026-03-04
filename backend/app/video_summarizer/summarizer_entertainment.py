"""
Module tóm tắt video giải trí chung (Entertainment)
Xử lý các video không thuộc cooking/vlog/talkshow/news
Bao gồm: Review sản phẩm, Unboxing, Tutorial, Comedy, Gaming commentary, audio, sách nói, etc.
"""
import re

class EntertainmentSummarizer:
    def __init__(self, lang='vi'):
        self.lang = lang

        # Danh sách từ khóa báo hiệu câu mang lượng thông tin cao 
        self.INFO_KEYWORDS = [
            'review', 'đánh giá', 'trải nghiệm', 'ưu điểm', 'nhược điểm', 'so sánh', 'giá',
            'mở hộp', 'thiết kế', 'phụ kiện', 'màn hình', 'pin', 'cấu hình',
            'hướng dẫn', 'cách làm', 'bước', 'mẹo', 'lưu ý', 'cách',
            'cảm nhận', 'thử thách', 'bất ngờ', 'sốc', 'thấy',
            'hài', 'vui', 'troll', 'phạt', 'cười',
            'game', 'chơi', 'đấu', 'rank', 'map', 'hero', 'skin', 'chiêu',
            'quan trọng', 'đặc biệt', 'tuyệt vời', 'kết luận', 'tóm lại',
            'câu chuyện', 'nhân vật', 'thế giới', 'xảy ra'
        ]

    def summarize_chunk(self, sentences_chunk):
        """
        Trích xuất đại ý của một phân đoạn (chunk) video.
        Format tối giản, phổ quát cho mọi loại content.
        """
        if not sentences_chunk:
            return []

        # 1. Gộp và lọc bỏ các mảnh vỡ do lỗi ngắt timeline
        cleaned = self._clean_sentences(sentences_chunk)
        if not cleaned:
            return []

        # 2. Chấm điểm từng câu để tìm ra câu chứa đại ý
        scored_sentences = []
        for sent in cleaned:
            score = self._score_sentence(sent)
            if score > 0:
                scored_sentences.append((score, sent))

        # 3. Chọn lọc các câu đại diện
        if not scored_sentences:
            # Fallback: Lấy 2 câu có độ dài tốt nhất nếu không tìm được keyword
            cleaned.sort(key=lambda x: len(x.split()), reverse=True)
            top_sentences = cleaned[:2]
        else:
            # Lấy top 3 câu có điểm cao nhất
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [sent for score, sent in scored_sentences[:3]]

        # 4. Khôi phục lại thứ tự gốc của các câu để đọc đúng luồng logic
        final_sentences = [sent for sent in cleaned if sent in top_sentences]

        # 5. Format lại kết quả thành các gạch đầu dòng
        result = []
        for sent in final_sentences:
            clean_pt = self._format_point(sent)
            if clean_pt:
                result.append(f"{clean_pt}")

        return result

    def _clean_sentences(self, sentences_chunk):
        """
        [ĐÃ NÂNG CẤP]: Gộp text để trị tận gốc lỗi ASR bị cắt vụn ngang xương
        """
        # 1. Trích xuất toàn bộ text từ chunk và gộp thành 1 đoạn văn duy nhất
        raw_texts = []
        for item in sentences_chunk:
            text = item['text'] if isinstance(item, dict) else str(item)
            raw_texts.append(text.strip())
            
        full_text = " ".join(raw_texts)
        
        # Sửa lỗi dính khoảng trắng
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # 2. Tách văn bản thành các câu thật sự dựa vào dấu chấm, chấm hỏi, chấm than
        # Sử dụng lookbehind (?<=[.!?]) để không làm mất dấu câu khi tách
        real_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if s.strip()]

        cleaned = []
        JUNK_PATTERNS = [
            r'^(xin chào|chào|hello|hi|hey)\b',
            r'^(subscribe|like|share|follow|đăng ký|theo dõi|bấm chuông|để lại bình luận)\b',
            r'^(cảm ơn|thank|thanks)\s+(các bạn|mọi người|anh em)\b',
            r'^(à|ừ|ờ|uh|um|well|dạ|vâng|rồi|thì|ok|okay)\s*,?\s*$'
        ]

        for text in real_sentences:
            # 3. CHẶN ĐỨNG mảnh vỡ: Bỏ qua các câu/cụm từ bị cắt vụn (dưới 4 từ)
            # Giúp loại bỏ những từ rác như "Phố.", "Tích phân.", "Lên vai họ." ở đầu/cuối timeline
            if len(text.split()) < 4:
                continue
                
            if any(re.search(p, text.lower()) for p in JUNK_PATTERNS):
                continue
            
            cleaned.append(text)
            
        return cleaned

    def _score_sentence(self, sentence):
        """Chấm điểm câu dựa trên mật độ thông tin"""
        score = 0
        sent_lower = sentence.lower()
        words = sent_lower.split()
        word_count = len(words)

        # Tiêu chí 1: Độ dài lý tưởng (ưu tiên câu từ 10 - 35 từ, không quá ngắn, không lê thê)
        if 10 <= word_count <= 35:
            score += 2
        elif 35 < word_count <= 50:
            score += 1

        # Tiêu chí 2: Chứa từ khóa mang thông tin
        for kw in self.INFO_KEYWORDS:
            if kw in sent_lower:
                score += 2
                
        # Tiêu chí 3: Chứa số liệu (Rất quan trọng cho truyện/review/hướng dẫn)
        if re.search(r'\d+', sent_lower):
            score += 1

        return score

    def _format_point(self, text):
        """Format dọn rác văn bản thành một ý gọn gàng"""
        text = re.sub(r'^(và|thì|mà|nhưng|rồi|thế|vậy|ừ|à|nói chung là|tóm lại là|thực ra thì)\s*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(nhé|nhá|nha|nhen|đó|đấy|ạ|nữa cơ)\s*$', '', text, flags=re.IGNORECASE)
        text = text.strip()
        
        if text:
            # Viết hoa chữ cái đầu tiên
            text = text[0].upper() + text[1:]
            # Thêm dấu chấm kết câu nếu thiếu
            if text[-1] not in '.!?':
                text += '.'
                
        return text