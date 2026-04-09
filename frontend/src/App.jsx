import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';

// --- IMPORT COMPONENTS ---
import Header from './components/Header';
import Footer from './components/Footer';
import InputForm from './components/InputForm';
import AuthForm from './components/AuthForm';
import ForgotPassword from './components/ForgotPassword';
import HistoryPage from './components/HistoryPage';
import DashboardWrapper from './components/DashboardWrapper';
import ReportPage from './components/ReportPage';

// --- IMPORT API ---
import { api } from './api';

function App() {
  const navigate = useNavigate();
  
  // 1. Quản lý State User (Lấy từ localStorage để F5 không bị mất đăng nhập)
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user_info');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // 2. Hàm xử lý khi đăng nhập thành công
  const handleLoginSuccess = (userInfo) => {
    setUser(userInfo);
    localStorage.setItem('user_info', JSON.stringify(userInfo));
  };

  // 3. Hàm xử lý Đăng xuất
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    navigate('/auth/login');
  };

  // 4. HÀM XỬ LÝ PHÂN TÍCH VIDEO (Đã sửa lỗi Initialization)
  const startAnalysis = async (url, commentCount) => {
    try {
      // Gọi hàm startAnalysis từ file api.js
      const taskId = await api.startAnalysis(url, commentCount);
      // Có taskId rồi thì chuyển hướng sang trang Report
      navigate(`/report/${taskId}`);
    } catch (error) {
      console.error("Lỗi khi phân tích:", error);
      alert("Có lỗi xảy ra khi bắt đầu phân tích video. Vui lòng thử lại!");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans relative overflow-hidden">
      
      {/* HEADER TÍCH HỢP AUTH & LỊCH SỬ */}
      <Header 
        user={user} 
        onLogout={handleLogout} 
        // Gửi kèm state isLogin = true khi bấm nút Đăng nhập
        onLoginClick={() => navigate('/auth/login', { state: { isLogin: true } })}
        
        // Gửi kèm state isLogin = false khi bấm nút Đăng ký
        onRegisterClick={() => navigate('/auth/login', { state: { isLogin: false } })} 
      />
      
      {/* MAIN CONTENT VỚI ROUTING */}
      <main className="flex-grow container mx-auto px-4 pt-24 pb-12 relative z-10 flex flex-col justify-center">
        <Routes>
          {/* Trang chủ: Nhập link */}
          <Route path="/" element={<InputForm onSubmit={startAnalysis} />} />
          
          {/* Auth: Đăng nhập / Đăng ký */}
          <Route path="/auth/login" element={<AuthForm onLogin={handleLoginSuccess} />} />
          
          {/* Auth: Quên mật khẩu */}
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          
          {/* Lịch sử phân tích (Yêu cầu đăng nhập) */}
          <Route path="/history" element={
            user ? <HistoryPage /> : (
              <div className="text-center mt-20">
                <h2 className="text-2xl font-bold text-slate-800 mb-4">Bạn chưa đăng nhập</h2>
                <button 
                  onClick={() => navigate('/auth/login')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700"
                >
                  Đăng nhập để xem lịch sử
                </button>
              </div>
            )
          } />
          <Route path="/history/:taskId" element={<ReportPage />} />

          {/* Trang Báo cáo Dashboard */}
          <Route path="/report/:taskId" element={<DashboardWrapper />} />
        </Routes>
      </main>
      
      <Footer />
    </div>
  );
}

export default App;