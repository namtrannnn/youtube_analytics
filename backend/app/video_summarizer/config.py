"""
Cấu hình cho hệ thống tóm tắt video thông minh
"""

# Ngưỡng thời gian
SILENCE_THRESHOLD = 0.5
MIN_SECTION_DURATION = 60
SHORT_VIDEO_THRESHOLD = 1200  # 20 phút
LONG_VIDEO_THRESHOLD = 3600   # 1 giờ

# Từ dừng theo ngôn ngữ
STOP_WORDS = {
    'vi': {
        'và', 'thì', 'mà', 'là', 'cái', 'này', 'kia', 'đó', 'đây', 'những', 'các',
        'cho', 'của', 'với', 'như', 'người', 'mình', 'tôi', 'bạn', 'chúng', 'rồi',
        'xong', 'nhé', 'nhá', 'ha', 'á', 'ơi', 'nhỉ', 'được', 'có', 'trong', 'ngoài',
        'lúc', 'khi', 'để', 'gì', 'đâu', 'ấy', 'vậy', 'thế', 'nha', 'luôn', 'rất',
        'quá', 'lắm', 'ạ', 'dạ', 'vâng', 'hello', 'xin', 'chào', 'ok', 'nhưng',
        'nên', 'vẫn', 'sẽ', 'đang', 'cũng', 'em', 'anh', 'chị', 'ở', 'về', 'sau',
        'trước', 'hay', 'nè', 'nãy', 'bây', 'giờ', 'còn', 'ừ', 'à', 'ơ'
    },
    'en': {
        'the', 'and', 'but', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'this', 'that', 'it',
        'i', 'you', 'we', 'they', 'just', 'so', 'well', 'like', 'um', 'uh',
        'hello', 'hi', 'guys', 'ok', 'okay', 'right', 'actually', 'basically',
        'literally', 'yeah', 'oh', 'hey', 'a', 'an'
    }
}

# Blacklist cho địa danh (để lọc rác)
LOCATION_BLACKLIST_WORDS = {
    'Khoai', 'Wow', 'Yes', 'Thank', 'Put', 'Yeah', 'Don', 'Ok',
    'Nhà', 'Phòng', 'Đây', 'Đó', 'Kia', 'Chỗ', 'Bên', 'Trong', 'Ngoài',
    'Cái', 'Con', 'Chiếc', 'Lúc', 'Khi', 'Một', 'Hai', 'Ba',
    'Bạn', 'Mình', 'Anh', 'Chị', 'Em', 'Cô', 'Chú', 'Bác',
    'Vách', 'Góc', 'Cửa', 'Tại', 'Đến', 'Về', 'Xong', 'Rồi',
    'Giá', 'Ngày', 'Sáng', 'Trưa', 'Chiều', 'Tối', 'Đêm',
    'Giải', 'Khung', 'Khoảng', 'Càng', 'Anber', 'Alber'
}

LOCATION_BLACKLIST_CONTEXT = {
    'giống', 'như', 'nhớ', 'tưởng', 'ngỡ', 'tựa', 'cảm giác', 'gợi'
}

# Từ điển nguyên liệu nấu ăn chuẩn
COOKING_INGREDIENTS = {
    # Thịt & Hải sản
    'thịt', 'thịt bò', 'thịt heo', 'thịt gà', 'thịt ba chỉ', 'sườn', 'cá', 'tôm', 
    'mực', 'trứng', 'chả', 'giò', 'cua', 'ngao', 'ốc', 'bò', 'gà', 'heo',
    
    # Rau củ
    'hành', 'tỏi', 'ớt', 'gừng', 'sả', 'tiêu', 'hành tây', 'hành tím', 'hành lá',
    'cà chua', 'cà rốt', 'khoai tây', 'khoai lang', 'rau', 'cải', 'nấm', 'ngò',
    'dưa leo', 'dưa chuột', 'bí', 'bầu', 'mướp', 'đậu', 'măng', 'giá',
    
    # Gia vị & Đồ khô
    'muối', 'đường', 'nước mắm', 'xì dầu', 'nước tương', 'dầu hào', 'bột ngọt', 
    'hạt nêm', 'bột canh', 'tiêu xay', 'ngũ vị hương', 'cà ri', 'sa tế', 'dấm', 
    'giấm', 'chanh', 'nước cốt dừa', 'sữa tươi', 'sữa đặc', 'bột năng', 'bột mì',
    'bột chiên giòn', 'bột bắp', 'gạo', 'nếp', 'bún', 'phở', 'miến', 'hủ tiếu', 
    'bánh tráng', 'bánh mì', 'dầu ăn', 'mỡ', 'tương ớt', 'tương cà', 'sữa', 'nước dừa'
}

