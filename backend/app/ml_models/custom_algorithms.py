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

class HoiQuyLogisticTuyChinh:
    def __init__(self, toc_do_hoc=0.1, so_vong_lap=3000, lamda=1.0):
        self.toc_do_hoc = toc_do_hoc
        self.so_vong_lap = so_vong_lap
        self.trong_so = None
        self.do_lech = None # bias
        self.cac_lop = None
        self.trong_so_lop = {}
        self.lamda = lamda

    def _ham_softmax(self, z):
        e_mu_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return e_mu_z / np.sum(e_mu_z, axis=1, keepdims=True)

    def _ma_hoa_one_hot(self, y):
        so_mau = len(y)
        # Fix lỗi: Nếu chỉ có 1 class (vd toàn Positive)
        cac_lop_duy_nhat = np.unique(y)
        if len(self.cac_lop) > len(cac_lop_duy_nhat):
             # Map lại cho đúng index của self.cac_lop
             pass 

        so_luong_lop = len(self.cac_lop)
        mang_one_hot = np.zeros((so_mau, so_luong_lop))
        for i, nhan_du_lieu in enumerate(y):
            if nhan_du_lieu in self.cac_lop:
                chi_so_lop = np.where(self.cac_lop == nhan_du_lieu)[0][0]
                mang_one_hot[i, chi_so_lop] = 1
        return mang_one_hot
    
    def _tinh_trong_so_lop(self, y):
        tong_mau = len(y)
        lop, so_luong = np.unique(y, return_counts=True)
        for l, count in zip(lop, so_luong):
            trong_so = np.log(tong_mau / count) + 1.0
            self.trong_so_lop[l] = min(max(trong_so, 0.5), 3.0)

    def huan_luyen(self, X, y):
        self.cac_lop = np.unique(y)
        so_mau, so_dac_trung = X.shape
        so_luong_lop = len(self.cac_lop)
        
        # Nếu chỉ có 1 class, không cần train, predict luôn trả về class đó
        if so_luong_lop < 2:
            return

        self._tinh_trong_so_lop(y)
        self.trong_so = np.zeros((so_dac_trung, so_luong_lop))
        self.do_lech = np.zeros((1, so_luong_lop))
        y_da_ma_hoa = self._ma_hoa_one_hot(y)

        trong_so_tung_mau = np.array([self.trong_so_lop[nhan] for nhan in y]).reshape(-1, 1)

        for vong_lap in range(self.so_vong_lap):
            # Cập nhật: Giảm dần tốc độ học giúp mô hình hội tụ tốt hơn
            toc_do_hien_tai = self.toc_do_hoc / (1 + 0.001 * vong_lap)
            
            mo_hinh_tuyen_tinh = np.dot(X, self.trong_so) + self.do_lech
            y_du_doan = self._ham_softmax(mo_hinh_tuyen_tinh)
            
            sai_so = (y_du_doan - y_da_ma_hoa) * trong_so_tung_mau
            
            dao_ham_trong_so = (1 / so_mau) * np.dot(X.T, sai_so) + (self.lamda / so_mau) * self.trong_so
            dao_ham_do_lech = (1 / so_mau) * np.sum(sai_so, axis=0)
            
            self.trong_so -= toc_do_hien_tai * dao_ham_trong_so
            self.do_lech -= toc_do_hien_tai * dao_ham_do_lech

    def du_doan(self, X):
        if self.trong_so is None: # Trường hợp data chỉ có 1 class
            return np.array([self.cac_lop[0]] * len(X))

        mo_hinh_tuyen_tinh = np.dot(X, self.trong_so) + self.do_lech
        xac_suat_y_du_doan = self._ham_softmax(mo_hinh_tuyen_tinh)
        chi_so_cac_lop = np.argmax(xac_suat_y_du_doan, axis=1)
        return np.array([self.cac_lop[i] for i in chi_so_cac_lop])
    