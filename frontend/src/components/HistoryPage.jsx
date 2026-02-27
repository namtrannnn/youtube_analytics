import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, MessageSquare, ArrowRight, PlayCircle, Calendar, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- HÀM LẤY ẢNH BÌA YOUTUBE TỪ LINK ---
const getYouTubeThumbnail = (url) => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  const videoId = (match && match[2].length === 11) ? match[2] : null;
  return videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : 'https://via.placeholder.com/640x360.png?text=No+Thumbnail';
};

// --- DỮ LIỆU GIẢ (NHIỀU HƠN ĐỂ TEST PHÂN TRANG) ---
const MOCK_HISTORY = Array.from({ length: 14 }).map((_, index) => ({
  taskId: `task-${index + 1}`,
  linkVideo: index % 2 === 0 ? 'https://youtu.be/KLakTkK82kM' : 'https://www.youtube.com/watch?v=O0gCk0USAXs',
  title: index % 2 === 0 ? `Hành trình khám phá Thụy Sĩ (Lần ${index + 1})` : `Bản tin thời sự (Lần ${index + 1})`,
  soLuongBinhLuan: Math.floor(Math.random() * 2000) + 100,
  ngayTao: new Date(Date.now() - index * 86400000).toISOString(), // Mỗi video cách nhau 1 ngày
  status: 'SUCCESS'
}));

export default function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // --- STATE CHO PHÂN TRANG ---
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6; // Số lượng video hiển thị trên 1 trang

  // Giả lập lấy dữ liệu
  useEffect(() => {
    setTimeout(() => {
      setHistory(MOCK_HISTORY); 
      setLoading(false);
    }, 500);
  }, []);

  // --- LOGIC TÍNH TOÁN PHÂN TRANG ---
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = history.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(history.length / itemsPerPage);

  // --- HÀM XỬ LÝ CHUYỂN TRANG ---
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    // Cuộn lên đầu trang mượt mà khi chuyển trang
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // --- HÀM XỬ LÝ XÓA LỊCH SỬ ---
  const handleDelete = (taskId, e) => {
    e.stopPropagation(); 
    
    if (window.confirm("Bạn có chắc chắn muốn xóa lịch sử phân tích này không? Dữ liệu không thể khôi phục.")) {
      const updatedHistory = history.filter(item => item.taskId !== taskId);
      setHistory(updatedHistory);
      
      // Fix lỗi UX: Nếu xóa phần tử cuối cùng của 1 trang, tự động lùi về trang trước
      const newTotalPages = Math.ceil(updatedHistory.length / itemsPerPage);
      if (currentPage > newTotalPages && newTotalPages > 0) {
        setCurrentPage(newTotalPages);
      }
      
      // Tương lai: Gọi API xóa
      // axios.delete(`/api/history/${taskId}`);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Đang tải lịch sử...</div>;
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
      className="max-w-6xl mx-auto py-10 px-4"
    >
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-blue-100 text-blue-600 rounded-2xl">
          <Clock className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-3xl font-extrabold text-slate-800">Lịch sử phân tích</h2>
          <p className="text-slate-500 mt-1">
            Bạn đã phân tích tổng cộng <span className="font-bold text-blue-600">{history.length}</span> video
          </p>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-slate-100 shadow-sm animate-in fade-in zoom-in duration-300">
           <p className="text-slate-500">Bạn chưa phân tích hoặc đã xóa hết lịch sử video.</p>
           <button onClick={() => navigate('/')} className="mt-4 text-blue-600 font-bold hover:underline">Phân tích ngay</button>
        </div>
      ) : (
        <>
          {/* LƯỚI HIỂN THỊ VIDEO */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {currentItems.map((item) => {
                const dateObj = new Date(item.ngayTao);
                const formattedDate = `${dateObj.getDate()}/${dateObj.getMonth()+1}/${dateObj.getFullYear()} - ${dateObj.getHours()}:${dateObj.getMinutes()}`;

                return (
                  <motion.div 
                    key={item.taskId}
                    layout 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                    whileHover={{ y: -5 }}
                    onClick={() => navigate(`/report/${item.taskId}`)}
                    className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-xl hover:border-blue-200 transition-all cursor-pointer group flex flex-col relative"
                  >
                    
                    {/* NÚT XÓA */}
                    <button
                      onClick={(e) => handleDelete(item.taskId, e)}
                      className="absolute top-3 right-3 z-10 p-2 bg-black/40 hover:bg-red-500 text-white rounded-full backdrop-blur-md opacity-0 group-hover:opacity-100 transition-all shadow-sm"
                      title="Xóa lịch sử này"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>

                    {/* Thumbnail YouTube */}
                    <div className="relative h-48 overflow-hidden bg-slate-100">
                      <img 
                        src={getYouTubeThumbnail(item.linkVideo)} 
                        alt="Thumbnail" 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors duration-500"></div>
                      <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-md text-white text-xs px-2 py-1 rounded-md flex items-center gap-1 font-medium">
                         <PlayCircle className="w-3 h-3"/> YouTube
                      </div>
                    </div>

                    {/* Info */}
                    <div className="p-5 flex-1 flex flex-col">
                      <h3 className="font-bold text-slate-800 text-lg mb-1 line-clamp-2 group-hover:text-blue-600 transition-colors">
                        {item.title || item.linkVideo}
                      </h3>
                      
                      <div className="mt-auto pt-4 space-y-2">
                        <div className="flex items-center text-sm text-slate-500 gap-2">
                          <Calendar className="w-4 h-4 text-slate-400"/> {formattedDate}
                        </div>
                        <div className="flex justify-between items-center">
                           <span className="flex items-center gap-1.5 text-sm font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-lg">
                             <MessageSquare className="w-4 h-4"/> {item.soLuongBinhLuan}
                           </span>
                           <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white text-slate-400 transition-colors">
                             <ArrowRight className="w-4 h-4"/>
                           </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>

          {/* TRÌNH ĐIỀU KHIỂN PHÂN TRANG (PAGINATION CONTROLS) */}
          {totalPages > 1 && (
            <div className="mt-10 flex justify-center items-center gap-2">
              
              {/* Nút Previous */}
              <button 
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`p-2 rounded-xl flex items-center justify-center transition-all ${
                  currentPage === 1 
                    ? 'text-slate-300 cursor-not-allowed bg-slate-50' 
                    : 'text-slate-600 hover:bg-blue-50 hover:text-blue-600 bg-white shadow-sm border border-slate-100'
                }`}
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              {/* Các số trang */}
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
                  <button
                    key={number}
                    onClick={() => handlePageChange(number)}
                    className={`w-10 h-10 rounded-xl font-bold text-sm transition-all flex items-center justify-center ${
                      currentPage === number
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-200'
                        : 'bg-white text-slate-600 border border-slate-100 hover:bg-blue-50 hover:text-blue-600 shadow-sm'
                    }`}
                  >
                    {number}
                  </button>
                ))}
              </div>

              {/* Nút Next */}
              <button 
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`p-2 rounded-xl flex items-center justify-center transition-all ${
                  currentPage === totalPages 
                    ? 'text-slate-300 cursor-not-allowed bg-slate-50' 
                    : 'text-slate-600 hover:bg-blue-50 hover:text-blue-600 bg-white shadow-sm border border-slate-100'
                }`}
              >
                <ChevronRight className="w-5 h-5" />
              </button>

            </div>
          )}
        </>
      )}
    </motion.div>
  );
}