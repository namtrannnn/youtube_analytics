import React, { useState } from 'react';
import { Activity, FileText, MessageCircle, Film } from 'lucide-react';
import { motion } from 'framer-motion';

// --- IMPORT CÁC COMPONENT ĐÃ TÁCH ---
import VideoSummaryPanel from './VideoSummary';
import CommentAnalysis from './CommentAnalysis';
import ChatWindow from './ChatWindow'; 

export default function Dashboard({ data, taskId }) {
  const [activeTab, setActiveTab] = useState('comments');

  // Trích xuất dữ liệu cơ bản cho giao diện chung
  const video_url = data?.video_url || '';
  const videoSummary = data?.video_summary || null;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="max-w-7xl mx-auto space-y-6 pb-20 pt-8">
      
      {/* === HEADER & TABS === */}
      <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 md:px-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-800 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-600" />
              Báo Cáo Phân Tích Bình Luận Video
            </h2>
            <p className="text-slate-500 text-sm mt-1 flex items-center gap-2 flex-wrap">
               {video_url ? (
                 <>
                   <span>Nguồn:</span>
                   <a href={video_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline font-medium truncate max-w-[200px]">{video_url}</a>
                 </>
               ) : (
                 <span className="italic text-slate-400">Chưa có nguồn video</span>
               )}
               {videoSummary?.category && <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md text-xs font-bold uppercase">{videoSummary.category}</span>}
            </p>
          </div>
          <button onClick={() => alert('Đang xuất báo cáo...')} className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-all font-medium text-sm shadow-lg shadow-slate-200">
              <FileText className="w-4 h-4" /> Xuất Excel
          </button>
        </div>

        <div className="flex px-6 pt-4 gap-6 bg-slate-50/50">
           <button 
              onClick={() => setActiveTab('comments')}
              className={`pb-4 px-2 font-bold text-sm md:text-base border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'comments' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
           >
              <MessageCircle className="w-5 h-5" /> Phân Tích Bình Luận
           </button>
           <button 
              onClick={() => setActiveTab('summary')}
              className={`pb-4 px-2 font-bold text-sm md:text-base border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'summary' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
           >
              <Film className="w-5 h-5" /> Tóm Tắt Nội Dung Video
           </button>
        </div>
      </div>

      {/* === MAIN LAYOUT === */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* --- CỘT TRÁI (8 CỘT) --- */}
        <div className="lg:col-span-8 space-y-6">
          {activeTab === 'summary' && (
            <VideoSummaryPanel videoSummary={videoSummary} />
          )}

          {activeTab === 'comments' && (
             <CommentAnalysis data={data} />
          )}
        </div>

        {/* --- CỘT PHẢI (CHATBOT - LUÔN HIỂN THỊ) --- */}
        <div className="lg:col-span-4">
          <div className="sticky top-6 h-[calc(100vh-40px)] flex flex-col">
             <div className="flex-1 min-h-0 bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
                <ChatWindow taskId={taskId} />
             </div>
             <div className="mt-4 p-5 bg-blue-50 text-blue-800 rounded-2xl text-sm border border-blue-100 shadow-sm">
                <strong className="flex items-center gap-2">💡 Gợi ý câu hỏi:</strong>
                <ul className="list-disc ml-4 mt-3 space-y-2 text-slate-600">
                   <li>Có vấn đề gì tiêu cực không?</li>
                   <li>Mọi người đang tranh luận về vấn đề gì?</li>
                   <li>Có từ khóa nào xuất hiện nhiều nhất?</li>
                </ul>
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}