"""
Module phân đoạn video động dựa trên độ tương đồng nội dung
Thay vì chia cứng mỗi 90s, ta chia khi nội dung thay đổi
"""
from collections import Counter

class DynamicSegmenter:
    """Phân đoạn timeline dựa trên thay đổi chủ đề"""
    
    def __init__(self, similarity_threshold=0.3, min_duration=60, max_duration=180):
        """
        Nới rộng thời gian để phù hợp với Vlog:
        - min_duration: 120s (2 phút) -> Giống cấu hình cũ bạn thấy ổn
        - max_duration: 400s (gần 7 phút) -> Cho phép các đoạn kể chuyện dài
        - similarity_threshold: 0.35 -> Giảm xuống để ít bị cắt vụn hơn
        """
        self.similarity_threshold = similarity_threshold
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def create_dynamic_segments(self, sentences, stop_words):
        """
        Tạo các segment động dựa trên thay đổi nội dung
        
        Returns:
            List[dict]: Mỗi dict chứa thông tin segment
        """
        if not sentences:
            return []
        
        segments = []
        current_segment = {
            'start': sentences[0]['start'],
            'end': sentences[0]['end'],
            'sentences': [sentences[0]],
            'keywords': self._extract_keywords([sentences[0]], stop_words)
        }
        
        for i in range(1, len(sentences)):
            curr_sent = sentences[i]
            
            # Tính độ tương đồng với segment hiện tại
            curr_keywords = self._get_sentence_keywords(curr_sent, stop_words)
            similarity = self._calculate_similarity(
                current_segment['keywords'],
                curr_keywords
            )
            
            # Tính thời lượng segment hiện tại
            current_duration = current_segment['end'] - current_segment['start']
            
            # Quyết định: Thêm vào segment hiện tại hay tạo segment mới?
            should_create_new = False
            
            # Điều kiện 1: Nội dung khác biệt (similarity thấp)
            if similarity < self.similarity_threshold:
                # Nhưng phải đảm bảo segment hiện tại đủ dài
                if current_duration >= self.min_duration:
                    should_create_new = True
            
            # Điều kiện 2: Segment hiện tại quá dài
            if current_duration >= self.max_duration:
                should_create_new = True
            
            if should_create_new:
                # Lưu segment hiện tại
                segments.append(current_segment)
                
                # Tạo segment mới
                current_segment = {
                    'start': curr_sent['start'],
                    'end': curr_sent['end'],
                    'sentences': [curr_sent],
                    'keywords': curr_keywords
                }
            else:
                # Mở rộng segment hiện tại
                current_segment['end'] = curr_sent['end']
                current_segment['sentences'].append(curr_sent)
                # Cập nhật keywords
                current_segment['keywords'] = self._extract_keywords(
                    current_segment['sentences'],
                    stop_words
                )
        
        # Thêm segment cuối
        if current_segment['sentences']:
            segments.append(current_segment)
        
        return segments
    
    def _extract_keywords(self, sentences, stop_words):
        """Trích xuất từ khóa từ danh sách câu"""
        all_words = []
        for sent in sentences:
            words = [
                w.lower() for w in sent['words']
                if w.lower() not in stop_words 
                and len(w) > 2 
                and w.isalnum()
            ]
            all_words.extend(words)
        
        # Đếm tần suất
        word_freq = Counter(all_words)
        
        # Lấy top keywords (xuất hiện >= 2 lần)
        keywords = [w for w, count in word_freq.most_common(10) if count >= 1]
        
        return set(keywords)
    
    def _get_sentence_keywords(self, sentence, stop_words):
        """Lấy keywords từ 1 câu"""
        words = [
            w.lower() for w in sentence['words']
            if w.lower() not in stop_words 
            and len(w) > 2 
            and w.isalnum()
        ]
        return set(words)
    
    def _calculate_similarity(self, keywords1, keywords2):
        """Tính độ tương đồng Jaccard giữa 2 tập keywords"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    

class TalkshowSegmenter:
    """
    Phân đoạn talkshow theo cấu trúc Q&A.
    Nguyên tắc: câu hỏi của MC + câu trả lời liền sau → 1 segment.
    Khi không có câu hỏi rõ ràng thì gộp theo thời gian ~60s.
    """

    def __init__(self, min_duration=45, max_duration=120):
        self.min_duration = min_duration
        self.max_duration = max_duration

        # Từ nghi vấn đánh dấu câu hỏi của MC
        self.QUESTION_SIGNALS = [
            'đâu là', 'tại sao', 'vì sao', 'như thế nào', 'thế nào',
            'bao giờ', 'khi nào', 'điều gì', 'ai là', 'ai sẽ',
            'câu hỏi', 'bây giờ hỏi', 'xin hỏi', 'cho biết',
            'chia sẻ về', 'đối với bạn', 'với bạn thì',
        ]

        # Câu hỏi xã giao nhỏ → không cắt segment ở đây
        self.TRIVIAL_QUESTIONS = [
            'đúng không', 'phải không', 'đúng rồi',
            'hay không', 'thật không', 'sao lại thế',
        ]

    def _is_real_question(self, text):
        """Câu hỏi thực chất của MC, không phải câu hỏi vặt"""
        t = text.lower()
        is_trivial = any(tq in t for tq in self.TRIVIAL_QUESTIONS)
        has_signal = any(qs in t for qs in self.QUESTION_SIGNALS)
        ends_q = t.strip().endswith('?')
        return has_signal and ends_q and not is_trivial

    def create_dynamic_segments(self, sentences, stop_words=None):
        """
        Tạo segment theo cấu trúc Q&A:
        - Phát hiện câu hỏi của MC
        - Gộp câu hỏi + tất cả câu trả lời tiếp theo (cho đến câu hỏi tiếp)
        - Segment tối đa max_duration giây
        """
        if not sentences:
            return []

        segments = []
        current = {
            'start': sentences[0]['start'],
            'end': sentences[0].get('end', sentences[0]['start'] + 5),
            'sentences': [sentences[0]],
            'has_question': self._is_real_question(sentences[0]['text']),
        }

        for i in range(1, len(sentences)):
            sent = sentences[i]
            s_start = sent['start']
            s_end = sent.get('end', s_start + 5)
            current_duration = s_start - current['start']
            is_new_question = self._is_real_question(sent['text'])

            # Điều kiện cắt segment mới:
            # 1. Câu hỏi mới của MC VÀ segment hiện tại đã đủ dài
            # 2. HOẶC segment quá dài (max_duration)
            should_cut = False

            if is_new_question and current_duration >= self.min_duration:
                should_cut = True
            elif current_duration >= self.max_duration:
                should_cut = True

            if should_cut:
                # Lưu segment cũ
                current['end'] = s_start
                segments.append(current)
                # Bắt đầu segment mới
                current = {
                    'start': s_start,
                    'end': s_end,
                    'sentences': [sent],
                    'has_question': is_new_question,
                }
            else:
                current['sentences'].append(sent)
                current['end'] = s_end

        # Lưu segment cuối
        if current['sentences']:
            segments.append(current)

        return segments