import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, MessageSquare, ArrowRight, PlayCircle, Calendar, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../api';

// --- HÀM LẤY ẢNH BÌA YOUTUBE TỪ LINK ---
const getYouTubeThumbnail = (url) => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  const videoId = (match && match[2].length === 11) ? match[2] : null;
  return videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : 'https://via.placeholder.com/640x360.png?text=No+Thumbnail';
};

export default function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // --- STATE CHO PHÂN TRANG ---
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6; // Số lượng video hiển thị trên 1 trang
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, taskId: null });

  //lấy dữ liệu
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.getHistory();
        setHistory(data);
      } catch (error) {
        console.error("Lỗi khi tải lịch sử:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
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
  // 1. Hàm chạy khi bấm nút Thùng rác trên thẻ Video -> Mở Modal
  const handleDeleteClick = (taskId, e) => {
    e.stopPropagation(); // Ngăn chặn sự kiện click lan ra thẻ cha (chuyển trang)
    setDeleteModal({ isOpen: true, taskId: taskId });
  };

  // 2. Hàm chạy khi bấm nút "Xóa vĩnh viễn" bên trong Modal
  const confirmDelete = async () => {
    const taskId = deleteModal.taskId;
    try {
      await api.deleteHistory(taskId);
      
      const updatedHistory = history.filter(item => item.taskId !== taskId);
      setHistory(updatedHistory);
      
      const newTotalPages = Math.ceil(updatedHistory.length / itemsPerPage);
      if (currentPage > newTotalPages && newTotalPages > 0) {
        setCurrentPage(newTotalPages);
      }
    } catch (error) {
      console.error("Lỗi khi xóa lịch sử:", error);
      alert("Có lỗi xảy ra, không thể xóa lịch sử lúc này. Vui lòng thử lại sau.");
    } finally {
      // Dù xóa thành công hay thất bại cũng phải đóng Modal lại
      setDeleteModal({ isOpen: false, taskId: null });
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
        <div className="text-center px-5 py-20 bg-white rounded-3xl border border-slate-100 shadow-sm animate-in fade-in zoom-in duration-300">
           <p className="text-slate-500">Bạn chưa phân tích hoặc đã xóa hết lịch sử video</p>
           <button onClick={() => navigate('/')} className="mt-4 text-blue-600 font-bold hover:underline">Phân tích ngay</button>
        </div>
      ) : (
        <>
          {/* LƯỚI HIỂN THỊ VIDEO */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {currentItems.map((item) => {
                const dateObj = new Date(item.ngayTao);
                const formattedDate = `${dateObj.getDate()}/${dateObj.getMonth()+1}/${dateObj.getFullYear()} - ${String(dateObj.getHours()).padStart(2, '0')}:${String(dateObj.getMinutes()).padStart(2, '0')}`;

                return (
                  <motion.div 
                    key={item.taskId}
                    layout 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                    whileHover={{ y: -5 }}
                    onClick={() => navigate(`/history/${item.taskId}`)}
                    className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-xl hover:border-blue-200 transition-all cursor-pointer group flex flex-col relative"
                  >
                    
                    {/* NÚT XÓA */}
                    <button
                      onClick={(e) => handleDeleteClick(item.taskId, e)}
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
      {/* --- GIAO DIỆN MODAL XÁC NHẬN XÓA --- */}
      <AnimatePresence>
        {deleteModal.isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            // Bấm ra ngoài vùng tối sẽ đóng Modal
            onClick={() => setDeleteModal({ isOpen: false, taskId: null })}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              // Ngăn sự kiện click lan ra ngoài làm đóng Modal
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-6 overflow-hidden relative">
              <div className="flex flex-col items-center text-center">
                
                {/* Icon Cảnh báo */}
                <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-4">
                  <Trash2 className="w-8 h-8" />
                </div>
                
                {/* Nội dung Text */}
                <h3 className="text-xl font-extrabold text-slate-800 mb-2">Xóa lịch sử phân tích?</h3>
                <p className="text-slate-500 mb-8 leading-relaxed">
                  Bạn có chắc chắn muốn xóa báo cáo phân tích này khỏi danh sách không? <br/>
                  <span className="font-semibold text-red-500">Dữ liệu sẽ bị xóa vĩnh viễn và không thể khôi phục.</span>
                </p>
                
                {/* Các nút bấm */}
                <div className="flex gap-3 w-full">
                  <button
                    onClick={() => setDeleteModal({ isOpen: false, taskId: null })}
                    className="flex-1 py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors">
                    Hủy bỏ
                  </button>
                  <button
                    onClick={confirmDelete}
                    className="flex-1 py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl transition-colors shadow-sm shadow-red-200">
                    Xóa vĩnh viễn
                  </button>
                </div>                
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}