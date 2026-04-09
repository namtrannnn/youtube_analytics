import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Dashboard from './Dashboard';
import { api } from '../api';
import { Loader2 } from 'lucide-react';

export default function ReportPage() {
  const { taskId } = useParams(); // Lấy ID từ url (/report/:taskId)
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const result = await api.getHistoryDetail(taskId);
        
        // Bóc tách dữ liệu từ API mới
        setData(result.dashboard_data); 
        setChatHistory(result.chat_history); 
        
      } catch (err) {
        setError("Không thể tải dữ liệu. Lịch sử này có thể không tồn tại hoặc bạn không có quyền xem.");
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [taskId]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-slate-500 font-medium">Đang tải lại dữ liệu phân tích...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
        <div className="bg-white p-8 rounded-2xl shadow-sm text-center">
           <h2 className="text-xl font-bold text-red-600 mb-2">Lỗi tải dữ liệu</h2>
           <p className="text-slate-500 mb-6">{error}</p>
           <button onClick={() => navigate('/history')} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
             Quay lại lịch sử
           </button>
        </div>
      </div>
    );
  }

  return <Dashboard data={data} taskId={taskId} initialChat={chatHistory} />;
}