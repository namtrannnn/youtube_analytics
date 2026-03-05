import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Địa chỉ FastAPI của bạn

// 1. Tạo một "bản sao" của axios (instance) để cài đặt cấu hình chung
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. INTERCEPTOR: Tự động đính kèm Token vào Header của mọi Request
apiClient.interceptors.request.use(
  (config) => {
    // Lấy token từ trình duyệt (do lúc đăng nhập mình đã lưu vào đây)
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const api = {
  // ==========================================
  // CÁC API PHÂN TÍCH & CHAT
  // Đã chuyển sang dùng apiClient thay vì axios gốc
  // ==========================================
  
  startAnalysis: async (url, count) => {
    const response = await apiClient.post('/analyze', { url, count });
    return response.data.task_id;
  },

  checkStatus: async (taskId) => {
    const response = await apiClient.get(`/status/${taskId}`);
    return response.data;
  },

  chatWithData: async (taskId, question) => {
    const response = await apiClient.post('/chat', {
      task_id: taskId,
      question: question
    });
    return response.data.answer;
  },

  // ==========================================
  // CÁC API XÁC THỰC
  // ==========================================

  // Đăng nhập
  login: async (email, password) => {
    const response = await apiClient.post('/api/auth/login', {
      email: email,
      mat_khau: password
    });
    return response.data; // Trả về { access_token, user_info }
  },

  // Đăng ký
  register: async (name, email, password) => {
    const response = await apiClient.post('/api/auth/register', {
      ten_dang_nhap: name,
      email: email,
      mat_khau: password
    });
    return response.data;
  }
};