import React from 'react';
import { Youtube, LogIn, UserPlus, LogOut, History } from 'lucide-react'; 
import { useNavigate } from 'react-router-dom';

export default function Header({ user, onLogout, onLoginClick, onRegisterClick }) {
  const navigate = useNavigate();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center gap-2 cursor-pointer group" onClick={() => navigate("/")}>
          <div className="bg-gradient-to-br from-red-500 to-pink-600 p-2 rounded-lg shadow-lg group-hover:scale-105 transition-transform">
            <Youtube className="w-6 h-6 text-white" />
          </div>
          <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-600">
            YT Analyst
          </span>
        </div>

        {/* User Actions */}
        <div className="flex items-center gap-4">
          {user ? (
            // --- ĐÃ LOGIN (GIAO DIỆN MỚI GỌN GÀNG) ---
            <div className="flex items-center gap-2 sm:gap-3">
              
              {/* 1. Cụm thông tin người dùng */}
              <div className="hidden md:flex flex-col items-end mr-1">
                <span className="text-sm font-bold text-slate-700">{user.name}</span>
                <span className="text-[11px] text-slate-400 font-medium">{user.email}</span>
              </div>
              
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-50 to-blue-100 flex items-center justify-center text-blue-600 font-bold border-2 border-white shadow-sm ring-1 ring-slate-100">
                {user.name.charAt(0).toUpperCase()}
              </div>

              {/* Vạch kẻ phân cách */}
              <div className="h-6 w-px bg-slate-200 mx-1 sm:mx-2"></div>

              {/* 2. Cụm Nút hành động (Chỉ dùng Icon, đồng nhất kích thước) */}
              <button 
                onClick={() => navigate('/history')}
                className="p-2.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all group"
                title="Lịch sử phân tích"
              >
                <History className="w-5 h-5 group-hover:-rotate-12 transition-transform" />
              </button>

              <button 
                onClick={onLogout}
                className="p-2.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-all group"
                title="Đăng xuất"
              >
                <LogOut className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
              </button>
              
            </div>
          ) : (
            // --- CHƯA LOGIN ---
            <div className="flex items-center gap-4">
              <button 
                onClick={onLoginClick}
                className="hidden md:flex items-center gap-2 text-slate-600 hover:text-blue-600 font-medium transition-colors"
              >
                <LogIn className="w-4 h-4" />
                Đăng nhập
              </button>
              
              <button 
                onClick={onRegisterClick}
                className="flex items-center gap-2 px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-full font-medium transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
              >
                <UserPlus className="w-4 h-4" />
                Đăng ký
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}