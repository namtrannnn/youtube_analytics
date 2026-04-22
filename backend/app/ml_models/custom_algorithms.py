import numpy as np

class KMeansTuyChinh:
    def __init__(self, so_cum=3, so_vong_lap_toi_da=100, dung_sai=1e-4, random_state=42):
        self.so_cum = so_cum
        self.so_vong_lap_toi_da = so_vong_lap_toi_da
        self.dung_sai = dung_sai 
        self.tam_cum = None
        self.random_state = random_state

    def _khoang_cach_euclide(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2)**2))

    def huan_luyen_va_du_doan(self, X):
        if len(X) < self.so_cum: # Fix lỗi nếu dữ liệu ít hơn số cụm
             self.so_cum = len(X)
        
        # Dùng RandomState để cố định seed, giúp kết quả ổn định
        rng = np.random.RandomState(self.random_state)
        chi_so = rng.choice(X.shape[0], self.so_cum, replace=False)
        self.tam_cum = X[chi_so]

        for _ in range(self.so_vong_lap_toi_da):
            nhan = []
            for mau_du_lieu in X:
                khoang_cach = [self._khoang_cach_euclide(mau_du_lieu, tam) for tam in self.tam_cum]
                nhan.append(np.argmin(khoang_cach))
            nhan = np.array(nhan)

            tam_cum_moi = []
            for i in range(self.so_cum):
                cac_diem = X[nhan == i]
                if len(cac_diem) > 0:
                    tam_cum_moi.append(cac_diem.mean(axis=0))
                else:
                    tam_cum_moi.append(self.tam_cum[i])
            
            tam_cum_moi = np.array(tam_cum_moi)
            if np.all(np.abs(tam_cum_moi - self.tam_cum) < self.dung_sai):
                break
            self.tam_cum = tam_cum_moi
        
        return nhan

import numpy as np

class KMeansTuyChinh:
    def __init__(self, so_cum=3, so_vong_lap_toi_da=100, dung_sai=1e-4, random_state=42):
        self.so_cum = so_cum
        self.so_vong_lap_toi_da = so_vong_lap_toi_da
        self.dung_sai = dung_sai 
        self.tam_cum = None
        self.random_state = random_state

    def tinh_khoang_cach_euclid(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2)**2))

    def huan_luyen_va_du_doan(self, X):
        if len(X) < self.so_cum:
             self.so_cum = len(X)
             
        rng = np.random.RandomState(self.random_state)
        chi_so_ngau_nhien = rng.choice(X.shape[0], self.so_cum, replace=False)
        self.tam_cum = X[chi_so_ngau_nhien]

        for _ in range(self.so_vong_lap_toi_da):
            nhan_du_doan = []
            for mau_du_lieu in X:
                khoang_cach = [self.tinh_khoang_cach_euclid(mau_du_lieu, tam) for tam in self.tam_cum]
                nhan_du_doan.append(np.argmin(khoang_cach))
            nhan_du_doan = np.array(nhan_du_doan)

            tam_cum_moi = []
            for i in range(self.so_cum):
                cac_diem_thuoc_cum = X[nhan_du_doan == i]
                if len(cac_diem_thuoc_cum) > 0:
                    tam_cum_moi.append(cac_diem_thuoc_cum.mean(axis=0))
                else:
                    tam_cum_moi.append(self.tam_cum[i])
            
            tam_cum_moi = np.array(tam_cum_moi)
            if np.all(np.abs(tam_cum_moi - self.tam_cum) < self.dung_sai):
                break
            self.tam_cum = tam_cum_moi
        
        return nhan_du_doan

class HoiQuyLogisticTuyChinh:
    def __init__(self, toc_do_hoc=0.01, so_vong_lap=3000, lamda=5.0, batch_size=64, patience=50):
        self.toc_do_hoc = toc_do_hoc
        self.so_vong_lap = so_vong_lap
        self.lamda = lamda 
        self.batch_size = batch_size
        self.patience = patience
        self.trong_so = None
        self.he_so_tu_do = None
        self.cac_lop = np.array(['Negative', 'Neutral', 'Positive']) 
        self.X_mean = None
        self.X_std = None

    def _ham_softmax(self, z):
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    def _tinh_loss(self, y_true_soft, y_pred):
        y_pred_clipped = np.clip(y_pred, 1e-9, 1 - 1e-9)
        return -np.mean(np.sum(y_true_soft * np.log(y_pred_clipped), axis=1))

    def huan_luyen(self, X, y_soft):
        np.random.seed(42)
        so_mau, so_dac_trung = X.shape
        so_lop = y_soft.shape[1]
        
        # Chuẩn hóa dữ liệu đầu vào (Z-score normalization)
        self.X_mean = np.mean(X, axis=0)
        self.X_std = np.std(X, axis=0) + 1e-8
        X_norm = (X - self.X_mean) / self.X_std

        self.trong_so = np.zeros((so_dac_trung, so_lop))
        self.he_so_tu_do = np.zeros((1, so_lop))

        best_loss = float('inf')
        epochs_no_improve = 0

        for vong_lap in range(self.so_vong_lap):
            chi_so = np.arange(so_mau)
            np.random.shuffle(chi_so)
            X_shuffled = X_norm[chi_so]
            y_shuffled = y_soft[chi_so]
            
            toc_do_hien_tai = self.toc_do_hoc / (1 + 0.001 * vong_lap)

            for i in range(0, so_mau, self.batch_size):
                X_batch = X_shuffled[i:i+self.batch_size]
                y_batch = y_shuffled[i:i+self.batch_size]
                so_mau_batch = X_batch.shape[0]

                mo_hinh_tuyen_tinh = np.dot(X_batch, self.trong_so) + self.he_so_tu_do
                y_du_doan = self._ham_softmax(mo_hinh_tuyen_tinh)
                
                sai_so = y_du_doan - y_batch
                
                dao_ham_trong_so = (1 / so_mau_batch) * np.dot(X_batch.T, sai_so) + (self.lamda / so_mau) * self.trong_so
                dao_ham_he_so = (1 / so_mau_batch) * np.sum(sai_so, axis=0) 
                
                # Gradient Clipping để tránh bùng nổ gradient
                dao_ham_trong_so = np.clip(dao_ham_trong_so, -5.0, 5.0)
                dao_ham_he_so = np.clip(dao_ham_he_so, -5.0, 5.0)
                
                self.trong_so -= toc_do_hien_tai * dao_ham_trong_so
                self.he_so_tu_do -= toc_do_hien_tai * dao_ham_he_so

            # Tính Loss toàn tập để Early Stopping
            y_du_doan_toan_tap = self._ham_softmax(np.dot(X_norm, self.trong_so) + self.he_so_tu_do)
            current_loss = self._tinh_loss(y_soft, y_du_doan_toan_tap)

            if current_loss < best_loss - 1e-4:
                best_loss = current_loss
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1

            if epochs_no_improve >= self.patience:
                break

    def du_doan(self, X):
        X_norm = (X - self.X_mean) / self.X_std
        mo_hinh_tuyen_tinh = np.dot(X_norm, self.trong_so) + self.he_so_tu_do
        xac_suat_du_bao = self._ham_softmax(mo_hinh_tuyen_tinh)
        chi_so_lop = np.argmax(xac_suat_du_bao, axis=1)
        return np.array([self.cac_lop[i] for i in chi_so_lop])
    