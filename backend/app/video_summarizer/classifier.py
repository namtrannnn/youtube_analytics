"""
Module phân loại video - Phân biệt "dạy nấu" vs "vlog ẩm thực"
"""
import re
from .config import VIDEO_CATEGORIES


class VideoClassifier:
    """Phân loại video để chọn phương pháp tóm tắt phù hợp"""

    def __init__(self):
        self.categories = VIDEO_CATEGORIES

    def classify(self, video_info):
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        category_id = video_info.get('category_id', '')
        transcript_sample = video_info.get('transcript_sample', '').lower()

        combined_text = f"{title} {description} {transcript_sample}"

        # 1. Không hỗ trợ
        if self._is_unsupported(category_id, combined_text):
            return 'unsupported'

        # 2. DETECTION ĐẶC BIỆT: Story/Audio/Review → ENTERTAINMENT
        if self._is_story_or_audio(title, transcript_sample):
            return 'entertainment'
        
        if self._is_movie_review(title, description, transcript_sample):
            return 'entertainment'

        # 3. Tính điểm
        scores = {'cooking': 0, 'vlog': 0, 'talkshow': 0, 'news': 0, 'entertainment': 0}

        # Điểm từ category_id
        for cat_name, cat_config in self.categories.items():
            if cat_name == 'unsupported':
                continue
            if category_id in cat_config.get('ids', []):
                scores[cat_name] += 30

        # Điểm từ keywords config
        for cat_name, cat_config in self.categories.items():
            if cat_name == 'unsupported':
                continue
            for keyword in cat_config.get('keywords', []):
                if keyword in combined_text:
                    scores[cat_name] += 10

        # Điểm từ pattern đặc trưng (chỉ dùng title + description, không dùng transcript)
        title_desc = f"{title} {description}"
        scores['cooking'] += self._score_cooking(title_desc, transcript_sample)
        scores['vlog']    += self._score_vlog(title_desc, transcript_sample)
        scores['talkshow'] += self._score_talkshow(title_desc, transcript_sample)
        scores['news']    += self._score_news(title_desc, transcript_sample)

        # 4. RULE ƯU TIÊN: Phân biệt "dạy nấu" vs "vlog ẩm thực"
        # Nếu cooking đang thắng, kiểm tra xem có phải vlog ẩm thực không
        best = max(scores, key=scores.get)

        if best == 'cooking':
            if self._is_food_vlog(title, description, transcript_sample):
                # Là vlog ẩm thực → Chuyển sang vlog
                scores['vlog'] += 50
                best = 'vlog'

        elif best == 'vlog':
            if self._is_cooking_tutorial(title, description, transcript_sample):
                # Là video dạy nấu → Chuyển sang cooking
                scores['cooking'] += 50
                best = 'cooking'

        if scores[best] < 10:
            return 'entertainment'

        return best

    # ─────────────────────────────────────────────
    # DETECTION ĐẶC BIỆT: STORY/AUDIO/REVIEW
    # ─────────────────────────────────────────────
    
    def _is_story_or_audio(self, title, transcript):
        """
        Phát hiện video kể chuyện/đọc truyện/audio book:
        - Title có "truyện", "audio", "đọc truyện", "văn án"
        - Transcript có dấu hiệu tường thuật: "tôi", "cô ta", "anh ta", "họ" + động từ quá khứ
        """
        # Check title
        story_keywords = [
            'truyện', 'audio', 'audiobook', 'đọc truyện', 'kể chuyện',
            'văn án', 'tiểu thuyết', 'novel', 'short story'
        ]
        if any(kw in title for kw in story_keywords):
            return True
        
        # Check transcript - Dấu hiệu kể chuyện
        # 1. Có nhiều đại từ nhân vật
        pronouns = len(re.findall(r'\b(tôi|cô ta|anh ta|họ|nó|cô ấy|anh ấy|chúng)\b', transcript))
        
        # 2. Có động từ quá khứ
        past_verbs = len(re.findall(r'\b(đã|đã từng|vừa|từng|đang|bỗng|bỗng nhiên|lập tức|ngay lập tức)\b', transcript))
        
        # 3. Có từ tường thuật
        narrative_words = len(re.findall(
            r'\b(nói|bảo|hỏi|trả lời|nghĩ|nhìn|thấy|cảm thấy|biết|quay đầu|bước vào|đứng dậy|ngồi xuống)\b', 
            transcript
        ))
        
        # 4. KHÔNG có tín hiệu video thật (camera, hình ảnh, ghi hình)
        real_video_signals = len(re.findall(
            r'\b(các bạn|mọi người|chúc|subscribe|like|share|theo dõi|đăng ký|xem|mình|nhé|nhá)\b',
            transcript
        ))
        
        # Nếu có nhiều dấu hiệu tường thuật và ít tín hiệu video thật → Đây là audio/story
        if pronouns > 10 and narrative_words > 15 and real_video_signals < 5:
            return True
        
        return False
    
    def _is_movie_review(self, title, description, transcript):
        """
        Phát hiện video review/tóm tắt phim:
        - Title có "review phim", "tóm tắt phim", "spoil", "recap"
        - Transcript có cốt truyện: nhân vật, tên người, hành động liên tục
        """
        # Check title
        review_keywords = [
            'review phim', 'review film', 'tóm tắt phim', 'spoil phim',
            'recap', 'phim hay', 'giải thích phim', 'phân tích phim',
            'cái kết', 'kết thúc', 'ending explained'
        ]
        if any(kw in title or kw in description for kw in review_keywords):
            return True
        
        # Check transcript - Dấu hiệu review phim
        # 1. Có tên nhân vật (chữ in hoa đầu + không phải từ thường)
        character_names = len(re.findall(r'\b[A-Z][a-z]+\b', transcript))
        
        # 2. Có từ liên quan phim
        movie_terms = len(re.findall(
            r'\b(nhân vật|diễn viên|đạo diễn|phim|movie|film|tập|season|trailer|cảnh|plot|twist)\b',
            transcript
        ))
        
        # 3. Có hành động liên tục (dấu hiệu kể cốt truyện)
        action_verbs = len(re.findall(
            r'\b(phát hiện|quyết định|cố gắng|tìm cách|bắt đầu|kết thúc|xuất hiện|biến mất|chạy trốn|tìm kiếm|giết|cứu|chiến đấu)\b',
            transcript
        ))
        
        # Nếu có nhiều dấu hiệu → review phim
        if (character_names > 5 and movie_terms > 3) or action_verbs > 10:
            return True
        
        return False

    # ─────────────────────────────────────────────
    # RULE PHÂN BIỆT CHÍNH
    # ─────────────────────────────────────────────

    def _is_cooking_tutorial(self, title, description, transcript):
        """
        Phát hiện video DẠY NẤU ĂN thật sự:
        - Title có "cách làm", "hướng dẫn nấu", "recipe", "công thức"
        - Transcript có nhiều định lượng (g, kg, muỗng canh...)
        - Transcript dạy step-by-step (ướp, xào, chiên theo thứ tự)
        """
        # Tín hiệu mạnh nhất: title/desc có từ "dạy nấu"
        STRONG_COOKING_TITLE = [
            'cách làm', 'cách nấu', 'hướng dẫn nấu', 'hướng dẫn làm',
            'công thức', 'recipe', 'how to cook', 'how to make',
            'dạy nấu', 'bí quyết nấu', 'mẹo nấu',
        ]
        for kw in STRONG_COOKING_TITLE:
            if kw in title or kw in description:
                return True

        # Tín hiệu trong transcript: nhiều định lượng + động từ nấu
        qty_count = len(re.findall(
            r'\d+\s*(g|kg|ml|l|muỗng|thìa|chén|gram|lít|củ|con|quả|cái|gói)',
            transcript, re.IGNORECASE
        ))
        cook_verbs = len(re.findall(
            r'\b(ướp|xào|chiên|luộc|hấp|kho|rim|nêm|cho vào|thêm vào|trộn đều|bóp đều)\b',
            transcript, re.IGNORECASE
        ))

        if qty_count >= 3 and cook_verbs >= 4:
            return True

        return False

    def _is_food_vlog(self, title, description, transcript):
        """
        Phát hiện VLOG ẨM THỰC (đi ăn, review quán, khám phá món):
        - Title có "review", "thử", "ăn thử", "đi ăn", "khám phá"
        - Transcript nói về ĐỊA ĐIỂM, trải nghiệm ăn uống, không dạy nấu
        - Có từ "quán", "nhà hàng", "tiệm", "order", "gọi món"
        """
        # Tín hiệu mạnh: title/desc có từ review ẩm thực
        STRONG_FOOD_VLOG_TITLE = [
            'review', 'thử', 'ăn thử', 'đi ăn', 'khám phá',
            'food tour', 'ẩm thực', 'street food', 'quán ngon',
            'nhà hàng', 'món ngon', 'địa điểm ăn', 'quán ăn',
            'vlog', 'du lịch ẩm thực',
        ]
        for kw in STRONG_FOOD_VLOG_TITLE:
            if kw in title or kw in description:
                return True

        # Tín hiệu trong transcript: nói về địa điểm, order, trải nghiệm
        FOOD_VLOG_TRANSCRIPT = [
            r'\b(quán|nhà hàng|tiệm|hàng|xe)\b',
            r'\b(order|gọi món|thực đơn|menu)\b',
            r'\b(đi đến|ghé|tới|đến)\b',
            r'\b(view|không gian|decor|trang trí)\b',
            r'\b(giá|bao nhiêu tiền|đắt|rẻ|hợp lý)\b',
            r'\b(ngon|dở|tệ|ổn|tuyệt)\b.{0,20}\b(quán|nhà hàng|nơi)\b',
        ]
        vlog_signals = sum(
            1 for p in FOOD_VLOG_TRANSCRIPT
            if re.search(p, transcript, re.IGNORECASE)
        )

        # Kiểm tra transcript THIẾU từ dạy nấu
        tutorial_signals = len(re.findall(
            r'\b(ướp|nêm|cho vào|thêm vào|bóp đều|trộn đều)\b',
            transcript, re.IGNORECASE
        ))

        # Là food vlog nếu có nhiều tín hiệu vlog và ít tín hiệu dạy nấu
        if vlog_signals >= 3 and tutorial_signals < 3:
            return True

        return False

    # ─────────────────────────────────────────────
    # SCORE FUNCTIONS
    # ─────────────────────────────────────────────

    def _score_cooking(self, title_desc, transcript):
        score = 0
        patterns = [
            r'\d+\s*(g|kg|ml|muỗng|thìa|chén|gram)',
            r'(cách làm|cách nấu|recipe|công thức)',
            r'(nguyên liệu|ingredients|gia vị)',
            r'(nấu|xào|chiên|luộc|kho|rim)',
        ]
        for p in patterns:
            score += len(re.findall(p, title_desc + ' ' + transcript, re.IGNORECASE)) * 5
        return score

    def _score_vlog(self, title_desc, transcript):
        score = 0
        # Chỉ tính điểm khi có từ ĐI/ĐẾN thật sự (không phải kể chuyện, tường thuật)
        patterns = [
            r'(vlog|daily vlog|travel vlog)',
            r'(tham quan|khám phá|du lịch|visit|travel)',
            r'(địa điểm|nhà hàng|restaurant)',
            r'(cùng mình|follow me|theo dõi)',
        ]
        for p in patterns:
            score += len(re.findall(p, title_desc + ' ' + transcript, re.IGNORECASE)) * 5

        # Giảm điểm nếu transcript có nhiều từ talkshow/interview
        talkshow_clues = len(re.findall(
            r'(chương trình|khán giả|câu hỏi|phỏng vấn|chia sẻ|anh mc|mc|show|talkshow|host)',
            transcript, re.IGNORECASE
        ))
        score -= talkshow_clues * 4

        return max(score, 0)

    def _score_talkshow(self, title_desc, transcript):
        score = 0
        patterns = [
            r'(podcast|interview|phỏng vấn|talk show|talkshow)',
            r'(chia sẻ|thảo luận|discuss)',
            r'(quan điểm|ý kiến|opinion)',
            r'(chủ đề|topic|vấn đề)',
        ]
        for p in patterns:
            score += len(re.findall(p, title_desc + ' ' + transcript, re.IGNORECASE)) * 5

        # Tín hiệu mạnh trong transcript: dẫn chương trình, hỏi đáp
        strong_talkshow = len(re.findall(
            r'(chương trình|khán giả|câu hỏi tiếp theo|bây giờ hỏi|anh mc|quý vị|xin mời|xin hỏi|thử thách)',
            transcript, re.IGNORECASE
        ))
        score += strong_talkshow * 8

        # Tín hiệu hỏi đáp qua lại
        qna_signals = len(re.findall(
            r'(em nghĩ|em thấy|theo em|theo anh|theo chị|đúng không ạ|vâng ạ|dạ ạ)',
            transcript, re.IGNORECASE
        ))
        score += qna_signals * 3

        return score

    def _score_news(self, title_desc, transcript):
        score = 0
        patterns = [
            r'(tin tức|thời sự|news|breaking)',
            r'(báo cáo|report|thông tin)',
            r'(mới nhất|latest|update)',
        ]
        for p in patterns:
            score += len(re.findall(p, title_desc + ' ' + transcript, re.IGNORECASE)) * 5
        return score

    def _is_unsupported(self, category_id, text):
        unsupported = self.categories['unsupported']
        if category_id in unsupported['ids']:
            return True
        for keyword in unsupported['keywords']:
            if keyword in text:
                return True
        return False

    def get_config(self, video_type):
        return self.categories.get(video_type, {})