# Phân loại video
VIDEO_CATEGORIES = {
    # Loại không hỗ trợ tóm tắt
    'unsupported': {
        'ids': ['10', '20'],  # Music, Gaming
        'keywords': ['music video', 'mv', 'official audio', 'lyric video', 'gameplay', 'playthrough']
    },
    
    # Nấu ăn / Cooking
    'cooking': {
        'ids': ['26'],  # Howto & Style
        'keywords': ['recipe', 'cooking', 'nấu ăn', 'món', 'cách làm', 'hướng dẫn nấu'],
        'chunk_size': 90,
        'similarity_threshold': 0.35
    },
    
    # Vlog / Du lịch
    'vlog': {
        'ids': ['19', '22'],  # Travel & Events
        'keywords': ['vlog', 'travel', 'du lịch', 'khám phá', 'review địa điểm'],
        'chunk_size': 120,
        'similarity_threshold': 0.30
    },
    
    # Talkshow / Podcast / Giáo dục
    'talkshow': {
        'ids': ['22', '27', '28'],  # People & Blogs, Education, Science & Technology
        'keywords': ['podcast', 'interview', 'talk', 'giáo dục', 'phỏng vấn', 'thảo luận'],
        'chunk_size': 150,
        'similarity_threshold': 0.40
    },
    
    # Tin tức
    'news': {
        'ids': ['25', '24', '27', '28'],  # News & Politics
        'keywords': [
            # Từ khóa chính thống
            'news', 'tin tức', 'thời sự', 'breaking', 'bản tin', 'điểm tin',
            'pháp luật', 'an ninh', 'chính trị', 'xã hội', 'thế giới', 'quốc tế',
            'thông tin', 'cập nhật', 'chuyển động', '24h', 'trực tiếp', 'live','tin mới','thời sự',
            '60 giây', '60 giay', 'chuyển động 24h', 'chào buổi sáng', 'tin nhanh',
            'vtv', 'htv', 'thvl', 'vtc', 'vov', 'đài phát thanh', 'truyền hình',
            
            # Từ khóa tin tức kiểu YouTube/Mạng xã hội
            'nóng', 'mới nhất', 'vụ án', 'cảnh báo', 'biến', 'drama',
            'sự thật', 'vạch trần', 'điều tra', 'xôn xao', 'chấn động',
            'diễn biến', 'kết quả', 'thông báo', 'phát hiện', 'bắt giữ'
        ],
        'chunk_size': 60,
        'similarity_threshold': 0.45
    },
    
    # Giải trí chung
    'entertainment': {
        'ids': ['24'],  # Entertainment
        'keywords': ['entertainment', 'giải trí', 'show'],
        'chunk_size': 100,
        'similarity_threshold': 0.35
    }
}

# Template tóm tắt theo loại video
SUMMARY_TEMPLATES = {
    'cooking': {
        'vi': {
            'ingredients': "🥘 Nguyên liệu: {items}",
            'steps': "• {action}",
            'note': "• Lưu ý: {note}"
        },
        'en': {
            'ingredients': "🥘 Ingredients: {items}",
            'steps': "• {action}",
            'note': "• Note: {note}"
        }
    },
    
    'vlog': {
        'vi': {
            'location': "📍 Địa điểm: {place}",
            'activity': "🎬 Hoạt động: {action}",
            'highlight': "⭐ Nổi bật: {point}"
        },
        'en': {
            'location': "📍 Location: {place}",
            'activity': "🎬 Activity: {action}",
            'highlight': "⭐ Highlight: {point}"
        }
    },
    
    'talkshow': {
        'vi': {
            'topic': "💬 Chủ đề: {topic}",
            'point': "• {point}",
            'quote': '"{quote}"'
        },
        'en': {
            'topic': "💬 Topic: {topic}",
            'point': "• {point}",
            'quote': '"{quote}"'
        }
    },
    
    'news': {
        'vi': {
            'headline': "📰 {headline}",
            'detail': "• {detail}",
            'source': "Nguồn: {source}"
        },
        'en': {
            'headline': "📰 {headline}",
            'detail': "• {detail}",
            'source': "Source: {source}"
        }
    }
}

