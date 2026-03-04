"""
Database địa danh - Dùng để nhận diện địa điểm trong vlog
Phương pháp: So khớp trực tiếp thay vì regex viết hoa
"""

# ─────────────────────────────────────────────────────────────
# VIỆT NAM
# ─────────────────────────────────────────────────────────────

VIETNAM_PROVINCES = {
    # Miền Bắc
    'hà nội', 'hải phòng', 'quảng ninh', 'hải dương', 'hưng yên',
    'thái bình', 'nam định', 'ninh bình', 'hà nam', 'vĩnh phúc',
    'bắc ninh', 'bắc giang', 'phú thọ', 'thái nguyên', 'lạng sơn',
    'cao bằng', 'bắc kạn', 'tuyên quang', 'hà giang', 'lào cai',
    'yên bái', 'sơn la', 'điện biên', 'lai châu', 'hòa bình',

    # Miền Trung
    'thanh hóa', 'nghệ an', 'hà tĩnh', 'quảng bình', 'quảng trị',
    'thừa thiên huế', 'huế', 'đà nẵng', 'quảng nam', 'quảng ngãi',
    'bình định', 'phú yên', 'khánh hòa', 'nha trang', 'ninh thuận',
    'bình thuận', 'phan thiết', 'kon tum', 'gia lai', 'đắk lắk',
    'đắk nông', 'lâm đồng', 'đà lạt',

    # Miền Nam
    'hồ chí minh', 'sài gòn', 'bình dương', 'đồng nai', 'bà rịa vũng tàu',
    'vũng tàu', 'tây ninh', 'bình phước', 'long an', 'tiền giang',
    'bến tre', 'trà vinh', 'vĩnh long', 'đồng tháp', 'an giang',
    'kiên giang', 'cần thơ', 'hậu giang', 'sóc trăng', 'bạc liêu',
    'cà mau',
}

VIETNAM_CITIES_DISTRICTS = {
    # Quận/huyện/phường nổi tiếng
    'quận 1', 'quận 3', 'quận 5', 'quận 7', 'quận 9', 'quận 10',
    'bình thạnh', 'tân bình', 'gò vấp', 'thủ đức',
    'hoàn kiếm', 'đống đa', 'ba đình', 'cầu giấy', 'tây hồ',
    'hội an', 'tam kỳ', 'hội an', 'mỹ sơn',
    'phú quốc', 'côn đảo', 'cát bà', 'hạ long', 'sapa', 'sa pa',
    'mộc châu', 'mai châu', 'hà giang', 'đồng văn', 'mèo vạc',
    'buôn ma thuột', 'pleiku', 'quy nhơn', 'tuy hòa',
    'phan rang', 'phan thiết', 'mũi né',
    'châu đốc', 'long xuyên', 'rạch giá', 'hà tiên',
    'mỹ tho', 'bến tre', 'cao lãnh', 'sa đéc',
}

VIETNAM_LANDMARKS = {
    'vịnh hạ long', 'hồ hoàn kiếm', 'hồ tây', 'lăng bác',
    'phố cổ hội an', 'thánh địa mỹ sơn', 'cố đô huế',
    'hang sơn đoòng', 'vườn quốc gia phong nha',
    'bãi biển mỹ khê', 'bãi biển đà nẵng',
    'núi bà đen', 'núi fansipan', 'đỉnh fansipan',
    'ruộng bậc thang mù cang chải', 'cao nguyên đồng văn',
}

# ─────────────────────────────────────────────────────────────
# ĐÔNG NAM Á
# ─────────────────────────────────────────────────────────────

