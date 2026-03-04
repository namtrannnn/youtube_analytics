"""
Module chia câu dài thành nhiều câu nhỏ có timestamp
Dùng cho các video mà transcript là 1 câu liên tục không có dấu câu
"""
import re


def needs_splitting(sentences, min_sentences=5, max_words_per_sentence=100):
    """
    Phát hiện transcript cần chia câu
    
    Returns True nếu:
    - Số câu quá ít (< min_sentences)
    - Có câu quá dài (> max_words_per_sentence từ)
    """
    if len(sentences) < min_sentences:
        return True
    
    for sent in sentences:
        if len(sent['text'].split()) > max_words_per_sentence:
            return True
    
    return False


def clean_sentence_tail(text):
    """
    Xóa các từ nối thừa ở CUỐI câu sau khi chia
    
    Ví dụ:
    "Mình ướp 30 phút rồi mình quay lại mình đi Chiên được rồi đó Còn nếu như mà"
    → "Mình ướp 30 phút rồi mình quay lại mình đi Chiên được"
    """
    if not text:
        return text
    
    # Danh sách các từ/cụm từ thừa ở cuối câu
    # Sắp xếp từ DÀI đến NGẮN để ưu tiên match cụm dài hơn
    TAIL_PATTERNS = [
        # Cụm từ nối dài
        r'\s+còn nếu như mà$',
        r'\s+nếu như mà$',
        r'\s+còn nếu mà$',
        r'\s+còn nếu như$',
        r'\s+cho nên là$',
        r'\s+bây giờ tiếp theo$',
        r'\s+tiếp theo là$',
        r'\s+sau khi mình$',
        r'\s+trước khi mình$',
        r'\s+để cho nó$',
        r'\s+để cho$',
        r'\s+để mình$',
        r'\s+hoặc là$',
        r'\s+hoặc là hạt$',
        r'\s+cho nên$',
        r'\s+mà các bạn$',
        r'\s+thì mình$',
        r'\s+thì các bạn$',
        r'\s+thì anh chị$',
        r'\s+đó các bạn$',
        r'\s+thì đó$',
        r'\s+cũng được$',
        r'\s+cũng vậy$',
        r'\s+như mà$',
        r'\s+nếu mà$',
        # Từ đơn thừa ở cuối
        r'\s+nếu$',
        r'\s+mà$',
        r'\s+thì$',
        r'\s+á$',
        r'\s+ha$',
        r'\s+nha$',
        r'\s+nè$',
        r'\s+nhé$',
        r'\s+ạ$',
        r'\s+à$',
        r'\s+ơi$',
        r'\s+nhỉ$',
        r'\s+vậy$',
        r'\s+đó$',
        r'\s+rồi$',
        r'\s+xong$',
        r'\s+thôi$',
        r'\s+luôn$',
        r'\s+vô$',
        r'\s+là$',
        r'\s+và$',
        r'\s+với$',
        r'\s+trong$',
        r'\s+của$',
        r'\s+các$',
        r'\s+một$',
        r'\s+cho$',
    ]
    
    # Áp dụng lặp đi lặp lại cho đến khi không còn gì để xóa
    cleaned = text.strip()
    changed = True
    while changed:
        changed = False
        for pattern in TAIL_PATTERNS:
            new_text = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
            if new_text != cleaned:
                cleaned = new_text
                changed = True
    
    return cleaned


def split_sentences_with_timestamps(sentences, video_type='default'):
    """
    Chia các câu dài thành nhiều câu nhỏ, giữ timestamp tỉ lệ.
    video_type: 'talkshow' dùng thuật toán chia theo câu hỏi/trả lời
    """
    if video_type == 'talkshow':
        return _split_talkshow(sentences)
    return _split_default(sentences)


def _split_talkshow(sentences):
    """
    Chia câu cho talkshow: giữ câu hỏi và câu trả lời đi cùng nhau.
    Không cắt cứng 25 từ — mục tiêu là ~60-80 từ mỗi chunk có nghĩa.
    """
    result = []

    # Từ nghi vấn đánh dấu bắt đầu câu hỏi mới
    QUESTION_STARTERS = [
        r'\b(bây giờ hỏi|hỏi bạn|câu hỏi|xin hỏi)\b',
        r'\b(đâu là|tại sao|vì sao|như thế nào|thế nào)\b',
        r'\b(bao giờ|khi nào|ai là|ai sẽ|điều gì)\b',
    ]

    for sent in sentences:
        text = sent['text']
        start = sent['start']
        end = sent.get('end', start + 5)
        duration = end - start

        # Câu ngắn hoặc vừa → giữ nguyên
        if len(text.split()) <= 60:
            result.append(sent)
            continue

        # Câu dài → chia tại điểm bắt đầu câu hỏi mới hoặc dấu chấm hỏi
        combined = '|'.join(QUESTION_STARTERS)
        # Điểm cắt: trước câu hỏi mới (giữ câu hỏi + trả lời cùng nhau)
        break_points = [0]
        for m in re.finditer(r'[.!?]\s+', text):
            break_points.append(m.end())
        break_points.append(len(text))

        # Ghép thành chunks ~50-80 từ
        chunks = []
        buffer = ''
        for i in range(len(break_points) - 1):
            segment = text[break_points[i]:break_points[i+1]].strip()
            if not segment:
                continue
            candidate = (buffer + ' ' + segment).strip() if buffer else segment
            if len(candidate.split()) >= 50 and buffer:
                chunks.append(buffer)
                buffer = segment
            else:
                buffer = candidate

        if buffer:
            if chunks and len(buffer.split()) < 15:
                chunks[-1] = chunks[-1] + ' ' + buffer
            else:
                chunks.append(buffer)

        # Nếu không chia được, giữ nguyên
        if len(chunks) <= 1:
            result.append(sent)
            continue

        # Gán timestamp tỉ lệ
        total_words = sum(len(c.split()) for c in chunks)
        current_start = start
        for chunk in chunks:
            wc = len(chunk.split())
            chunk_duration = duration * (wc / total_words) if total_words > 0 else 5.0
            chunk_end = current_start + chunk_duration
            clean = clean_sentence_tail(chunk)
            if clean and len(clean.split()) >= 5:
                result.append({
                    'text': clean,
                    'start': round(current_start, 2),
                    'end': round(chunk_end, 2),
                    'words': clean.lower().split()
                })
            current_start = chunk_end

    return result


