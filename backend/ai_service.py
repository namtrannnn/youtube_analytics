import os
import json
from google import genai # Import thư viện mới
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env")

# Khởi tạo Client mới theo chuẩn của google-genai
client = genai.Client(api_key=GEMINI_API_KEY)

def get_chatbot_response(cau_hoi: str, du_lieu_phan_tich: dict) -> str:
    """Hàm gửi tin nhắn và dữ liệu ngữ cảnh tới Gemini"""
    try:
        # Chuyển đổi dữ liệu phân tích thành chuỗi Text
        data_str = json.dumps(du_lieu_phan_tich, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Bạn là một trợ lý AI thông minh chuyên phân tích dữ liệu bình luận YouTube.
        Dưới đây là kết quả phân tích bình luận và bản tóm tắt của một video do hệ thống thu thập và xử lý:
        
        <du_lieu_phan_tich>
        {data_str}
        </du_lieu_phan_tich>
        
        Nhiệm vụ: Dựa HOÀN TOÀN vào phần <du_lieu_phan_tich> ở trên, hãy trả lời ngắn gọn câu hỏi của người dùng.
        
        Quy tắc bắt buộc:
        - Chỉ sử dụng thông tin có trong dữ liệu. Không tự bịa thêm thông tin bên ngoài.
        - Trả lời ngắn gọn các thông tin có trong dữ liệu.
        - Trình bày câu trả lời rõ ràng, dễ đọc (có thể dùng bullet point, in đậm).
        - Nếu câu hỏi hỏi về thông tin không có trong dữ liệu, hãy trả lời: "Tôi không tìm thấy thông tin này trong dữ liệu phân tích hiện tại."
        
        Câu hỏi của người dùng: "{cau_hoi}"
        """
        
        # Dùng model gemini-2.5-flash (hoặc gemini-2.0-flash) với cú pháp mới
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Xin lỗi, chatbot hiện tại đang gặp sự cố khi xử lý dữ liệu. Vui lòng thử lại sau."