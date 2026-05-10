import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessor:
    @staticmethod
    def _resize_and_convert(cv_img_rgb, max_w, max_h):
        h_orig, w_orig = cv_img_rgb.shape[:2]
        ratio = min(max_w / w_orig, max_h / h_orig)
        new_w, new_h = int(w_orig * ratio), int(h_orig * ratio)

        interp = cv2.INTER_LANCZOS4 if ratio > 1 else cv2.INTER_AREA
        img_resized = cv2.resize(cv_img_rgb, (new_w, new_h), interpolation=interp)

        return ImageTk.PhotoImage(Image.fromarray(img_resized))

    @staticmethod
    def process_for_tkinter(image_path, max_w, max_h):
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None: return None

        # Logic xử lý màu sắc chuẩn của bạn
        if len(img.shape) == 4 or (len(img.shape) == 3 and img.shape[2] == 4):
            img_correct = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            img_correct = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return ImageProcessor._resize_and_convert(img_correct, max_w, max_h)

    # Xử lý tách màu thành 3 kênh
    @staticmethod
    def process_rgb_layers_for_tkinter(image_path, max_w, max_h):
        img = cv2.imread(image_path)
        if img is None: return None, None, None

        b, g, r = cv2.split(img)
        zeros = np.zeros_like(b)

        # Tạo 3 lớp màu (Hệ BGR của OpenCV)
        layers_bgr = [
            cv2.merge([zeros, zeros, r]),  # Lớp Red
            cv2.merge([zeros, g, zeros]),  # Lớp Green
            cv2.merge([b, zeros, zeros])  # Lớp Blue
        ]

        # Duyệt qua các lớp, convert sang RGB rồi gọi hàm resize dùng chung
        results = []
        for layer_bgr in layers_bgr:
            layer_rgb = cv2.cvtColor(layer_bgr, cv2.COLOR_BGR2RGB)
            results.append(ImageProcessor._resize_and_convert(layer_rgb, max_w, max_h))

        return results[0], results[1], results[2]

    # Xử lý chuyển màu xám cho ảnh
    @staticmethod
    def process_grayscale_for_tkinter(image_path, max_w, max_h):
        # 1. Đọc ảnh giữ nguyên kênh Alpha (Mượn ý tưởng từ hàm của bạn)
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None: return None

        # 2. Kiểm tra nếu là ảnh 4 kênh (có Alpha)
        if len(img.shape) == 4 or (len(img.shape) == 3 and img.shape[2] == 4):
            # Tách kênh BGR và kênh Alpha
            bgr = img[:, :, :3]
            alpha = img[:, :, 3] / 255.0

            # Tạo một nền trắng (White Background) có cùng kích thước
            white_bg = np.ones_like(bgr, dtype=np.uint8) * 255

            # Công thức Alpha Blending để "dán" ảnh lên nền trắng:
            img_final = cv2.convertScaleAbs(bgr * alpha[..., None] + white_bg * (1 - alpha[..., None]))

            # Chuyển ảnh sau khi dán nền sang màu xám
            gray_img = cv2.cvtColor(img_final, cv2.COLOR_BGR2GRAY)
        else:
            # Nếu là ảnh 3 kênh bình thường, chuyển BGR sang Gray trực tiếp
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Sử dụng hàm dùng chung để resize và trả về PhotoImage[cite: 1]
        return ImageProcessor._resize_and_convert(gray_img, max_w, max_h)

    # Xử lý xoay hình ảnh
    @staticmethod
    def rotate_and_resize_cv(cv_img, angle, scale):
        (h, w) = cv_img.shape[:2]
        center = (w // 2, h // 2)

        # Tạo ma trận xoay
        M = cv2.getRotationMatrix2D(center, angle, scale)
        bg_color = (255, 255, 255) if len(cv_img.shape) == 3 else 255
        # Thực hiện biến đổi
        transformed = cv2.warpAffine(cv_img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=bg_color, flags=cv2.INTER_LINEAR,)
        return transformed

    @staticmethod
    def get_cv_image(image_path, is_grayscale=False):
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None: return None
        if is_grayscale:
            if len(img.shape) == 4 or (len(img.shape) == 3 and img.shape[2] == 4):
                bgr = img[:, :, :3]
                alpha = img[:, :, 3] / 255.0
                white_bg = np.ones_like(bgr, dtype=np.uint8) * 255
                img = cv2.convertScaleAbs(bgr * alpha[..., None] + white_bg * (1 - alpha[..., None]))
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    # Xử lý crop hình ảnh
    @staticmethod
    def get_crop_bounds(cv_img):
        h, w = cv_img.shape[:2]
        x_start, y_start = w // 4, h // 4
        x_end, y_end = 3 * w // 4, 3 * h // 4
        return x_start, y_start, x_end, y_end

    @staticmethod
    def create_crop_overlay(cv_img):
        """Tạo vùng cắt"""
        overlay = cv_img.copy()
        x1, y1, x2, y2 = ImageProcessor.get_crop_bounds(cv_img)

        # Tạo một bản sao để vẽ lớp phủ
        temp_img = cv_img.copy()
        # Tạo hình chữ nhật
        cv2.rectangle(temp_img, (0, 0), (cv_img.shape[1], cv_img.shape[0]), (200, 200, 200), -1)

        # Trộn ảnh gốc với màu xám (alpha = 0.5)
        cv2.addWeighted(temp_img, 0.5, overlay, 0.5, 0, overlay)

        # Khôi phục vùng trung tâm (giữ nguyên độ sáng để làm nổi bật vùng sẽ cắt)
        overlay[y1:y2, x1:x2] = cv_img[y1:y2, x1:x2]

        return overlay

    @staticmethod
    def extract_center_quarter(cv_img):
        """Thực hiện cắt lấy 1/4 ảnh ở tâm"""
        x1, y1, x2, y2 = ImageProcessor.get_crop_bounds(cv_img)
        cropped = cv_img[y1:y2, x1:x2]
        return cropped

