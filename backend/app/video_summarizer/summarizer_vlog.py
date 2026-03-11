"""
Module tóm tắt vlog - Dùng geo_database để nhận diện địa điểm chính xác
"""
import re
from .config import PATTERNS
from .geo_database import find_locations_in_text


class VlogSummarizer:
    def __init__(self, lang='vi'):
        self.lang = lang
        self.patterns = PATTERNS['vlog'].get(lang, PATTERNS['vlog']['vi'])

        self.bad_starters = {
            'thì', 'là', 'mà', 'nhưng', 'rồi', 'vậy', 'à', 'ừ',
            'kiểu', 'tại', 'xong', 'và', 'nên', 'hay', 'hoặc'
        }
        self.junk_markers = {
            'sao trời', 'được không', 'phải không', 'đúng không',
            'nhỉ', 'ha', 'hả', 'hở', 'á', 'cơ', 'à', 'vậy'
        }

    def summarize_chunk(self, sentences_chunk):
        if not sentences_chunk:
            return []

        # 1. Làm sạch câu
        clean_sentences = []
        for s in sentences_chunk:
            text = self._clean_noise(s['text'])
            if not self._is_junk_sentence(text) and len(text.split()) >= 5:
                clean_sentences.append(text)

        full_text = ' '.join(clean_sentences)

        # 2. Tìm địa điểm bằng geo_database (CHÍNH XÁC)
        locations = find_locations_in_text(full_text)

        # 3. Tìm nội dung chính
        top_segments = self._find_best_segments(clean_sentences)

        # 4. Tổng hợp
        summary = []

        if locations:
            summary.append(f"Đang ở: {locations[0]}")

        count = 0
        for seg in top_segments:
            if count >= 2:
                break
            summary.append(f"{seg}")
            count += 1

        return summary

    def _clean_noise(self, text):
        """Dọn rác trong text"""
        text = re.sub(r'>>+', '', text)
        text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
        fillers = [
            r'\bthì là\b', r'\bkiểu là\b', r'\bnghĩa là\b',
            r'\bnhư là\b', r'\bà ờ\b', r'\bxong rồi\b'
        ]
        for pattern in fillers:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            text = text[0].upper() + text[1:]
        return text

    def _is_junk_sentence(self, text):
        """Kiểm tra câu rác"""
        text_lower = text.lower()
        if any(
            text_lower.endswith(m + '.') or text_lower.endswith(m)
            for m in self.junk_markers
        ):
            return True
        words = text_lower.split()
        if len(words) < 6 and any(
            w in words for w in ['wow', 'trời', 'ghê', 'kìa', 'đi', 'ôi']
        ):
            return True
        if text.replace('.', '').isdigit():
            return True
        return False

    def _find_best_segments(self, sentences):
        """Tìm câu có nội dung hay nhất"""
        keywords = [
            'đi', 'đến', 'thấy', 'nhìn', 'ăn', 'ngon', 'đẹp',
            'núi', 'sông', 'hồ', 'đường', 'tàu', 'xe', 'lạnh',
            'nắng', 'mưa', 'giá', 'mua', 'bán', 'quán', 'chợ',
            'biển', 'rừng', 'thác', 'hang'
        ]
        scored = []
        for i, current in enumerate(sentences):
            combined = current
            if i + 1 < len(sentences):
                combined = f"{current} {sentences[i+1]}"

            score = 0
            text_lower = combined.lower()
            score += sum(2 for k in keywords if k in text_lower)
            if any(c.isdigit() for c in combined):
                score += 1
            first_word = combined.split()[0].lower()
            if first_word in self.bad_starters:
                score -= 2
            words = combined.split()
            if len(words) < 10:
                score -= 3
            if len(words) > 40:
                score -= 1

            if score > 0:
                scored.append((score, self._polish_sentence(combined)))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, text in scored:
            if not any(self._is_overlap(text, r) for r in results):
                results.append(text)
        return results

    def _polish_sentence(self, text):
        """Làm đẹp câu"""
        words = text.split()
        while words and words[0].lower() in self.bad_starters:
            words.pop(0)
        text = ' '.join(words)
        if text:
            text = text[0].upper() + text[1:]
        return text

    def _is_overlap(self, s1, s2):
        """Kiểm tra 2 câu trùng nội dung"""
        w1 = set(s1.lower().split())
        w2 = set(s2.lower().split())
        if not w1 or not w2:
            return False
        return len(w1 & w2) / min(len(w1), len(w2)) > 0.6