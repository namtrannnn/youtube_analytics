"""
Hệ thống tóm tắt video YouTube thông minh (Backend Version)
Hỗ trợ nhiều loại video: Cooking, Vlog, Talkshow, News, Entertainment
Đầu ra: Dictionary (JSON) tương thích với React Frontend.
"""
import sys
import re
import traceback
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator

# Import các module con của bạn (Đảm bảo cấu trúc thư mục đúng)
from .config import SHORT_VIDEO_THRESHOLD, LONG_VIDEO_THRESHOLD, STOP_WORDS
from .utils import extract_video_id, reconstruct_sentences, format_timestamp
from .classifier import VideoClassifier
from .summarizer_cooking import CookingSummarizer
from .summarizer_vlog import VlogSummarizer
from .summarizer_talkshow import TalkshowSummarizer
from .summarizer_news import NewsSummarizer
from .summarizer_entertainment import EntertainmentSummarizer
from .summary_merger import SummaryMerger
from .dynamic_segmenter import DynamicSegmenter, TalkshowSegmenter
from .sentence_splitter import needs_splitting, split_sentences_with_timestamps

class SmartVideoSummarizer:
    def __init__(self):
        self.classifier = VideoClassifier()
        self.merger = SummaryMerger(similarity_threshold=0.5)
        self.segmenter = DynamicSegmenter(similarity_threshold=0.4, min_duration=60, max_duration=300)
        self.cooking_segmenter = DynamicSegmenter(similarity_threshold=0.3, min_duration=45, max_duration=120)
        self.talkshow_segmenter = TalkshowSegmenter(min_duration=45, max_duration=120)
        self.summarizers = {
            'cooking': None, 
            'vlog': None, 
            'talkshow': None, 
            'news': None, 
            'entertainment': None
        }

    def process_video(self, url, progress_callback=None):
        """
        Hàm chính: Xử lý video từ URL và trả về kết quả dạng Dictionary (JSON).
        """
        def update_progress(percent, msg):
            if progress_callback:
                progress_callback(percent, msg)
        # Mẫu kết quả mặc định nếu xảy ra lỗi
        default_error_result = {
            "type": "TEXT", 
            "category": "UNKNOWN", 
            "content": "Không thể trích xuất tóm tắt cho video này. Vui lòng kiểm tra lại link hoặc video không hỗ trợ."
        }

        update_progress(2, "Bắt đầu tải dữ liệu từ YouTube...")
        vid_id = extract_video_id(url)
        if not vid_id:
            return {"type": "TEXT", "category": "ERROR", "content": "Link YouTube không hợp lệ!"}

        try:
            update_progress(5, "Đang tải phụ đề (Transcript) của video...")
            api = YouTubeTranscriptApi()
            transcript_list = api.list(vid_id)
            
            transcript = None
            lang = 'vi'
            needs_translation = False

            # =================================================================
            # LOGIC LẤY PHỤ ĐỀ MỚI (Bắt được en-US, en-GB...)
            # =================================================================
            available_transcripts = [t for t in transcript_list]

            # 1. Ưu tiên 1: Tiếng Việt thủ công
            transcript = next((t for t in available_transcripts if not t.is_generated and t.language_code == 'vi'), None)
            
            # 2. Ưu tiên 2: Tiếng Anh thủ công (Bao gồm en, en-US, en-GB...)
            if not transcript:
                transcript = next((t for t in available_transcripts if not t.is_generated and t.language_code.startswith('en')), None)
                if transcript:
                    lang = 'en'
                    needs_translation = True

            # 3. Ưu tiên 3: Tiếng Việt tự động
            if not transcript:
                transcript = next((t for t in available_transcripts if t.is_generated and t.language_code == 'vi'), None)
            
            # 4. Ưu tiên 4: Tiếng Anh tự động (Bao gồm en, en-US, en-GB...)
            if not transcript:
                transcript = next((t for t in available_transcripts if t.is_generated and t.language_code.startswith('en')), None)
                if transcript:
                    lang = 'en'
                    needs_translation = True
            
            # 5. Fallback: Lấy bất kỳ phụ đề ngôn ngữ nào hiện có (thủ công trước, tự động sau)
            if not transcript:
                transcript = next((t for t in available_transcripts if not t.is_generated), None) or \
                             next((t for t in available_transcripts if t.is_generated), None)
                if transcript:
                    lang = transcript.language_code
                    needs_translation = True

            if transcript is None:
                return {"type": "TEXT", "category": "NO_SUBTITLE", "content": "Video này không có phụ đề (Transcript) để AI có thể phân tích."}

            update_progress(8, "Đang đọc nội dung phụ đề...")
            data = transcript.fetch()
            if len(data) < 10:
                return {"type": "TEXT", "category": "TOO_SHORT", "content": "Video này có quá ít nội dung hội thoại, không đủ dữ liệu để tóm tắt."}

            # Xử lý dịch thuật sang tiếng Việt nếu video là tiếng nước ngoài
            if needs_translation:
                update_progress(12, f"Đang dịch phụ đề từ '{lang}' sang Tiếng Việt...")
                translator = GoogleTranslator(source='auto', target='vi')
                translated_data = []
                def get_field(item, field):
                    try: return getattr(item, field)
                    except AttributeError: return item[field]
                
                BATCH_SIZE = 20
                total = len(data)
                for i in range(0, total, BATCH_SIZE):
                    batch = data[i:i + BATCH_SIZE]
                    batch_text = ' ||| '.join([get_field(item, 'text') for item in batch])
                    try:
                        translated_text = translator.translate(batch_text)
                        translated_parts = translated_text.split(' ||| ')
                        for j, item in enumerate(batch):
                            vi_text = translated_parts[j].strip() if j < len(translated_parts) else get_field(item, 'text')
                            translated_data.append({'text': vi_text, 'start': get_field(item, 'start'), 'duration': get_field(item, 'duration')})
                    except:
                        # Fallback nếu lỗi dịch
                        for item in batch:
                            translated_data.append({'text': get_field(item, 'text'), 'start': get_field(item, 'start'), 'duration': get_field(item, 'duration')})
                
                data = translated_data
                lang = 'vi'

            # 1. Tái tạo câu và phân loại video
            update_progress(16, "Đang phân tích ngữ cảnh và phân loại video...")
            sentences = reconstruct_sentences(data)
            duration = sentences[-1]['end'] if sentences else 0
            
            title_str = ''
            description_str = ''

            try:
                import requests
                # Lấy HTML page của video
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(f'https://www.youtube.com/watch?v={vid_id}', headers=headers, timeout=5)
                html = resp.text
                
                # Parse title
                import re
                title_match = re.search(r'"title":"([^"]+)"', html)
                desc_match = re.search(r'"shortDescription":"([^"]+)"', html)
                
                title_str = title_match.group(1).lower() if title_match else ''
                description_str = desc_match.group(1).lower() if desc_match else ''
            except Exception as e:
                print(f"[WARNING] Không lấy được metadata: {e}")

            video_info = {
                'title': title_str, 
                'description': description_str, 
                'category_id': '',
                'transcript_sample': ' '.join([s['text'] for s in sentences[:20]])
            }
            video_type = self.classifier.classify(video_info)

            # Trường hợp video thiên về nhạc/hình ảnh, không có nội dung chữ
            if video_type == 'unsupported':
                return {
                    "type": "TEXT", 
                    "category": "UNSUPPORTED", 
                    "content": "Video này thiên về hình ảnh/âm thanh, không có đủ nội dung thông tin hoặc hội thoại để tóm tắt."
                }

            if video_type == 'talkshow':
                sentences = reconstruct_sentences(data, video_type='talkshow')

            if needs_splitting(sentences):
                sentences = split_sentences_with_timestamps(sentences, video_type=video_type)
            update_progress(20, f"Đang tóm tắt nội dung ({video_type.upper()})...")

            # TRÍCH XUẤT TOÀN BỘ NỘI DUNG PHỤ ĐỀ GỐC SAU KHI ĐÃ ĐƯỢC XỬ LÝ/DỊCH
            full_transcript_text = " ".join([s['text'] for s in sentences])

            # =================================================================
            # 2. XỬ LÝ TÓM TẮT DỰA TRÊN LOẠI VIDEO VÀ XUẤT KẾT QUẢ
            # =================================================================
            
            # --- NHÓM 1: TÓM TẮT TOÀN CỤC (TEXT MODE) - Cho News & Talkshow ---
            if video_type in ['news', 'talkshow']:
                if not self.summarizers[video_type]:
                    if video_type == 'news':
                        self.summarizers['news'] = NewsSummarizer(lang)
                    else:
                        self.summarizers['talkshow'] = TalkshowSummarizer(lang)
                
                merged_summary = self.summarizers[video_type].summarize_video(sentences)
                
                return {
                    "type": "TEXT",
                    "category": video_type.upper(),
                    "content": merged_summary
                }
                
            # --- NHÓM 2: TÓM TẮT THEO TIMELINE (TIMELINE MODE) - Cho Vlog, Cooking, Giải trí ---
            else:
                timeline = self._create_timeline(sentences, video_type, lang)
                summary = self._create_summary(timeline, video_type, lang)

                if video_type == 'cooking':
                    merged_summary = self.merger.merge_similar_summaries(summary)
                else:
                    merged_summary = summary

                # Format lại cho Frontend React
                frontend_timeline = []
                for idx, item in enumerate(merged_summary):
                    frontend_timeline.append({
                        "time": item['time'],
                        "title": f"Phần {idx + 1}", # Sinh ra tiêu đề "Phần 1, Phần 2..."
                        "points": item['points'] if item['points'] else ["(Không có nội dung đáng chú ý)"]
                    })

                update_progress(28, "Hoàn tất tóm tắt nội dung video!")
                return {
                    "type": "TIMELINE",
                    "category": video_type.upper(),
                    "timeline": frontend_timeline,
                    "original_transcript": full_transcript_text
                }

        except Exception as e:
            # Ghi log lỗi vào console của server để debug
            print(f"❌ Lỗi nghiêm trọng tại quá trình tóm tắt video: {e}")
            traceback.print_exc()
            return default_error_result

    def _create_timeline(self, sentences, video_type, lang):
        stop_words = STOP_WORDS.get(lang, STOP_WORDS['vi'])
        if video_type == 'cooking':
            segmenter = self.cooking_segmenter
        else:
            segmenter = self.segmenter
            
        segments = segmenter.create_dynamic_segments(sentences, stop_words)
        timeline = []
        for seg in segments:
            timeline.append({
                'start_time': seg['start'], 
                'end_time': seg['end'],
                'timestamp': format_timestamp(seg['start']), 
                'sentences': seg['sentences']
            })
        return timeline

    def _create_summary(self, timeline, video_type, lang):
        if not self.summarizers[video_type]:
            if video_type == 'cooking':
                self.summarizers['cooking'] = CookingSummarizer(lang)
            elif video_type == 'vlog':
                self.summarizers['vlog'] = VlogSummarizer(lang)
            elif video_type == 'entertainment':
                self.summarizers['entertainment'] = EntertainmentSummarizer(lang)
            else:
                self.summarizers[video_type] = VlogSummarizer(lang)
                
        summarizer = self.summarizers[video_type]
        summary = []
        for item in timeline:
            points = summarizer.summarize_chunk(item['sentences'])
            
            # Format hiển thị khoảng thời gian (VD: 00:00 ➝ 01:05)
            if 'end_time' in item and item['end_time'] != item['start_time']:
                duration = item['end_time'] - item['start_time']
                time_display = f"{item['timestamp']} ➝ {format_timestamp(item['end_time'])}" if duration > 60 else item['timestamp']
            else:
                time_display = item['timestamp']
                
            summary.append({
                'time': time_display, 
                'points': points
            })
            
        return summary