"""
Module tóm tắt chuyên biệt cho video nấu ăn - Phiên bản Fix lỗi nhận diện
"""
import re
# Import COOKING_INGREDIENTS từ config
from .config import PATTERNS, SUMMARY_TEMPLATES, STOP_WORDS, COOKING_INGREDIENTS
from .utils import clean_sentence, extract_numbers_with_units

class CookingSummarizer:
    """Tóm tắt video nấu ăn với trích xuất nguyên liệu, bước làm, lưu ý"""
    
    def __init__(self, lang='vi'):
        self.lang = lang
        self.patterns = PATTERNS['cooking'].get(lang, PATTERNS['cooking']['vi'])
        self.templates = SUMMARY_TEMPLATES['cooking'].get(lang, SUMMARY_TEMPLATES['cooking']['vi'])
        self.stop_words = STOP_WORDS.get(lang, STOP_WORDS['vi'])
        # Dùng set để tra cứu nhanh hơn
        self.ingredient_db = COOKING_INGREDIENTS
    
    def summarize_chunk(self, sentences_chunk):
        if not sentences_chunk:
            return []
        
        full_text = ' '.join([s['text'] for s in sentences_chunk])
        
        info = self._extract_cooking_info(sentences_chunk, full_text)
        summary_points = self._generate_summary(info)
        
        return summary_points
    
    def _extract_cooking_info(self, sentences, full_text):
        """Trích xuất thông tin nấu ăn"""
        info = {
            'ingredients': [],
            'quantities': [],
            'actions': [],
            'notes': [],
            '_sentences': sentences
        }
        
        # 1. Trích xuất số liệu
        quantities = extract_numbers_with_units(full_text, self.patterns['quantities'])
        info['quantities'] = list(set(quantities))[:10]  # Tăng lên 10
        
        # 2. Trích xuất nguyên liệu (Dựa trên từ điển - SỬA LỖI TẠI ĐÂY)
        info['ingredients'] = self._extract_ingredients_by_dict(full_text)
        
        # 3. Trích xuất hành động (Câu chứa động từ nấu nướng)
        info['actions'] = self._extract_actions(sentences)
        
        # 4. Trích xuất lưu ý
        info['notes'] = self._extract_notes(sentences)
        
        return info
    
    def _extract_ingredients_by_dict(self, text):
        """
        Trích xuất nguyên liệu bằng cách so khớp với từ điển COOKING_INGREDIENTS
        Thay thế hoàn toàn phương pháp đếm tần suất cũ.
        """
        found_ingredients = set()
        text_lower = text.lower()
        
        # Quét qua danh sách nguyên liệu chuẩn
        for item in self.ingredient_db:
            # Dùng regex \b để tìm từ chính xác (tránh tìm 'bò' trong 'từ bỏ')
            if re.search(r'\b' + re.escape(item) + r'\b', text_lower):
                found_ingredients.add(item)
                
        # Sắp xếp theo độ dài từ (để ưu tiên từ ghép dài hơn nếu cần hiển thị)
        # hoặc chỉ cần trả về list
        return list(found_ingredients)
    
    def _extract_actions(self, sentences):
        """Trích xuất câu hành động"""
        action_sentences = []
        action_words = self.patterns['actions']
        seen = set()
        
        for sent in sentences:
            text = sent['text']
            text_lower = text.lower()
            
            # Chỉ lấy câu chứa động từ nấu ăn
            if any(act in text_lower for act in action_words):
                # Làm sạch nhẹ
                clean = clean_sentence(text, self.lang)
                if clean not in seen and len(clean.split()) >= 5:
                    action_sentences.append(clean)
                    seen.add(clean)
                    
        return action_sentences
    
    def _extract_notes(self, sentences):
        """Trích xuất lưu ý"""
        notes = []
        note_keywords = self.patterns['notes']
        seen = set()
        
        for sent in sentences:
            text = sent['text']
            text_lower = text.lower()
            
            if any(kw in text_lower for kw in note_keywords):
                clean = clean_sentence(text, self.lang)
                if clean not in seen and len(clean.split()) >= 5:
                    notes.append(clean)
                    seen.add(clean)
        return notes
    
    def _generate_summary(self, info):
        """Sinh câu tóm tắt - Ghép định lượng vào nguyên liệu"""
        summary = []
        
        # 1. Ghép Nguyên liệu + Định lượng thành 1 dòng
        if info['ingredients'] or info['quantities']:
            # Thử ghép định lượng với nguyên liệu
            matched_items = self._match_quantities_to_ingredients(
                info['ingredients'], 
                info['quantities'], 
                info.get('_sentences', [])
            )
            
            if matched_items:
                summary.append(self.templates['ingredients'].format(items=matched_items))
        
        # 2. Hiển thị các bước thực hiện
        if info['actions']:
            for action in info['actions']:
                summary.append(self.templates['steps'].format(action=action))
        
        # 3. Hiển thị lưu ý
        if info['notes']:
            for note in info['notes']:
                summary.append(self.templates['note'].format(note=note))
        
        # Fallback: Nếu không trích xuất được gì
        if not summary and info.get('_sentences'):
            sorted_sents = sorted(info['_sentences'], key=lambda x: len(x['text']), reverse=True)
            for s in sorted_sents[:2]:
                summary.append(f"{s['text']}")
        
        return summary
    
    def _match_quantities_to_ingredients(self, ingredients, quantities, sentences):
        """
        Ghép định lượng với nguyên liệu thông minh
        
        Returns:
            str: "Thịt bò 1kg, Cà rốt 500g, Muối"
        """
        if not ingredients and not quantities:
            return None
        
        # Lấy full text
        if sentences:
            full_text = ' '.join([s['text'] for s in sentences])
        else:
            full_text = ''
        
        result_items = []
        matched_qty = set()
        
        # Duyệt qua từng nguyên liệu
        for ing in ingredients:
            # Tìm định lượng gần nguyên liệu này
            qty = self._find_quantity_near(ing, quantities, full_text)
            
            if qty:
                # Có định lượng → Ghép
                result_items.append(f"{ing.capitalize()} {qty}")
                matched_qty.add(qty)
            else:
                # Không có → Chỉ tên nguyên liệu
                result_items.append(ing.capitalize())
        
        # Thêm các định lượng chưa ghép (nếu còn)
        # NHƯNG bỏ qua thời gian/nhiệt độ
        invalid_units = ['tiếng', 'phút', 'giờ', 'độ', '°c', 'độ c']
        
        remaining = []
        for q in quantities:
            if q not in matched_qty:
                # Kiểm tra không phải thời gian/nhiệt độ
                q_lower = q.lower()
                if not any(unit in q_lower for unit in invalid_units):
                    remaining.append(q)
        
        if remaining:
            for qty in remaining[:2]:  # Tối đa 2 định lượng rời
                result_items.append(f"({qty})")
        
        return ', '.join(result_items) if result_items else None
    
    def _find_quantity_near(self, ingredient, quantities, text):
        """
        Tìm định lượng gần nguyên liệu nhất trong text
        CHỈ ghép định lượng có đơn vị khối lượng/thể tích, BỎ QUA thời gian/nhiệt độ
        """
        if not text or not quantities:
            return None
        
        text_lower = text.lower()
        ing_lower = ingredient.lower()
        
        # Lọc chỉ lấy định lượng CÓ ĐƠN VỊ PHÙ HỢP
        # Đơn vị phù hợp: g, kg, ml, l, muỗng, thìa, chén, cốc, gram, lít, củ, con, quả
        # BỎ QUA: tiếng, phút, giờ, độ, °C
        valid_quantities = []
        invalid_units = ['tiếng', 'phút', 'giờ', 'độ', '°c', 'độ c']
        
        for qty in quantities:
            qty_lower = qty.lower()
            # Kiểm tra không chứa đơn vị thời gian/nhiệt độ
            if not any(unit in qty_lower for unit in invalid_units):
                valid_quantities.append(qty)
        
        if not valid_quantities:
            return None
        
        # Tìm tất cả vị trí xuất hiện của nguyên liệu
        positions = []
        start = 0
        while True:
            idx = text_lower.find(ing_lower, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1
        
        if not positions:
            return None
        
        # Tìm định lượng GẦN NHẤT (trong valid_quantities)
        best_qty = None
        min_distance = float('inf')
        
        for pos in positions:
            # Lấy window xung quanh (±50 ký tự)
            window_start = max(0, pos - 50)
            window_end = min(len(text), pos + len(ingredient) + 50)
            window = text[window_start:window_end].lower()
            
            for qty in valid_quantities:
                qty_idx = window.find(qty.lower())
                if qty_idx != -1:
                    # Tính khoảng cách
                    distance = abs(qty_idx - (pos - window_start))
                    
                    # Ưu tiên định lượng TRƯỚC nguyên liệu ("1kg thịt bò")
                    if qty_idx < (pos - window_start):
                        distance *= 0.7
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_qty = qty
        
        # Chỉ trả về nếu đủ gần (< 40 ký tự)
        if min_distance < 40:
            return best_qty
        
        return None