SOUTHEAST_ASIA = {
    # Thái Lan
    'thái lan', 'thailand', 'bangkok', 'chiang mai', 'chiang rai',
    'phuket', 'krabi', 'koh samui', 'pattaya', 'ayutthaya',
    'hua hin', 'kanchanaburi', 'udon thani', 'korat', 'nakhon ratchasima',
    'mukdahan', 'nong khai', 'ubon ratchathani', 'khon kaen',
    'vientiane', 'mốc đa hảnh', 'mukdahan', 'savannakhet',

    # Campuchia
    'campuchia', 'cambodia', 'phnom penh', 'siem reap', 'angkor wat',
    'sihanoukville', 'battambang', 'kampot',

    # Lào
    'lào', 'laos', 'viêng chăn', 'luang prabang', 'vang vieng',
    'savannakhet', 'pakse',

    # Myanmar
    'myanmar', 'burma', 'yangon', 'mandalay', 'bagan', 'inle',
    'naypyidaw',

    # Malaysia
    'malaysia', 'kuala lumpur', 'penang', 'malacca', 'johor bahru',
    'kota kinabalu', 'kuching', 'langkawi', 'genting highlands',
    'cameron highlands',

    # Singapore
    'singapore', 'sentosa', 'marina bay',

    # Indonesia
    'indonesia', 'jakarta', 'bali', 'bandung', 'yogyakarta', 'lombok',
    'surabaya', 'medan', 'makassar', 'komodo',

    # Philippines
    'philippines', 'manila', 'cebu', 'davao', 'boracay', 'palawan',
    'el nido', 'coron',

    # Brunei
    'brunei', 'bandar seri begawan',

    # Timor Leste
    'timor leste', 'dili',
}

# ─────────────────────────────────────────────────────────────
# ĐÔNG Á
# ─────────────────────────────────────────────────────────────

EAST_ASIA = {
    # Nhật Bản
    'nhật bản', 'japan', 'tokyo', 'osaka', 'kyoto', 'hiroshima',
    'nagoya', 'sapporo', 'fukuoka', 'naha', 'okinawa', 'yokohama',
    'kobe', 'nara', 'nikko', 'hakone', 'fuji', 'núi fuji',

    # Hàn Quốc
    'hàn quốc', 'korea', 'seoul', 'busan', 'incheon', 'daegu',
    'jeju', 'gyeongju', 'gangnam', 'itaewon',

    # Trung Quốc
    'trung quốc', 'china', 'bắc kinh', 'beijing', 'thượng hải', 'shanghai',
    'quảng châu', 'guangzhou', 'thâm quyến', 'shenzhen', 'hàng châu',
    'tây an', 'thành đô', 'côn minh', 'lệ giang', 'guilin',
    'trương gia giới', 'hoàng sơn', 'vạn lý trường thành',
    'hạ môn', 'amoy', 'nam kinh', 'nanjing',

    # Đài Loan
    'đài loan', 'taiwan', 'đài bắc', 'taipei', 'cao hùng', 'kaohsiung',
    'đài trung', 'taichung', 'hoa liên', 'hualien',

    # Hồng Kông
    'hồng kông', 'hong kong', 'kowloon', 'lantau',

    # Mông Cổ
    'mông cổ', 'mongolia', 'ulaanbaatar',
}

# ─────────────────────────────────────────────────────────────
# NAM Á & TRUNG ĐÔNG
# ─────────────────────────────────────────────────────────────

SOUTH_CENTRAL_ASIA = {
    # Ấn Độ
    'ấn độ', 'india', 'new delhi', 'mumbai', 'bangalore', 'kolkata',
    'chennai', 'jaipur', 'agra', 'varanasi', 'goa', 'kerala',

    # Nepal
    'nepal', 'kathmandu', 'pokhara', 'everest',

    # Dubai & UAE
    'dubai', 'abu dhabi', 'uae',

    # Thổ Nhĩ Kỳ
    'thổ nhĩ kỳ', 'turkey', 'istanbul', 'ankara', 'cappadocia',

    # Israel
    'israel', 'jerusalem', 'tel aviv',
}

# ─────────────────────────────────────────────────────────────
# CHÂU ÂU
# ─────────────────────────────────────────────────────────────

EUROPE = {
    # Quốc gia - Chỉ dùng tên đầy đủ, bỏ từ đơn dễ nhầm
    'pháp', 'france', 'đức', 'germany', 'ý', 'italy', 'tây ban nha', 'spain',
    'bồ đào nha', 'portugal', 'hà lan', 'netherlands', 'bỉ', 'belgium',
    'thụy sĩ', 'switzerland', 'áo', 'austria', 'hy lạp', 'greece',
    'nước anh', 'vương quốc anh', 'uk', 'england', 'scotland', 'wales', 'ireland',
    # 'anh' bị bỏ vì trùng với đại từ "anh" trong tiếng Việt
    'nước nga', 'liên bang nga', 'russia', 'ukraine', 'ba lan', 'poland', 'séc', 'czech',
    'hungary', 'romania', 'bulgaria', 'croatia', 'slovenia',
    'nauy', 'norway', 'thụy điển', 'sweden', 'đan mạch', 'denmark',
    'phần lan', 'finland', 'iceland',

    # Thành phố
    'paris', 'london', 'berlin', 'rome', 'madrid', 'barcelona',
    'amsterdam', 'brussels', 'vienna', 'zurich', 'athens',
    'prague', 'budapest', 'warsaw', 'stockholm', 'oslo', 'copenhagen',
    'milan', 'florence', 'venice', 'naples', 'lisbon', 'porto',
    'frankfurt', 'munich', 'hamburg', 'cologne',
    'moscow', 'saint petersburg', 'kiev',
    'dubrovnik', 'split', 'santorini', 'mykonos',
    'reykjavik',
}

