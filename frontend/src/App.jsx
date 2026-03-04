import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom'; 
import axios from 'axios';

// Import Components
import Header from './components/Header';
import Footer from './components/Footer';
import InputForm from './components/InputForm';
import AuthForm from './components/AuthForm';
import DashboardWrapper from './components/DashboardWrapper'; 
import HistoryPage from './components/HistoryPage';
import ForgotPassword from './components/ForgotPassword';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate(); 

  // --- HÀM XỬ LÝ AUTH (LOGIN/LOGOUT) ---
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    navigate('/'); 
  };

  const handleLogout = () => {
    setUser(null);
    navigate('/');
  };

  // --- HÀM XỬ LÝ PHÂN TÍCH (GỌI API) ---
  const startAnalysis = async (url, count) => {
    try {
      // ĐÃ SỬA: Gửi đúng key tiếng Việt theo chuẩn Pydantic của Backend
      const res = await axios.post(`${API_BASE_URL}/api/analyze`, { 
        duong_dan: url, 
        so_luong: count 
      });
      
      // ĐÃ SỬA: Lấy ma_tac_vu thay vì task_id để chuyển trang
      if (res.data.ma_tac_vu) {
        navigate(`/report/${res.data.ma_tac_vu}`);
      }
    } catch (error) {
      alert("Lỗi kết nối API: " + error.message);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 selection:bg-blue-100">
      {/* Background Effect */}
      <div className="fixed inset-0 z-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-100 via-slate-50 to-white opacity-60 pointer-events-none" />
      
      {/* Header luôn hiển thị */}
      <Header 
        user={user} 
        onLogout={handleLogout} 
        onLoginClick={() => navigate('/auth/login')}    
        onRegisterClick={() => navigate('/auth/register')} 
      />

      <main className="flex-grow container mx-auto px-4 pt-24 pb-12 relative z-10 flex flex-col justify-center">
        
        {/* --- KHU VỰC ĐỊNH TUYẾN (ROUTES) --- */}
        <Routes>
          
          {/* 1. Trang chủ: Nhập Link */}
          <Route path="/" element={
            <InputForm onSubmit={startAnalysis} isLoading={false} />
          } />

          {/* 2. Trang Đăng nhập/Đăng ký */}
          <Route path="/auth/login" element={
            <AuthForm 
              onLogin={handleLoginSuccess} 
              initialIsLogin={true} 
              onBack={() => navigate('/')}
            />
          } />
          
          <Route path="/auth/register" element={
            <AuthForm 
              onLogin={handleLoginSuccess} 
              initialIsLogin={false} 
              onBack={() => navigate('/')}
            />
          } />
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          <Route path="/history" element={
            user ? <HistoryPage /> : <div className="text-center mt-20 font-bold">Vui lòng đăng nhập để xem lịch sử.</div>
          } />

          {/* 3. Trang Báo cáo (Dashboard) */}
          <Route path="/report/:taskId" element={<DashboardWrapper />} />

        </Routes>

      </main>
      
      <Footer />
    </div>
  );
}

export default App;