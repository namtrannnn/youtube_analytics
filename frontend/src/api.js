import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Địa chỉ FastAPI của bạn

export const api = {
  // Gửi link để bắt đầu phân tích
  startAnalysis: async (url, count) => {
    const response = await axios.post(`${API_BASE_URL}/analyze`, { url, count });
    return response.data.task_id;
  },

  // Polling: Kiểm tra trạng thái
  checkStatus: async (taskId) => {
    const response = await axios.get(`${API_BASE_URL}/status/${taskId}`);
    return response.data;
  },

  // Chat với dữ liệu
  chatWithData: async (taskId, question) => {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      task_id: taskId,
      question: question
    });
    return response.data.answer;
  }
};