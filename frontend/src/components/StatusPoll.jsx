import React from 'react';
import { motion } from 'framer-motion';

export default function StatusPoll({ progress, status }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg text-center">
        <h3 className="text-xl font-semibold mb-2">Đang xử lý dữ liệu</h3>
        <p className="text-slate-500 mb-6 text-sm">{status || "Đang kết nối..."}</p>

        <div className="w-full bg-slate-100 rounded-full h-4 mb-4 overflow-hidden">
          <motion.div 
            className="bg-blue-600 h-full rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        <div className="text-3xl font-bold text-blue-600">{progress}%</div>
      </div>
    </div>
  );
}