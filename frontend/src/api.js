import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // Địa chỉ FastAPI của bạn

const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
};

export const api = {
  // ==========================================
  // 1. CÁC API PHÂN TÍCH
  // ==========================================

  startAnalysis: async (url, count) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/analyze`,
      {
        duong_dan: url,
        so_luong: count,
      },
      getAuthHeader(),
    );

    return response.data.ma_tac_vu;
  },

  checkStatus: async (taskId) => {
    const response = await axios.get(`${API_BASE_URL}/api/status/${taskId}`);
    return response.data;
  },

  chatWithData: async (taskId, question) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/chat`,
      {
        ma_tac_vu: taskId,
        cau_hoi: question,
      },
      getAuthHeader(),
    );
    return response.data.answer;
  },

  // ==========================================
  // 2. CÁC API XÁC THỰC
  // ==========================================

  login: async (email, password) => {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      email: email,
      mat_khau: password,
    });
    return response.data;
  },

  register: async (name, email, password) => {
    const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
      ten_dang_nhap: name,
      email: email,
      mat_khau: password,
    });
    return response.data;
  },

  googleLogin: async (credential) => {
    console.log("Google credential nhận được:", credential);

    const response = await axios.post(`${API_BASE_URL}/api/auth/google`, {
      credential: credential,
    });

    console.log("Response từ backend:", response.data);

    return response.data;
  },

  // ==========================================
  // 3. CÁC API QUÊN MẬT KHẨU
  // ==========================================

  forgotSendOtp: async (email) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/auth/forgot-password/send-otp`,
      {
        email: email,
      },
    );
    return response.data;
  },

  forgotVerifyOtp: async (email, otp) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/auth/forgot-password/verify-otp`,
      {
        email: email,
        otp: otp,
      },
    );
    return response.data;
  },

  forgotResetPassword: async (email, otp, newPassword) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/auth/forgot-password/reset`,
      {
        email: email,
        otp: otp,
        mat_khau_moi: newPassword,
      },
    );
    return response.data;
  },

  // Lấy danh sách lịch sử
  getHistory: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/history`, getAuthHeader());
    return response.data;
  },

  // Lấy chi tiết một lịch sử để hiện Dashboard
  getHistoryDetail: async (taskId) => {
    const response = await axios.get(`${API_BASE_URL}/api/history/${taskId}`, getAuthHeader());
    return response.data;
  },

  // Xóa một lịch sử phân tích
  deleteHistory: async (taskId) => {
    const response = await axios.delete(`${API_BASE_URL}/api/history/${taskId}`, getAuthHeader());
    return response.data;
  },

};
