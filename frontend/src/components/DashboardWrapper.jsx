import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';
import StatusPoll from './StatusPoll'; 

export default function DashboardWrapper() {
  const { taskId } = useParams();
  const [data, setData] = useState(null);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState('Đang khởi tạo...');
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let intervalId;
    
    const checkStatus = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/status/${taskId}`);
        
        // --- ĐÃ SỬA: Bắt đúng các key tiếng Việt do FastAPI trả về ---
        const { trang_thai, tien_do, tin_nhan, ket_qua } = res.data;

        // Cập nhật state nội bộ của React (dùng giá trị mặc định nếu API chưa kịp gửi)
        setProgress(tien_do || 0);
        setStatusMsg(tin_nhan || 'Đang xử lý...');

        // Kiểm tra logic theo tên trạng thái mới
        if (trang_thai === 'SUCCESS') {
          setData(ket_qua); // Đẩy dữ liệu vào state data
          clearInterval(intervalId); // Dừng polling
        } else if (trang_thai === 'FAILURE') {
          setIsError(true);
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error("Polling error", error);
      }
    };

    // Gọi ngay lần đầu
    checkStatus();
    // Sau đó lặp lại mỗi 2s
    intervalId = setInterval(checkStatus, 2000);

    return () => clearInterval(intervalId);
  }, [taskId]);

  if (isError) return <div className="text-center text-red-500 mt-10">Xử lý thất bại. Vui lòng thử lại.</div>;

  // Nếu chưa có data -> Hiện thanh Loading (StatusPoll)
  if (!data) {
    return <StatusPoll progress={progress} status={statusMsg} />;
  }

  // Có data -> Hiện Dashboard chính
  return <Dashboard data={data} taskId={taskId} />;
}