def _split_default(sentences):
    """Thuật toán chia câu gốc (dùng cho cooking/vlog)"""
    result = []
    
    for sent in sentences:
        text = sent['text']
        start = sent['start']
        end = sent.get('end', start + 5)
        duration = end - start
        
        # Câu ngắn (≤ 40 từ) → Giữ nguyên
        if len(text.split()) <= 40:
            result.append(sent)
            continue
        
        # Câu dài → Chia nhỏ
        sub_texts = _split_text_to_chunks(text, target_words=25)
        
        if len(sub_texts) <= 1:
            result.append(sent)
            continue
        
        # Chia cứng thêm nếu sub vẫn > 35 từ
        final_subs = []
        for sub in sub_texts:
            sub = sub.strip()
            if not sub or len(sub.split()) < 5:
                continue
            if len(sub.split()) > 35:
                words = sub.split()
                for i in range(0, len(words), 25):
                    chunk = ' '.join(words[i:i+25])
                    if chunk and len(chunk.split()) >= 5:
                        final_subs.append(chunk)
            else:
                final_subs.append(sub)
        
        if not final_subs:
            result.append(sent)
            continue
        
        # Gán timestamp tỉ lệ theo số từ
        total_words = sum(len(s.split()) for s in final_subs)
        current_start = start
        
        for sub in final_subs:
            wc = len(sub.split())
            sub_duration = duration * (wc / total_words) if total_words > 0 else 5.0
            sub_end = current_start + sub_duration
            
            # Dọn đuôi câu thừa
            sub_clean = clean_sentence_tail(sub)
            
            # Bỏ qua nếu sau khi dọn quá ngắn
            if sub_clean and len(sub_clean.split()) >= 4:
                result.append({
                    'text': sub_clean,
                    'start': round(current_start, 2),
                    'end': round(sub_end, 2),
                    'words': sub_clean.lower().split()
                })
            current_start = sub_end
    
    return result


def _split_text_to_chunks(text, target_words=25):
    """
    Chia text thành các đoạn ~25 từ
    Hai bước: (1) chia theo từ nối tự nhiên, (2) chia cứng nếu vẫn dài
    """
    BREAK_PATTERNS = [
        r'(?<=\s)(ha|nha|nè|đó|rồi|luôn|thôi|được|xong|nhé|ạ)\s+',
        r'[.!?]+\s+',
        r'\bvà\s+(?=\w)',
        r'\bthì\s+(?=mình|anh|chị|các bạn|bây giờ)',
        r'\bcòn\s+(?=nếu|mình|anh|chị)',
        r'\bbây giờ\s+',
        r'\btiếp theo\s+',
        r'\bsau khi\s+',
        r'\btrước khi\s+',
    ]
    combined = '|'.join(BREAK_PATTERNS)
    
    # Tìm điểm cắt
    split_points = [0]
    for match in re.finditer(combined, text):
        split_points.append(match.end())
    split_points.append(len(text))
    
    raw_chunks = []
    for i in range(len(split_points) - 1):
        chunk = text[split_points[i]:split_points[i+1]].strip()
        if chunk:
            raw_chunks.append(chunk)
    
    # Chia cứng nếu không chia được
    if len(raw_chunks) <= 1:
        words = text.split()
        return [' '.join(words[i:i+target_words]) for i in range(0, len(words), target_words)]
    
    # Ghép các đoạn quá ngắn, sau đó chia cứng nếu đoạn quá dài
    final_chunks = []
    buffer = ""
    
    for chunk in raw_chunks:
        buffer = (buffer + " " + chunk).strip() if buffer else chunk
        
        if len(buffer.split()) >= target_words:
            # Nếu buffer quá dài (>50 từ), chia cứng
            if len(buffer.split()) > 50:
                words = buffer.split()
                for i in range(0, len(words), target_words):
                    sub = ' '.join(words[i:i+target_words])
                    if sub:
                        final_chunks.append(sub)
            else:
                final_chunks.append(buffer)
            buffer = ""
    
    # Phần còn lại
    if buffer:
        if len(buffer.split()) > 50:
            words = buffer.split()
            for i in range(0, len(words), target_words):
                sub = ' '.join(words[i:i+target_words])
                if sub:
                    final_chunks.append(sub)
        elif final_chunks and len(buffer.split()) < 8:
            final_chunks[-1] += " " + buffer
        else:
            final_chunks.append(buffer)
    
    return final_chunks