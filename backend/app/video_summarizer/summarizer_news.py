"""
Module tóm tắt video tin tức (News) - V17 (Look-ahead Deduplication)
Khắc phục triệt để việc in ra các câu "Điểm tin đầu giờ/Teaser" bị trùng lặp với tin chi tiết phía sau.
"""
import re

class NewsSummarizer:
    def __init__(self, lang='vi'):
        self.lang = lang
        
        self.INVESTIGATIVE_THEMES = {
            'damage': ['thiệt hại', 'đầu tư', 'vốn', 'triệu', 'tỷ', 'củ giống', 'cành', 'mất trắng', 'phế phẩm', 'nạn nhân'],
            'method': ['thủ đoạn', 'tinh vi', 'camera', 'ban đêm', 'ghen ăn tức ở', 'đố kỵ', 'phá hoại', 'xuống tay', 'hiện trường', 'hung khí'],
            'consequence': ['nợ nần', 'uy tín', 'thương lái', 'sợ hãi', 'bất an', 'thức đêm', 'khó khăn', 'tuyệt vọng', 'bức xúc', 'ảnh hưởng'],
            'legal': ['luật sư', 'pháp luật', 'chế tài', 'truy cứu', 'hình sự', 'năm tù', 'phạt tù', 'đền bù', 'công an', 'cơ quan chức năng', 'xử lý', 'bản án', 'tòa án', 'khởi tố']
        }
        
        self.BULLETIN_SIGNALS = {
            'verbs': ['cho biết', 'thông báo', 'tuyên bố', 'khẳng định', 'phát hiện', 'ghi nhận', 'xảy ra', 'tổ chức', 'khai mạc', 'bốc cháy', 'thu hút', 'xử lý', 'trải nghiệm', 'tham quan', 'đón', 'khai hội', 'khởi tố', 'bắt giữ', 'tạm giữ', 'cứu hộ'],
            'entities': ['bộ', 'sở', 'công an', 'ủy ban', 'chính phủ', 'chuyên gia', 'đại diện', 'cục', 'cảnh sát', 'bệnh viện', 'cơ quan', 'lực lượng', 'du khách', 'bảo tàng'],
            'locations': ['tại', 'ở', 'khu vực', 'thành phố', 'tỉnh', 'huyện', 'xã', 'phường', 'quốc gia', 'trên địa bàn'],
            'times': ['hôm nay', 'hôm qua', 'sáng nay', 'chiều nay', 'tối qua', 'vừa qua', 'mới đây', 'ngày', 'tháng', 'năm nay'],
            'critical': ['khởi tố', 'bắt giữ', 'tai nạn', 'tử vong', 'bị thương', 'thiệt hại', 'vi phạm', 'ma túy', 'cấp cứu', 'án mạng']
        }

    def summarize_video(self, all_sentences):
        if not all_sentences: return []
        cleaned_sentences = self._clean_and_merge(all_sentences)
        if not cleaned_sentences: return []

        news_type = self._detect_news_type(cleaned_sentences)

        if news_type == 'bulletin':
            return self._process_bulletin(cleaned_sentences)
        else:
            return self._process_investigative(cleaned_sentences)

    def _is_fluff_or_interview(self, sent):
        sent_lower = sent.lower().strip()
        if re.search(r'^(tôi|mình|chúng tôi|em|cháu|mới đầu thì|ở đây có|thì đây|thực sự thì|cũng có bàn|bọn mình|anh em|bỏ một khúc|nếu mà không)\b', sent_lower): return True
        if re.search(r'\b(cảm thấy|nghĩ là|thấy là|mong là|ấn tượng với|chia sẻ|cảm ơn|xúc động|ngạc nhiên|hy vọng|tâm lý rất là|rất là thích)\b', sent_lower): return True
        if re.search(r'\b(tưởng tượng|nhát dao|băng hoại|đạo đức|nước mắt|đau đớn|xót xa|rợn người|pho tượng|oan nghiệt|tàn nhẫn)\b', sent_lower): return True
        
        descriptive_words = r'\b(vẻ đẹp|thiên nhiên|mộng mơ|rung cảm|cảm hứng|rộn ràng|hứa hẹn|bất tận|cần mẫn|bền bỉ|nguyên sơ|nguyên bản|đại ngàn|chú ngựa|khẽ cọ mũi|đáng yêu)\b'
        if re.search(descriptive_words, sent_lower):
            has_news_verb = any(v in sent_lower for v in ['cho biết', 'thông báo', 'ghi nhận', 'xảy ra', 'tổ chức', 'duy trì', 'đảm bảo'])
            if not has_news_verb: return True
                
        return False

    def _score_bulletin_starter(self, sent):
        sent_lower = sent.lower()
        if self._is_fluff_or_interview(sent): return -100
        if len(sent.split()) < 6: return -100
        
        score = 0
        if any(v in sent_lower for v in self.BULLETIN_SIGNALS['verbs']): score += 2
        if any(e in sent_lower for e in self.BULLETIN_SIGNALS['entities']): score += 2
        if any(l in sent_lower for l in self.BULLETIN_SIGNALS['locations']): score += 1
        if any(t in sent_lower for t in self.BULLETIN_SIGNALS['times']): score += 1
        if re.search(r'\d+\s*(người|triệu|tỷ|ca|vụ|chiếc|đồng|%|km|giờ|trường hợp)\b', sent_lower): score += 2
        if any(kw in sent_lower for kw in self.BULLETIN_SIGNALS['critical']): score += 3
        return score

    def _detect_news_type(self, sentences):
        headline_count = sum(1 for s in sentences if self._score_bulletin_starter(s) >= 4)
        if headline_count >= 4: return 'bulletin'
        return 'investigative'

    def _get_core_vocab(self, text):
        words = re.findall(r'\b[a-zđàáảãạâầấẩẫậăằắẳẵặeèéẻẽẹêềếểễệiìíỉĩịoòóỏõọôồốổỗộơờớởỡợuùúủũụưừứửữựyỳýỷỹỵ]{4,}\b', text.lower())
        stopwords = {'trong', 'không', 'những', 'người', 'được', 'rằng', 'theo', 'nhưng', 'cũng', 'một', 'nhiều', 'hơn', 'đang', 'công', 'quan', 'cơ', 'cảnh', 'sát'}
        return set(w for w in words if w not in stopwords)

    def _get_location_names(self, text):
        words = text.split()
        locs = set()
        indicators = {'tỉnh', 'phường', 'huyện', 'xã', 'quận', 'thành', 'tại', 'ở', 'đảo', 'quốc'}
        for i, w in enumerate(words):
            clean_w = w.lower().strip(',.:')
            if clean_w in indicators and i + 1 < len(words):
                next_word = words[i+1].strip(',.:')
                if next_word and next_word[0].isupper():
                    locs.add(next_word)
        return locs

    def _process_bulletin(self, sentences):
        news_blocks = []
        current_block = []
        current_vocab = set()
        current_locations = set()
        
        hard_break_pattern = r'^(hôm qua|hôm nay|sáng nay|chiều nay|tối qua|mới đây|còn tại|theo\s+(cục|bộ|sở|ủy|cơ quan|đại diện)|tại\s+(phường|xã|quận|huyện|tỉnh|thành phố|thủ đô|quốc gia|cảng|vùng|làng)|cơ quan cảnh sát|công an tỉnh|lực lượng chức năng)\b'
        continuation_pattern = r'^(trong quá trình|qua test nhanh|sau đó|bằng các biện pháp|hiện vụ|hiện tại|trước đó|cơ quan công an cũng|các nạn nhân|theo hồ sơ|tổng thống)\b'

        for sent in sentences:
            score = self._score_bulletin_starter(sent)
            if score <= 0: continue
                
            sent_vocab = self._get_core_vocab(sent)
            sent_locations = self._get_location_names(sent)
            
            is_hard_break = re.search(hard_break_pattern, sent.lower().strip())
            is_continuation = re.search(continuation_pattern, sent.lower().strip())
            
            vocab_overlap = current_vocab.intersection(sent_vocab)
            location_overlap = current_locations.intersection(sent_locations)
            
            if not current_block:
                current_block.append(sent)
                current_vocab.update(sent_vocab)
                current_locations.update(sent_locations)
            else:
                should_break = False
                if not is_continuation:
                    if is_hard_break:
                        should_break = True
                    elif len(vocab_overlap) == 0 and len(location_overlap) == 0:
                        should_break = True
                    elif score >= 4 and sent_locations and current_locations and len(location_overlap) == 0:
                        should_break = True

                if should_break:
                    news_blocks.append(current_block)
                    current_block = [sent]
                    current_vocab = set(sent_vocab)
                    current_locations = set(sent_locations)
                else:
                    if len(current_block) < 6:
                        current_block.append(sent)
                        current_vocab.update(sent_vocab)
                        current_locations.update(sent_locations)
                    else:
                        news_blocks.append(current_block)
                        current_block = [sent]
                        current_vocab = set(sent_vocab)
                        current_locations = set(sent_locations)
                        
        if current_block:
            news_blocks.append(current_block)
            
        # =========================================================================
        # BƯỚC MỚI: XÓA BỎ CÁC TIN MÀO ĐẦU (TEASERS) TRÙNG LẶP VỚI TIN CHÍNH
        # =========================================================================
        deduped_blocks = []
        for i, block in enumerate(news_blocks):
            is_teaser = False
            # Các câu mào đầu thường chỉ là đoạn ngắn 1-2 câu
            if len(block) <= 2:
                block_vocab = self._get_core_vocab(" ".join(block))
                # Quét các tin ở phía sau video
                for later_block in news_blocks[i+1:]:
                    later_vocab = self._get_core_vocab(" ".join(later_block))
                    overlap = block_vocab.intersection(later_vocab)
                    
                    # Nếu trùng >= 3 từ khóa quan trọng -> Chắc chắn đây là mào đầu của tin phía sau
                    if len(overlap) >= 3 or (len(block_vocab) > 0 and len(overlap) / len(block_vocab) >= 0.6):
                        is_teaser = True
                        break
            
            if not is_teaser:
                deduped_blocks.append(block)
                
        # =========================================================================
        # FORMAT KẾT QUẢ ĐẦU RA
        # =========================================================================
        result = ["[TỔNG HỢP] TỔNG HỢP CÁC THÔNG TIN ĐÁNG CHÚ Ý\n"]
        valid_paras = []
        
        for block in deduped_blocks:
            if any(self._score_bulletin_starter(s) >= 4 for s in block):
                clean_sents = [self._format_final_sentence(s) for s in block]
                
                first_sent = clean_sents[0]
                first_sent = re.sub(r'^(Hiện vụ án đang tiếp tục được điều tra làm rõ)\s*\.?\s*', '', first_sent, flags=re.IGNORECASE)
                if first_sent: 
                    first_sent = first_sent[0].upper() + first_sent[1:]
                clean_sents[0] = first_sent
                
                if "".join(clean_sents).strip():
                    valid_paras.append(" ".join(clean_sents))
                
        if not valid_paras:
            result.append("> *(Không trích xuất được thông tin cụ thể từ video này)*")
        else:
            for item in valid_paras: 
                result.append(f"{item}\n")
                
        return "\n".join(result)

    def _process_investigative(self, sentences):
        buckets = {'headline': None, 'damage': [], 'method': [], 'consequence': [], 'legal': []}
        seen_signatures = set()
        buckets['headline'] = self._extract_investigative_headline(sentences)

        for sent in sentences:
            if self._is_fluff_or_interview(sent): continue
            
            sent_lower = sent.lower()
            if len(sent.split()) < 10: continue
            sig = ' '.join(sent.split()[:5]).lower()
            if sig in seen_signatures: continue

            scores = {theme: sum(1 for kw in kws if kw in sent_lower) for theme, kws in self.INVESTIGATIVE_THEMES.items()}
            best_theme = max(scores, key=scores.get)
            
            if scores[best_theme] >= 1:
                clean_txt = self._format_final_sentence(sent)
                buckets[best_theme].append((clean_txt, scores[best_theme]))
                seen_signatures.add(sig)

        for theme in ['damage', 'method', 'consequence', 'legal']:
            buckets[theme].sort(key=lambda x: x[1], reverse=True)
            buckets[theme] = [item[0] for item in buckets[theme][:3]] 

        return self._render_investigative_markdown(buckets)

    def _extract_investigative_headline(self, sentences):
        for sent in sentences[:15]: 
            if self._is_fluff_or_interview(sent): continue
            
            score = 0
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in ['vụ việc', 'phá hoại', 'thiệt hại', 'bức xúc', 'nghiêm trọng']): score += 2
            if any(kw in sent_lower for kw in ['nông dân', 'gia đình', 'nạn nhân', 'người dân']): score += 1
            if len(sent.split()) >= 15: score += 1
            if score >= 3: return self._format_final_sentence(sent)
        return "Ghi nhận vụ việc gây thiệt hại và bức xúc trong dư luận."

    def _render_investigative_markdown(self, buckets):
        summary = ["[TÓM TẮT] TÓM TẮT CHUYÊN SÂU (PHÓNG SỰ)\n"]
        if buckets['headline']: summary.append(f"**[TIÊU ĐIỂM] TIÊU ĐIỂM:** {buckets['headline']}\n")
        
        if buckets['damage']:
            summary.append("**[NẠN NHÂN] Nạn nhân & Thiệt hại:**")
            summary.extend([f"* {item}" for item in buckets['damage']])
            summary.append("")
        if buckets['method']:
            summary.append("**[DIỄN BIẾN] Diễn biến & Nhận định:**")
            summary.extend([f"* {item}" for item in buckets['method']])
            summary.append("")
        if buckets['consequence']:
            summary.append("**[HẬU QUẢ] Hậu quả & Hệ lụy:**")
            summary.extend([f"* {item}" for item in buckets['consequence']])
            summary.append("")
        if buckets['legal']:
            summary.append("**[PHÁP LÝ] Góc độ pháp lý & Xử lý:**")
            summary.extend([f"* {item}" for item in buckets['legal']])
            
        return "\n".join(summary)

    def _clean_and_merge(self, sentences_raw):
        cleaned = []
        filler_patterns = [
            r'^(xin chào|chào mừng|kính chào|thưa quý vị|quý vị ơi|nhở).*?[\.\?!,]\s*',
            r'(đăng ký|subscribe|like|share|follow|bấm|nhấn|theo dõi|chuông|kênh|bình luận phía dưới)',
            r'(tuyên bố chính thức|miễn trừ trách nhiệm|quan hệ ngoại giao)'
        ]
        
        for item in sentences_raw:
            text = item['text'] if isinstance(item, dict) else str(item)
            text = text.strip()
            
            if any(re.search(p, text, re.IGNORECASE) for p in filler_patterns): continue
            if not text or len(text.split()) < 4: continue

            text = re.sub(r'^(Và|Nhưng|Vậy mà|Thế nhưng|Thưa quý vị|Liệu)\s*,?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^(Tiếp theo.*?chương trình|Chuyển sang.*?tin tức|Tiếp theo.*?quốc tế|Một thông tin.*?khác|Thưa quý vị|Thưa các bạn|Cũng trong ngày|Bên cạnh đó|Tuy nhiên|Vâng)\s*,?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^(của chương trình|trong chương trình hôm nay)\s*,?\s*', '', text, flags=re.IGNORECASE)
            
            if text: text = text[0].upper() + text[1:]
            cleaned.append(text)

        full_text = " ".join(cleaned)
        proper_sentences = re.split(r'(?<=[.!?])\s+', full_text)
        return [s.strip() for s in proper_sentences if len(s.split()) >= 6]

    def _format_final_sentence(self, text, max_words=None):
        text = text.strip()
        if not text: return ""
        text = text[0].upper() + text[1:]
        if text[-1] not in ['.', '!', '?']: return text + '.'
        return text