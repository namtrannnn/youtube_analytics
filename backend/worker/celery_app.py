import os
from celery import Celery

# Lấy Redis URL từ biến môi trường (Docker đã set)
DUONG_DAN_REDIS = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker", 
    broker=DUONG_DAN_REDIS,
    backend=DUONG_DAN_REDIS,
)

# Cấu hình thêm cho ổn định
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600, # Kết quả hết hạn sau 1 giờ
)