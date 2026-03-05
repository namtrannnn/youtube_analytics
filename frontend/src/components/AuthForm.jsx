import React, { useState, useEffect } from 'react';
import { Mail, Lock, User, ArrowRight, Loader2, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api'; 

export default function AuthForm({ onLogin, initialIsLogin = true }) {
  const navigate = useNavigate();
  const location = useLocation(); 
  
  const [isLogin, setIsLogin] = useState(initialIsLogin);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // State mới: Quản lý hiển thị màn hình Đăng ký thành công
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    if (location.state && location.state.isLogin !== undefined) {
      setIsLogin(location.state.isLogin);
    } else {
      setIsLogin(initialIsLogin);
    }
    setError(''); 
  }, [location.state, initialIsLogin]);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate độ dài mật khẩu ở Frontend
    if (password.length < 8) {
      setError('Mật khẩu quá ngắn. Vui lòng nhập ít nhất 8 ký tự!');
      return; 
    }
    if (password.length > 50) {
      setError('Mật khẩu quá dài. Vui lòng nhập tối đa 50 ký tự!');
      return; 
    }

    setIsLoading(true);
    setError(''); 

    try {
      if (isLogin) {
        // --- ĐĂNG NHẬP ---
        const data = await api.login(email, password);
        localStorage.setItem('access_token', data.access_token);
        onLogin(data.user_info);
        navigate('/'); 
      } else {
        // --- ĐĂNG KÝ ---
        await api.register(name, email, password);
        
        // KÍCH HOẠT MÀN HÌNH THÀNH CÔNG (Thay cho alert)
        setShowSuccess(true);
        
        // Tự động chuyển về form Đăng nhập sau 2.5 giây
        setTimeout(() => {
          setShowSuccess(false);
          setIsLogin(true); 
          setPassword(''); // Xóa mật khẩu cho an toàn
        }, 2500);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        setError(err.response.data.detail || 'Có lỗi xảy ra!');
      } else {
        setError('Không thể kết nối đến máy chủ.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md mx-auto px-4"
    >
      <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-[0_20px_50px_rgba(8,_112,_184,_0.1)] border border-white/20 overflow-hidden min-h-[500px] flex flex-col justify-center">
        
        {/* Decorative Blobs */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>

        <div className="relative z-10">
          
          <AnimatePresence mode="wait">
            {/* -----------------------------------------------------------
                TRẠNG THÁI 1: MÀN HÌNH THÔNG BÁO THÀNH CÔNG (HIỂN THỊ KHI ĐĂNG KÝ XONG) 
            -------------------------------------------------------------*/}
            {showSuccess ? (
              <motion.div 
                key="success"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.1 }}
                transition={{ duration: 0.4, type: "spring" }}
                className="flex flex-col items-center justify-center text-center space-y-4 py-10"
              >
                <motion.div 
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5, type: "spring", bounce: 0.5 }}
                  className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center shadow-lg shadow-green-200 mb-2"
                >
                  <CheckCircle className="w-12 h-12 text-green-500" />
                </motion.div>
                <h2 className="text-3xl font-extrabold text-slate-800 tracking-tight">Thành công!</h2>
                <p className="text-slate-500 font-medium">
                  Tài khoản của bạn đã được tạo.<br/>Đang chuyển hướng đến Đăng nhập...
                </p>
                <Loader2 className="w-6 h-6 animate-spin text-green-500 mt-4" />
              </motion.div>
            ) : (
              
              /* -----------------------------------------------------------
                 TRẠNG THÁI 2: FORM ĐĂNG NHẬP / ĐĂNG KÝ BÌNH THƯỜNG
              -------------------------------------------------------------*/
              <motion.div
                key="form"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="text-center mb-6">
                  <h2 className="text-3xl font-bold text-slate-900 mb-2">
                    {isLogin ? 'Chào mừng trở lại!' : 'Tạo tài khoản mới'}
                  </h2>
                  <p className="text-slate-500 text-sm">
                    {isLogin ? 'Đăng nhập để tiếp tục phân tích video' : 'Bắt đầu hành trình khám phá dữ liệu ngay hôm nay'}
                  </p>
                </div>

                {/* Khối báo lỗi */}
                <AnimatePresence>
                  {error && (
                    <motion.div 
                      initial={{ opacity: 0, y: -10 }} 
                      animate={{ opacity: 1, y: 0 }} 
                      exit={{ opacity: 0, height: 0 }}
                      className="mb-6 p-3 bg-red-50 border border-red-100 rounded-xl text-red-500 text-sm font-medium text-center shadow-sm"
                    >
                      {error}
                    </motion.div>
                  )}
                </AnimatePresence>

                <form onSubmit={handleSubmit} className="space-y-5">
                  {/* Tên hiển thị (Đăng ký) */}
                  <AnimatePresence>
                    {!isLogin && (
                      <motion.div 
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="space-y-1 overflow-hidden"
                      >
                        <label className="text-sm font-semibold text-slate-700 ml-1">Họ tên</label>
                        <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <User className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                          </div>
                          <input
                            type="text"
                            required={!isLogin}
                            placeholder="Nguyễn Văn A"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                          />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Email */}
                  <div className="space-y-1">
                    <label className="text-sm font-semibold text-slate-700 ml-1">Email</label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                      </div>
                      <input
                        type="email"
                        required
                        placeholder="name@gmail.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Password */}
                  <div className="space-y-1">
                    <div className="flex justify-between items-center ml-1">
                      <label className="text-sm font-semibold text-slate-700">Mật khẩu</label>
                      {isLogin && <Link to="/auth/forgot-password" className="text-xs text-blue-600 hover:underline">Quên mật khẩu?</Link>}
                    </div>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                      </div>
                      <input
                        type="password"
                        required
                        minLength={8}
                        maxLength={50}
                        placeholder="Ít nhất 8 ký tự..."
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3.5 rounded-xl font-bold text-white bg-gradient-to-r from-blue-600 to-violet-600 hover:shadow-lg hover:shadow-blue-200 transform active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-2"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        {isLogin ? 'Đăng nhập' : 'Đăng ký tài khoản'}
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </form>

                {/* Nút Social Login & Chuyển đổi trạng thái */}
                <div className="mt-8">
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-slate-200"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-2 bg-white/80 text-slate-500">Hoặc tiếp tục với</span>
                    </div>
                  </div>
                  <div className="mt-6">
                    <button type="button" className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors">
                      <img src="https://images.seeklogo.com/logo-png/27/1/google-logo-png_seeklogo-273191.png" className="w-4 h-4" alt="Google" />
                      <span className="font-semibold text-slate-700">Google</span>
                    </button>
                  </div>
                </div>

                <p className="mt-8 text-center text-sm text-slate-600">
                  {isLogin ? 'Chưa có tài khoản? ' : 'Đã có tài khoản? '}
                  <button 
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setError(''); 
                    }}
                    className="font-bold text-blue-600 hover:text-blue-700 hover:underline transition-colors"
                  >
                    {isLogin ? 'Đăng ký ngay' : 'Đăng nhập ngay'}
                  </button>
                </p>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>
    </motion.div>
  );
}