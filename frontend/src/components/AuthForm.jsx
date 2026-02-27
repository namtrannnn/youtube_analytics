import React, { useState, useEffect } from 'react';
import { Mail, Lock, User, ArrowRight, Loader2, Github } from 'lucide-react';
import { motion } from 'framer-motion';

// Nhận prop initialIsLogin
export default function AuthForm({ onLogin, onBack, initialIsLogin = true }) {
  // Khởi tạo state dựa trên prop được truyền vào
  const [isLogin, setIsLogin] = useState(initialIsLogin);
  // Lắng nghe sự thay đổi của prop initialIsLogin (từ Header gửi xuống)
  // Mỗi khi bấm nút trên Header, biến này thay đổi -> cập nhật lại state isLogin
  useEffect(() => {
    setIsLogin(initialIsLogin);
  }, [initialIsLogin]);
  const [isLoading, setIsLoading] = useState(false);

  // Form State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Giả lập gọi API login (Delay 1.5s)
    setTimeout(() => {
      setIsLoading(false);
      // Gọi hàm onLogin để báo cho App.jsx biết là đã đăng nhập thành công
      // Truyền thông tin user giả lập
      onLogin({ name: name || "User", email: email });
    }, 1500);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md mx-auto px-4"
    >
      <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-[0_20px_50px_rgba(8,_112,_184,_0.1)] border border-white/20 overflow-hidden">
        
        {/* Decorative Blobs (Giống InputForm) */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>

        <div className="relative z-10">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-slate-900 mb-2">
              {isLogin ? 'Chào mừng trở lại!' : 'Tạo tài khoản mới'}
            </h2>
            <p className="text-slate-500 text-sm">
              {isLogin ? 'Đăng nhập để tiếp tục phân tích video' : 'Bắt đầu hành trình khám phá dữ liệu ngay hôm nay'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Tên hiển thị (Chỉ hiện khi Đăng ký) */}
            {!isLogin && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
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
                {isLogin && <a href="#" className="text-xs text-blue-600 hover:underline">Quên mật khẩu?</a>}
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
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
              className="w-full py-3.5 rounded-xl font-bold text-white bg-gradient-to-r from-blue-600 to-violet-600 hover:shadow-lg hover:shadow-blue-200 transform active:scale-[0.98] transition-all flex items-center justify-center gap-2"
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

          {/* Social Login */}
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-slate-500">Hoặc tiếp tục với</span>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button className="flex items-center justify-center px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors">
                <Github className="w-5 h-5 mr-2" /> Github
              </button>
              <button className="flex items-center justify-center px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors">
                <span className="font-bold text-red-500 mr-2">G</span> Google
              </button>
            </div>
          </div>

          {/* Switch Mode */}
          <p className="mt-8 text-center text-sm text-slate-600">
            {isLogin ? 'Chưa có tài khoản? ' : 'Đã có tài khoản? '}
            <button 
              onClick={() => setIsLogin(!isLogin)}
              className="font-bold text-blue-600 hover:text-blue-700 hover:underline transition-colors"
            >
              {isLogin ? 'Đăng ký ngay' : 'Đăng nhập ngay'}
            </button>
          </p>
        </div>
      </div>
    </motion.div>
  );
}