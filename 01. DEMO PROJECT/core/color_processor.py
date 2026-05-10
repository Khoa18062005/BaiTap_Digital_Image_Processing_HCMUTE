import cv2
import numpy as np


class ColorProcessor:
    @staticmethod
    def apply_log_transform(cv_img, c_value):
        # Nếu c = 0, coi như không có biến đổi, trả về ảnh gốc
        if cv_img is None or c_value == 0:
            return cv_img

        has_alpha = cv_img.shape[-1] == 4
        bgr = cv_img[:, :, :3] if has_alpha else cv_img

        # Công thức: s = c * ln(1 + r)[cite: 1]
        bgr_float = np.float32(bgr)
        transformed = c_value * np.log2(1 + bgr_float)

        res = np.clip(transformed, 0, 255).astype(np.uint8)
        return cv2.merge((res, cv_img[:, :, 3])) if has_alpha else res

    @staticmethod
    def apply_gamma_transform(cv_img, c_offset, gamma_offset):
        # Mặc định c=1.0 và gamma=1.0 là trạng thái giữ nguyên ảnh[cite: 1]
        # Chúng ta tính toán dựa trên độ lệch (offset) từ người dùng
        actual_c = 1.0 + c_offset
        actual_gamma = 1.0 + gamma_offset

        if cv_img is None: return None
        # Nếu cả hai offset đều là 0, trả về ảnh gốc[cite: 1]
        if c_offset == 0 and gamma_offset == 0:
            return cv_img

        has_alpha = cv_img.shape[-1] == 4
        bgr = cv_img[:, :, :3] if has_alpha else cv_img

        # Công thức: s = c * (r/255)^gamma * 255[cite: 1]
        img_normalized = bgr / 255.0
        res_gamma = actual_c * np.power(img_normalized, actual_gamma)

        res_uint8 = np.clip(res_gamma * 255.0, 0, 255).astype(np.uint8)
        return cv2.merge((res_uint8, cv_img[:, :, 3])) if has_alpha else res_uint8