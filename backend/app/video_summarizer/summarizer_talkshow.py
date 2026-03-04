import re

class TalkshowSummarizer:
    def __init__(self, lang='vi'):
        self.lang = lang
        
        self.END_CONNECTORS = ['và', 'thì', 'là', 'của', 'nhưng', 'mà', 'để', 'với', 
                               'trong', 'rằng', 'nếu', 'làm', 'bị', 'được', 'ở', 'như']
        self.HANGING_WORDS = ['hành', 'bàn', 'giải', 'bóng', 'thi', 'cầu', 'huấn', 
                              'đồng', 'đội', 'huy', 'trận', 'lưới', 'pha', 'lễ', 'nhân', 'ngày', 'tháng', 'năm']
        self.START_DEPENDENTS = ['của', 'trình', 'thắng', 'đấu', 'đá', 'viên', 'luyện', 'trương', 'tình']

        self.ANSWER_STARTERS = [
            'Dạ', 'Vâng', 'Đối với em', 'Đối với anh', 'Đối với mình',
            'Thì đối với', 'Thì em', 'Thì anh', 'Thì mình',
            'Em nghĩ', 'Em thấy', 'Em cảm', 'Mình nghĩ', 'Tôi nghĩ',
            'Hiện tại', 'Thực ra', 'Lúc đó', 'Khi đó', 'Hồi đó',
            'Theo em', 'Theo anh', 'Với em', 'Với anh', 'Ờ thật sự', 'Thật sự là',
            'Vì', 'Bởi vì', 'Tại vì', 'Là do', 'Là vì',
            'Lời đầu tiên', 'Đầu tiên', 'Thực sự', 'Cá nhân em', 'Thú thật', 'Cho em', 'Cho phép em'
        ]

        self.PERSONAL_STARTERS = (
            'em ', 'anh ', 'mình ', 'dạ ', 'vâng ', 'tôi ', 'bọn em ', 'chúng em ',
            'thì em', 'thì anh', 'thì mình', 
            'đối với em', 'đối với anh',
            'thật sự thì em', 'thật sự em',
            'ờ em', 'ờ anh', 'ờ mình', 
            'ừ em', 'à em', 'vì em', 'tại em',
            'lời đầu tiên', 'cho em', 'cho phép em', 'khi mà', 'lúc đó'
        )

    def summarize_video(self, all_sentences):
        if not all_sentences: return ""
        merged  = self._preprocess_merge(all_sentences)
        cleaned = self._split_and_clean(merged)
        return self._build_qa_format(cleaned)

    def _preprocess_merge(self, raw_sentences):
        if not raw_sentences: return []
        merged_list = []
        current_text = raw_sentences[0]['text'] if isinstance(raw_sentences[0], dict) else raw_sentences[0]

        for i in range(1, len(raw_sentences)):
            next_text = raw_sentences[i]['text'] if isinstance(raw_sentences[i], dict) else raw_sentences[i]
            if self._should_merge(current_text, next_text):
                current_text += " " + next_text
            else:
                merged_list.append(current_text)
                current_text = next_text

        merged_list.append(current_text)
        return merged_list

    def _should_merge(self, text_a, text_b):
        words_a = text_a.strip().split()
        words_b = text_b.strip().split()
        if not words_a or not words_b: return False

        last_a  = words_a[-1].lower().rstrip('.,!?')
        first_b = words_b[0].lower().rstrip('.,!?')

        if last_a in self.END_CONNECTORS or last_a in self.HANGING_WORDS: return True
        if first_b in self.START_DEPENDENTS: return True

        if not text_a.strip()[-1] in ['.', '?', '!']:
            next_lower = text_b.lower()
            starts_new_sentence = next_lower.startswith(('đây có', 'vậy', 'rồi', 'sau đó', 'thế', 'và', 'còn', 'lời đầu tiên', 'cho em'))
            if not starts_new_sentence:
                return True

        return False

    def _split_and_clean(self, text_list):
        final_list = []
        
        # [ĐÃ ĐỒNG BỘ MÁY CHÉM] Thêm các từ khóa thời gian, kể chuyện và chuyển ý
        guest_splitters = [
            r'dạ\b', r'vâng\b', r'lời đầu tiên\b', r'đối với em\b', r'đối với anh\b', r'đối với mình\b',
            r'theo em\b', r'theo anh\b', r'cá nhân em\b', r'với em\b', r'với anh\b', r'với mình\b',
            r'em nghĩ\b', r'em thấy\b', r'thú thật\b', r'thật sự\b', r'trước đây\b', r'hồi đó\b', r'lúc đó\b'
        ]
        
        mc_splitters = [
            r'à rồi\b', r'rồi cảm ơn\b', r'thế còn\b', r'vậy còn\b', r'bây giờ\b',
            r'và đúng là\b', r'vậy thì\b', r'như vậy\b', r'đúng là\b', r'vậy\b',
            r'cảm ơn hai\b', r'cảm ơn sự\b', r'tiếp theo\b', r'trở lại với\b', 
            r'đến với\b', r'qua hai\b', r'để khép lại\b', r'chúng ta tiếp tục\b'
        ]
        
        split_pat = '|'.join(guest_splitters + mc_splitters)
        aggressive_split_regex = fr'(?<=[^\s])\s+(?=(?:{split_pat})\b)'

        for text in text_list:
            text = re.sub(r'^(xin chào|chào mừng).*?(?=\s*(và\s+|hôm nay|gương mặt|cầu thủ|chúng ta|talk show))', '', text, flags=re.IGNORECASE).strip()
            if not text: continue

            parts = re.split(aggressive_split_regex, text, flags=re.IGNORECASE)
            real_parts = [p for p in parts if p and len(p.strip()) > 1]
            if not real_parts: real_parts = [text]

            for p in real_parts:
                p = p.strip()
                if not p: continue

                chunks = self._split_answer_from_mc(p)
                for chunk in chunks:
                    chunk = chunk.strip()
                    if not chunk: continue
                    
                    chunk = chunk[0].upper() + chunk[1:]
                    if len(chunk.split()) > 2:
                        final_list.append(chunk)
                        
        return final_list

    def _split_answer_from_mc(self, text):
        VIETHOA = re.compile(r'[A-ZĐÀÁẢÃẠĂẮẶẲẴẤẦẨẪẬÊẾỀỆỂỄÔỐỒỘỔỖƠỚỜỢỞỠƯỨỪỰỬỮ]')
        sentence_end = re.compile(r'([.!]|ạ[.,]?)\s+(?=' + VIETHOA.pattern + r')')
        PERSONAL_PRONOUNS = {'em', 'anh', 'mình', 'tôi', 'bọn', 'chúng'}

        results = []
        last_cut = 0

        for m in sentence_end.finditer(text):
            before = text[last_cut:m.end()].strip()
            cut_pos = m.end()
            remainder = text[cut_pos:]
            
            before_words = before.lower().split()
            remainder_words = remainder.lower().split()

            starts_personal = any(before.lower().startswith(p) for p in self.PERSONAL_STARTERS)
            contains_personal = any(w in PERSONAL_PRONOUNS for w in before_words[:5])
            before_is_personal = (starts_personal or contains_personal) and len(before_words) >= 4

            after_starts_personal = any(remainder.lower().startswith(p) for p in self.PERSONAL_STARTERS)
            after_contains_personal = any(w in PERSONAL_PRONOUNS for w in remainder_words[:20])
            after_is_personal = after_starts_personal or after_contains_personal

            after_long_enough = len(remainder_words) >= 4

            if before_is_personal and not after_is_personal and after_long_enough:
                results.append(before)
                last_cut = cut_pos

        tail = text[last_cut:].strip()
        if tail:
            results.append(tail)

        return results if len(results) > 1 else [text]

    def _is_lyrics(self, text):
        text_lower = text.lower()
        lyrics_patterns = [
            r'(chim|hoa|gió|mây|trăng|mưa|sao)\s+.{10,}\s+(cô đơn|yêu|thương|buồn|xa)',
            r'(tim|lòng|tâm)\s+.{10,}\s+(đau|buồn|vui|mừng)',
            r'(áo|kinh|phong)\s+.{5,}\s+(hình|xương|cô đơn)'
        ]
        return any(re.search(p, text_lower) for p in lyrics_patterns)

    def _is_question_aggressive(self, text):
        text_lower = text.lower().strip()
        
        guest_patterns = r'^\s*(rồi\s*|à\s*|ừ\s*|thì\s*|nhưng mà\s*|và\s*|dạ\s*|vâng\s*)?(với em|với anh|với mình|theo em|theo anh|theo mình|đối với em|đối với mình|đối với anh|cá nhân|lời đầu tiên|thú thật|thật sự|em nghĩ|em thấy|em cảm|khi mà|lúc đó|thì em|bọn em|tại vì)\b'
        
        storytelling = [
            r'\bem (hỏi|nói|thấy|nhớ|cảm thấy|bảo|nghĩ là)\b', 
            r'\banh (hỏi|nói|bảo|thấy)\b', 
            r'\bmình (hỏi|nói|nghĩ|bảo)\b'
        ]
        
        if re.search(guest_patterns, text_lower) or any(re.search(p, text_lower) for p in storytelling):
            return False

        BAD_ENDINGS = ['vâng?', 'như thế nào?', 'cảm thấy như thế nào?']
        if any(text_lower.endswith(b) for b in BAD_ENDINGS): 
            return False

        STRONG_STARTERS = [
            'tại sao', 'vì sao', 'đâu là', 'đâu sẽ là', 'ai là', 
            'điều gì', 'cái gì', 'bao giờ', 'khi nào', 
            'thế thì'
        ]
        if any(text_lower.startswith(s) for s in STRONG_STARTERS): 
            return True

        PATS = [
            r'^(vậy|thế|rồi|còn)\s+(thì|là|bây giờ|giờ)\s+.*\?$', 
            r'\bhay\s+(là\s+)?.*\s+(thôi|không|nhỉ|chứ|nhờ)\??$', 
            r'\bđã\s+.+\s+hay\s+(là\s+)?',
            r'\bcó\s+.+\s+(không|chưa|nhỉ|chăng)\??$',
            r'\bcó\s+.+\s+(gì|nào)\s+(không|chưa)',
            r'\bliệu\s+.+\s+có\s+', 
            r'\bđã\s+.+\s+chưa\??$', 
            r'\bthì sao\??',
            r'\bđâu là\s*(nhỉ|vậy|hả)?\??$', 
            r'\bđâu sẽ là\b', 
            r'\bbao nhiêu\s*(nhỉ|vậy|hả)?\??$',
            r'\blàm thế nào\b',
            r'\bnhư thế nào\b',
            r'\bra sao\b', 
            r'\bnhững\s+.+\s+(gì)\??$', 
            r'\bcụ thể là gì\b',
            r'\bVậy thì\b', 
            r'\blà gì\b',
            r'\bnhỉ\??$', 
            r'\bsao\??$', 
            r'\bhả\??$',
            r'\bđúng không\b.*?\??$', 
            r'\bphải không\b.*?\??$'
        ]

        if text.endswith('?'):
            if len(text.split()) < 20:
                return True

        for p in PATS:
            if re.search(p, text_lower): 
                if "làm sao" in text_lower and not text_lower.startswith("làm sao"):
                    continue
                return True

        return False

    def _is_mc_transition(self, text):
        text_lower = text.lower().strip()
        core_text = re.sub(r'^(rồi\s*,?\s*|vâng\s*,?\s*|nhưng mà\s*,?\s*|vậy\s*,?\s*|thế thì\s*,?\s*|và\s*,?\s*)', '', text_lower).strip()
        
        mc_starters = [
            'cảm ơn hai', 'cảm ơn sự', 'và bây giờ', 'còn bây giờ', 'như vậy', 'tiếp theo', 
            'trở lại với', 'đến với', 'qua hai', 'để khép lại', 'xin nhờ', 
            'những người đồng đội', 'xin cảm ơn', 'kính chúc'
        ]
        if any(core_text.startswith(s) for s in mc_starters):
            if not any(p in core_text.split()[:8] for p in ['em', 'mình', 'tôi', 'bọn', 'chúng']):
                return True
                
        if re.search(r'\b(quý vị khán giả|hai bạn phúc|đức cả phúc|cả đức cả phúc|thử thách này|khép lại chương trình|khép lại cái chương trình|chiến binh trở về|xin giới thiệu|các bạn ấy không chỉ|rất tuyệt vời)\b', text_lower):
            return True
            
        return False

    def _build_qa_format(self, sentences):
        intro = []
        qa_pairs = []

        current_q = [] 
        current_a = []
        context_buffer = [] 
        state = 'INTRO'

        guest_check_pattern = r'^\s*(rồi\s*|à\s*|ừ\s*|thì\s*|nhưng mà\s*|và\s*)?(với em|với anh|với mình|theo em|theo anh|theo mình|đối với|cá nhân|dạ|vâng|lời đầu tiên|thú thật|thật sự|em nghĩ|em thấy|trước đây|hồi đó|lúc đó)'

        for text in sentences:
            if self._is_lyrics(text):
                continue
            
            is_q = self._is_question_aggressive(text)

            if is_q:
                # [ĐÃ SỬA CỘNG DỒN CÂU HỎI]: Chỉ lưu Q&A cũ nếu đã có câu trả lời
                if current_q and current_a:
                    if not self._is_question_aggressive(current_a[0]):
                        qa_pairs.append({'q': " ".join(current_q), 'a': current_a})
                    current_q = [] # Reset để đón block hỏi mới
                
                mc_context = []
                while context_buffer:
                    last_ctx = context_buffer[-1]
                    if not re.search(guest_check_pattern, last_ctx.lower()) and not any(p in last_ctx.lower().split()[:5] for p in ['em', 'mình', 'tôi']):
                        mc_context.insert(0, context_buffer.pop())
                    else:
                        break 
                
                q_text = text if text.endswith('?') else text + '?'
                
                # Nếu current_q đã có dữ liệu (MC đang hỏi liên tiếp), ta NỐI TIẾP vào
                if current_q and not current_a:
                    current_q.extend(mc_context + [q_text])
                else:
                    current_q = mc_context + [q_text]
                    
                current_a = []
                context_buffer = [] 
                state = 'QA'
                
            else:
                if state == 'INTRO':
                    if any(kw in text.lower() for kw in ['giới thiệu', 'khách mời', 'cùng đến với', 'chương trình', 'chào mừng']):
                        intro.append(text)
                    else:
                        context_buffer.append(text)
                        
                elif state == 'QA':
                    if self._is_mc_transition(text) and current_q:
                        if current_a:
                            qa_pairs.append({'q': " ".join(current_q), 'a': current_a})
                            current_q = []
                            current_a = []
                        context_buffer.append(text)
                        state = 'TRANSITION'
                    else:
                        current_a.append(text)
                        
                elif state == 'TRANSITION':
                    context_buffer.append(text)
                    if len(context_buffer) > 8:
                        context_buffer = context_buffer[-8:]

        if current_q and current_a:
            if not self._is_question_aggressive(current_a[0]):
                qa_pairs.append({'q': " ".join(current_q), 'a': current_a})

        # =====================================================================
        # RENDER OUTPUT KẾT QUẢ 
        # =====================================================================
        result = ["### 🎙️ TÓM TẮT TALKSHOW / PHỎNG VẤN\n"]

        if intro:
            result.append("**🌟 GIỚI THIỆU KHÁCH MỜI:**")
            clean_intro = [re.sub(r'^(Và|Nhưng|Thì|Vậy)\s+', '', s, flags=re.IGNORECASE) for s in intro[:3]]
            result.append(f"{' '.join(clean_intro)}\n")

        for pair in qa_pairs:
            if not pair['a']: continue

            full_answer_text = " ".join(pair['a']).lower()
            if not re.search(r'\b(em|anh|mình|tôi|bọn|chúng)\b', full_answer_text):
                continue
                
            first_ans_lower = pair['a'][0].lower()
            if re.search(r'\b(như vậy là|và đây chúng ta|những người đồng đội|để khép lại|cố tình để hiểu nhầm)\b', first_ans_lower):
                continue

            # [ĐÃ SỬA DỌN RÁC]: Xóa triệt để các cụm 1-2 từ (Vâng., À., Hôm nay.)
            raw_q = pair['q']
            q_parts = [p.strip() for p in raw_q.split('. ') if p.strip()]
            
            clean_q_parts = []
            for qp in q_parts:
                qp_clean = re.sub(r'^(Và|Nhưng|Vậy|Thế thì|Vâng|À rồi|À|Ừ|Như|Hôm nay|Rồi|Thì)\s*,?\s*', '', qp, flags=re.IGNORECASE).strip()
                # Chặn đứng các câu rác <= 2 từ KHÔNG chứa dấu hỏi chấm
                if len(qp_clean.split()) > 2 or '?' in qp_clean:
                    clean_q_parts.append(qp_clean)
            
            clean_q = '. '.join(clean_q_parts).strip()
            
            if clean_q.count('.') > 3:
                parts = clean_q.split('.')
                clean_q = '. '.join(parts[-4:]).strip() 
                
            if clean_q: 
                clean_q = clean_q[0].upper() + clean_q[1:]
                clean_q = re.sub(r'\s+\?', '?', clean_q)
                if not clean_q.endswith('?'): clean_q += '?'
                result.append(f"**❓ {clean_q}**")
            else:
                continue 
            
            first_ans = pair['a'][0]
            first_ans = re.sub(r'^(Dạ|Vâng|Thì|Ờ|À|Ừ|Thật sự thì)\s*,?\s*', '', first_ans, flags=re.IGNORECASE)
            if first_ans: 
                result.append(f"↳ {first_ans[0].upper() + first_ans[1:]}")

            for extra in pair['a'][1:6]:
                if len(extra.split()) >= 10:
                    extra_clean = re.sub(r'^(Có nghĩa là|Thì|Và|Tại vì|Nhưng mà)\s*,?\s*', '', extra, flags=re.IGNORECASE).strip()
                    if extra_clean:
                        extra_clean = extra_clean[0].upper() + extra_clean[1:]
                        result.append(f"{extra_clean}")
            
            result.append("") 

        if len(result) == 1:
            result.append("🔹 *(Không trích xuất được đoạn đối đáp cụ thể nào từ video này)*")

        return "\n".join(result)