# ─────────────────────────────────────────────────────────────
# CHÂU MỸ
# ─────────────────────────────────────────────────────────────

AMERICAS = {
    # Mỹ
    'mỹ', 'america', 'usa', 'new york', 'los angeles', 'la', 'san francisco',
    'chicago', 'miami', 'las vegas', 'washington', 'boston', 'seattle',
    'dallas', 'houston', 'atlanta', 'hawaii', 'alaska',
    'california', 'florida', 'texas', 'new york city', 'nyc',

    # Canada
    'canada', 'toronto', 'vancouver', 'montreal', 'calgary', 'ottawa',
    'quebec',

    # Mỹ Latin
    'mexico', 'brazil', 'argentina', 'peru', 'colombia', 'chile',
    'cancun', 'buenos aires', 'rio de janeiro', 'sao paulo',
    'lima', 'bogota', 'santiago', 'machu picchu',

    # Caribbean
    'cuba', 'havana', 'jamaica', 'bahamas', 'dominican republic',
    'puerto rico', 'barbados',
}

# ─────────────────────────────────────────────────────────────
# CHÂU ÚC & CHÂU PHI
# ─────────────────────────────────────────────────────────────

OCEANIA_AFRICA = {
    # Úc & New Zealand
    'úc', 'australia', 'sydney', 'melbourne', 'brisbane', 'perth',
    'adelaide', 'canberra', 'cairns', 'gold coast', 'great barrier reef',
    'new zealand', 'auckland', 'wellington', 'queenstown',

    # Châu Phi
    'ai cập', 'egypt', 'cairo', 'marrakech', 'morocco', 'kenya',
    'nairobi', 'tanzania', 'cape town', 'johannesburg', 'south africa',
}

# ─────────────────────────────────────────────────────────────
# GỘP TẤT CẢ
# ─────────────────────────────────────────────────────────────

ALL_LOCATIONS = (
    VIETNAM_PROVINCES |
    VIETNAM_CITIES_DISTRICTS |
    VIETNAM_LANDMARKS |
    SOUTHEAST_ASIA |
    EAST_ASIA |
    SOUTH_CENTRAL_ASIA |
    EUROPE |
    AMERICAS |
    OCEANIA_AFRICA
)