# Pattern nhận diện
PATTERNS = {
    'cooking': {
        'vi': {
            'quantities': r'\b(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|muỗng|thìa|chén|cốc|gram|lít|phút|tiếng|giờ)\b',
            'actions': ['cho', 'thêm', 'ướp', 'nấu', 'xào', 'rán', 'luộc', 'kho', 'rim', 'hấp', 'trộn', 'cắt', 'thái', 'băm', 'nêm'],
            'notes': ['lưu ý', 'quan trọng', 'nhớ', 'cần', 'phải', 'không nên', 'tránh', 'nếu', 'vì']
        },
        'en': {
            'quantities': r'\b(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|cup|tsp|tbsp|oz|lb|minute|hour)\b',
            'actions': ['add', 'mix', 'cook', 'fry', 'boil', 'stir', 'cut', 'chop', 'season', 'heat'],
            'notes': ['note', 'important', 'remember', 'must', 'should', 'avoid', 'if', 'because']
        }
    },
    
    'vlog': {
        'vi': {
            'locations': r'\b([A-ZĐÀÁẢÃẠ][a-zđàáảãạèéẻẽẹ]+(?:\s+[A-ZĐÀÁẢÃẠ][a-zđàáảãạèéẻẽẹ]+)*)\b',
            'activities': ['đi', 'tham quan', 'khám phá', 'thử', 'ăn', 'chơi', 'trải nghiệm'],
            'emotions': ['tuyệt vời', 'đẹp', 'ngon', 'hay', 'thú vị', 'ấn tượng']
        },
        'en': {
            'locations': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'activities': ['visit', 'explore', 'try', 'eat', 'play', 'experience', 'see'],
            'emotions': ['amazing', 'beautiful', 'delicious', 'interesting', 'impressive']
        }
    },
    
    'talkshow': {
        'vi': {
            'topics': ['về', 'vấn đề', 'chủ đề', 'nói về', 'thảo luận', 'chia sẻ'],
            'opinions': ['theo tôi', 'tôi nghĩ', 'quan điểm', 'nhìn nhận'],
            'questions': ['tại sao', 'như thế nào', 'ai', 'gì', 'khi nào', 'ở đâu']
        },
        'en': {
            'topics': ['about', 'issue', 'topic', 'discuss', 'share'],
            'opinions': ['i think', 'in my opinion', 'perspective', 'view'],
            'questions': ['why', 'how', 'who', 'what', 'when', 'where']
        }
    },
    
    'news': {
        'vi': {
            'reporting_verbs': ['theo', 'cho biết', 'thông báo', 'tuyên bố', 'công bố', 'báo cáo','tin nóng','tin tức'],
            'time_markers': ['hôm nay', 'ngày', 'sáng nay', 'chiều nay', 'tối nay', 'vừa qua', 'mới đây'],
            'sources': ['ông', 'bà', 'anh', 'chị', 'đại diện', 'phát ngôn viên', 'chuyên gia'],
            'numbers': r'\d+\s*(người|triệu|tỷ|nghìn|%|USD|VND|ca|vụ|trường hợp)'
        },
        'en': {
            'reporting_verbs': ['according', 'said', 'announced', 'declared', 'reported', 'confirmed'],
            'time_markers': ['today', 'yesterday', 'this morning', 'tonight', 'recently', 'on'],
            'sources': ['official', 'spokesperson', 'representative', 'expert', 'authority'],
            'numbers': r'\d+\s*(people|million|billion|thousand|%|USD|cases|incidents)'
        }
    }
}