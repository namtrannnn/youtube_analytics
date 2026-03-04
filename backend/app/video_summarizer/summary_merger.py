"""
Module gộp các phần tóm tắt có nội dung tương tự
Giúp giảm redundancy và tạo tóm tắt súc tích hơn
"""

class SummaryMerger:
    """Gộp các summary liền kề có nội dung tương tự"""
    
    def __init__(self, similarity_threshold=0.6):
        self.similarity_threshold = similarity_threshold
    
    def merge_similar_summaries(self, summaries):
        """
        Gộp các summary liên tiếp có nội dung giống nhau
        
        Args:
            summaries: List[dict] - Mỗi dict có 'time' và 'points'
        
        Returns:
            List[dict] - Đã gộp các phần giống nhau
        """
        if len(summaries) <= 1:
            return summaries
        
        merged = []
        current_group = [summaries[0]]
        
        for i in range(1, len(summaries)):
            curr = summaries[i]
            prev = summaries[i-1]
            
            # Tính độ tương đồng
            similarity = self._calculate_similarity(curr['points'], prev['points'])
            
            if similarity >= self.similarity_threshold:
                # Gộp vào group hiện tại
                current_group.append(curr)
            else:
                # Kết thúc group, tạo merged item
                merged_item = self._create_merged_item(current_group)
                merged.append(merged_item)
                
                # Bắt đầu group mới
                current_group = [curr]
        
        # Xử lý group cuối
        if current_group:
            merged_item = self._create_merged_item(current_group)
            merged.append(merged_item)
        
        return merged
    
    def _calculate_similarity(self, points1, points2):
        """
        Tính độ tương đồng giữa 2 danh sách điểm tóm tắt
        
        Logic:
        - So sánh số từ chung
        - Xem có cùng icon không (📍, 🎬, ⭐)
        """
        if not points1 or not points2:
            return 0.0
        
        # Chuyển tất cả points thành text
        text1 = ' '.join(points1).lower()
        text2 = ' '.join(points2).lower()
        
        # Loại bỏ icon để so sánh thuần text
        for icon in ['📍', '🎬', '⭐', '💡', '🥘', '⚖️', '💬', '📰', '•']:
            text1 = text1.replace(icon, '')
            text2 = text2.replace(icon, '')
        
        # Tách từ
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Tính Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _create_merged_item(self, group):
        """
        Tạo item đã merge từ một group
        
        Logic:
        - Thời gian: Lấy từ item đầu đến item cuối
        - Nội dung: Gộp unique points, loại trùng
        """
        if len(group) == 1:
            return group[0]
        
        # Lấy time range
        start_time = group[0]['time']
        end_time = group[-1]['time']
        
        if len(group) > 1:
            time_range = f"{start_time} - {end_time}"
        else:
            time_range = start_time
        
        # Gộp points, loại trùng
        all_points = []
        seen_content = set()
        
        for item in group:
            for point in item['points']:
                # Chuẩn hóa để check trùng
                normalized = point.lower().replace('📍', '').replace('🎬', '').replace('⭐', '').replace('🥘', '').replace('⚖️', '').strip()
                
                if normalized and normalized not in seen_content:
                    all_points.append(point)
                    seen_content.add(normalized)
        
        # KHÔNG giới hạn - Lấy hết
        final_points = all_points  # Bỏ [:3]
        
        return {
            'time': time_range,
            'points': final_points,
            'merged_count': len(group)
        }