def find_locations_in_text(text):
    """
    Tìm địa danh trong text - CHỈ lấy khi có ngữ cảnh rõ ràng là đang ở/đến
    Phân biệt: ngữ cảnh MẠNH vs YẾU, địa danh RÕ RÀNG vs MƠ HỒ
    """
    text_lower = text.lower()
    found = []

    # Ngữ cảnh MẠNH: Rõ ràng đang đi đến
    STRONG_POSITIVE = [
        'đang ở ', 'đang tại ', 'đang đi tới ',
        'chào mừng tới', 'chào mừng đến', 'chào mừng mọi người tới',
        'hôm nay ở ', 'hôm nay tại ', 'hôm nay đến ',
        'bay qua ', 'bay đến ', 'bay sang ',
        'nhập cảnh vào ', 'xuất cảnh sang',
        'tới được ', 'đã đến được ', 'lần này ở ','đến với '
    ]

    # Ngữ cảnh YẾU: Có thể là đang ở, có thể không
    WEAK_POSITIVE = [
        'tại ', 'đến ', 'tới ', 'ghé ', 'sang ',
        'đi tới ', 'đi đến ', 'đi qua ', 'qua ',
        'thành phố ', 'thủ đô ',
    ]

    # Ngữ cảnh ÂM TÍNH: So sánh, quá khứ, quê quán, nhắc đến
    NEGATIVE_CONTEXT = [
        'nhớ tới', 'nhớ đến', 'nhớ mấy', 'nhớ những',
        'giống như', 'giống ở', 'tương tự', 'kiểu như',
        'như ở', 'như bên', 'như tại',
        'cảm giác giống', 'giống hồi',
        'cảm giác như đang', 'cảm giác như',
        'giống như khoai đang', 'giống như mình đang',
        'hồi ở', 'hồi tại', 'hồi xưa', 'hồi còn',
        'xưa ở', 'đã ở', 'từng ở', 'từng đến',
        'đợt đi ', 'lần đi ', 'lần trước',
        'ba mẹ ở', 'quê ở', 'quê hương', 'quê ba mẹ',
        'gốc ', 'người gốc', 'ở quê',
        'cô là ở', 'anh là ở', 'chị là ở',
        'mọi người hay đi', 'hay đi ', 'có dịp', 'nếu đi', 'muốn đi',
        'cao nhất nước', 'nổi tiếng ở', 'đặc trưng của',
        'thời la ', 'thời trung', 'thời cổ',  # thời La Mã...
        'nhớ mấy cái', 'làm mình nhớ', 'làm khoai nhớ', 'con ở', 'cô ở', 'bên đó là','bên đó chính là','bên kia', 'lui về'
    ]

    # Địa danh MƠ HỒ: Chỉ lấy khi có STRONG context
    # (dễ nhầm với từ thông thường hoặc hay xuất hiện trong so sánh)
    AMBIGUOUS_LOCATIONS = {
        'la', 'áo', 'mỹ', 'ý', 'úc',
        'anh', 'lào',
        'hà giang', 'cao bằng', 'lạng sơn', 'bắc kạn',
        'việt nam', 'đức',
    }

    CONTEXT_WINDOW = 40

    sorted_locations = sorted(ALL_LOCATIONS, key=len, reverse=True)
    matched_spans = []
    seen_locs = set()

    for loc in sorted_locations:
        idx = 0
        while True:
            pos = text_lower.find(loc, idx)
            if pos == -1:
                break

            end = pos + len(loc)

            before_ok = (pos == 0 or not text_lower[pos-1].isalpha())
            after_ok = (end == len(text_lower) or not text_lower[end].isalpha())

            if before_ok and after_ok:
                is_overlapping = any(
                    not (end <= s or pos >= e)
                    for s, e in matched_spans
                )

                if not is_overlapping:
                    context_before = text_lower[max(0, pos - CONTEXT_WINDOW):pos]
                    # Mở rộng window cho negative check (60 ký tự)
                    context_before_wide = text_lower[max(0, pos - 60):pos]
                    has_negative = any(neg in context_before_wide for neg in NEGATIVE_CONTEXT)

                    # Thêm: bỏ qua nếu ngay trước địa danh là "hoặc là", "hay là" (liệt kê ví dụ)
                    immediate_before = text_lower[max(0, pos - 15):pos].strip()
                    if immediate_before.endswith('hoặc là') or immediate_before.endswith('hay là') or immediate_before.endswith('như là'):
                        has_negative = True

                    if not has_negative:
                        has_strong = any(p in context_before for p in STRONG_POSITIVE)
                        has_weak = any(p in context_before for p in WEAK_POSITIVE)

                        if loc in AMBIGUOUS_LOCATIONS:
                            should_include = has_strong  # Chỉ lấy khi ngữ cảnh MẠNH
                        else:
                            should_include = has_strong or has_weak

                        if should_include:
                            loc_cap = _capitalize_location(loc)
                            if loc_cap not in seen_locs:
                                found.append((pos, loc_cap))
                                seen_locs.add(loc_cap)
                                matched_spans.append((pos, end))

            idx = pos + 1

    found.sort(key=lambda x: x[0])
    return [loc for _, loc in found]


def _capitalize_location(loc):
    """Viết hoa chữ cái đầu mỗi từ của địa danh"""
    skip_words = {'và', 'của', 'ở', 'tại', 'the', 'de', 'van', 'von'}
    words = loc.split()
    result = []
    for i, word in enumerate(words):
        if i == 0 or word not in skip_words:
            result.append(word.capitalize())
        else:
            result.append(word)
    return ' '.join(result)