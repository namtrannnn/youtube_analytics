import React, { useState } from 'react';
import { Youtube, Search, Loader2, Link as LinkIcon, MessageSquare, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function InputForm({ onSubmit }) {
  const [url, setUrl] = useState('');
  
  // Mặc định là 500 theo ý bạn
  const [count, setCount] = useState(500); 
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Cấu hình giới hạn an toàn
  const MIN_COMMENTS = 100; // Thấp nhất cho phép (để AI có cái mà phân tích)
  const MAX_COMMENTS = 5000; // Giới hạn trần để không sập server
  
  // Các mốc chọn nhanh
  const PRESETS = [500, 1000, 2000, 5000];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    // Validate số lượng trước khi gửi
    let finalCount = count;
    if (finalCount < MIN_COMMENTS) finalCount = MIN_COMMENTS;
    if (finalCount > MAX_COMMENTS) finalCount = MAX_COMMENTS;
    
    // Cập nhật lại UI cho đúng số thực tế sẽ chạy
    setCount(finalCount);

    setIsSubmitting(true);
    try {
      await onSubmit(url, finalCount);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl mx-auto px-4"
    >
      <div 
        className="relative bg-white/90 backdrop-blur-xl rounded-3xl p-8 md:p-10 shadow-[0_20px_50px_rgba(8,_112,_184,_0.1)] border border-white/20 overflow-hidden"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Decorative Blob */}
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>

        <div className="relative z-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-tr from-red-500 to-orange-500 shadow-lg shadow-red-200 mb-6 transform transition-transform hover:rotate-6">
              <Youtube className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
              Phân tích <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-violet-600">Video Insight</span>
            </h1>
            <p className="text-lg text-slate-500 max-w-md mx-auto">
              Khám phá cảm xúc, xu hướng & giá trị ẩn sau từng bình luận YouTube
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* 1. URL Input */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 ml-1">Đường dẫn YouTube</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <LinkIcon className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                </div>
                <input
                  type="text"
                  required
                  placeholder="Dán link video (Ví dụ: https://youtu.be/...)"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all duration-300 font-medium text-slate-700"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
            </div>

            {/* 2. Count Input (CUSTOM + PRESETS) */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                  <label className="text-sm font-bold text-slate-700 ml-1">Số lượng bình luận cần lấy</label>
                  <span className="text-xs font-medium text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">
                    Tối đa: {MAX_COMMENTS.toLocaleString()}
                  </span>
              </div>
              
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <MessageSquare className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                </div>
                
                {/* Ô nhập số tùy ý */}
                <input
                  type="number"
                  min={MIN_COMMENTS}
                  max={MAX_COMMENTS}
                  value={count}
                  onChange={(e) => setCount(Number(e.target.value))}
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all duration-300 font-bold text-slate-700 text-lg"
                />

                {/* Cảnh báo nếu nhập quá giới hạn */}
                {count > MAX_COMMENTS && (
                    <div className="absolute inset-y-0 right-6 flex items-center text-amber-500 text-xs font-bold gap-1 animate-pulse">
                        <AlertCircle className="w-4 h-4" /> Tự động giảm về {MAX_COMMENTS}
                    </div>
                )}
              </div>

              {/* Các nút chọn nhanh (Presets) */}
              <div className="flex flex-wrap gap-2">
                {PRESETS.map((val) => (
                    <button
                        key={val}
                        type="button"
                        onClick={() => setCount(val)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                            count === val 
                            ? 'bg-blue-100 text-blue-700 border-blue-200 shadow-inner' 
                            : 'bg-white text-slate-500 border-slate-200 hover:border-blue-300 hover:text-blue-600'
                        }`}
                    >
                        {val === 5000 ? 'Tối đa (5k)' : `${val} bình luận`}
                    </button>
                ))}
              </div>
            </div>

            {/* 3. Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full relative overflow-hidden group py-4 rounded-xl font-bold text-lg text-white shadow-xl shadow-blue-200 transition-all duration-300 transform active:scale-[0.98] ${
                isSubmitting 
                  ? 'bg-slate-400 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:shadow-indigo-300 hover:-translate-y-1'
              }`}
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
              <div className="flex items-center justify-center gap-2">
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Đang khởi tạo...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-6 h-6" />
                    <span>Bắt đầu phân tích ngay</span>
                  </>
                )}
              </div>
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
}