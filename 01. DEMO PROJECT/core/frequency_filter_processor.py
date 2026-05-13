import numpy as np
import cv2

class FrequencyFilterProcessor:
    @staticmethod
    def create_distance_matrix(shape):
        M, N = shape
        u = np.arange(M)
        v = np.arange(N)
        u, v = np.meshgrid(u, v, indexing='ij')
        # Tính khoảng cách D(u,v) từ tâm [cite: 1]
        D = np.sqrt((u - M/2)**2 + (v - N/2)**2)
        return D

    @staticmethod
    def apply_filter(cv_img, mask):
        """
        Áp dụng mask cho ảnh màu hoặc ảnh xám
        """
        if len(cv_img.shape) == 3:
            channels = cv2.split(cv_img)
            result_channels = []

            for ch in channels:
                # 1. Chuyển sang tần số
                f_shift = np.fft.fftshift(np.fft.fft2(ch))
                # 2. Nhân với Mask (Mask này dùng chung cho cả 3 kênh)
                res_shift = f_shift * mask
                # 3. Biến đổi ngược
                f_ishift = np.fft.ifftshift(res_shift)
                img_back = np.abs(np.fft.ifft2(f_ishift))
                result_channels.append(img_back)

            # Gộp và chuẩn hóa tổng thể
            merged = cv2.merge(result_channels)
            return cv2.normalize(merged, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        else:
            # Logic cho ảnh xám (như cũ)
            f_shift = np.fft.fftshift(np.fft.fft2(cv_img))
            res_shift = f_shift * mask
            f_ishift = np.fft.ifftshift(res_shift)
            img_back = np.abs(np.fft.ifft2(f_ishift))
            return cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # --- LOW PASS FILTERS ---
    @staticmethod
    def ideal_low_pass(D, D0):
        return (D <= D0).astype(float) # [cite: 3]

    @staticmethod
    def butterworth_low_pass(D, D0, n):
        return 1 / (1 + (D / D0)**(2 * n)) # [cite: 5]

    @staticmethod
    def gaussian_low_pass(D, D0):
        return np.exp(-(D**2) / (2 * (D0**2))) # [cite: 8]

    # --- HIGH PASS FILTERS ---
    @staticmethod
    def ideal_high_pass(D, D0):
        return (D > D0).astype(float) # [cite: 13]

    @staticmethod
    def butterworth_high_pass(D, D0, n):
        # Tránh chia cho 0 tại tâm bằng cách thêm epsilon nhỏ
        return 1 / (1 + (D0 / (D + 1e-9))**(2 * n)) # [cite: 15]

    @staticmethod
    def gaussian_high_pass(D, D0):
        return 1 - np.exp(-(D**2) / (2 * (D0**2))) # [cite: 16]