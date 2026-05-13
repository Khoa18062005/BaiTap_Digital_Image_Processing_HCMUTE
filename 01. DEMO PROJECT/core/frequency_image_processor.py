import cv2
import numpy as np


class FrequencyImageProcessor:
    @staticmethod
    def compute_fft(cv_img):
        if cv_img is None: return None

        # Nếu là ảnh màu (3 kênh)
        if len(cv_img.shape) == 3:
            # Tách các kênh màu
            channels = cv2.split(cv_img)
            magnitude_channels = []

            for ch in channels:
                # FFT từng kênh
                f_transform = np.fft.fft2(ch)
                f_shift = np.fft.fftshift(f_transform)
                # Tính phổ biên độ
                mag = 20 * np.log(np.abs(f_shift) + 1)
                # Chuẩn hóa từng kênh
                mag_norm = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
                magnitude_channels.append(mag_norm.astype(np.uint8))

            # Gộp lại thành ảnh phổ có màu
            return cv2.merge(magnitude_channels)
        else:
            # Xử lý ảnh xám như cũ
            f_transform = np.fft.fft2(cv_img)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
            res_normalized = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
            return res_normalized.astype(np.uint8)