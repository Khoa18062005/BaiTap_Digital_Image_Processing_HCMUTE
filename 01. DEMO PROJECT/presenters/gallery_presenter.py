import time
import cv2
import os
from tkinter import filedialog
from core.color_processor import ColorProcessor
class GalleryPresenter:
    def __init__(self, view, image_processor):
        self.view = view
        self.processor = image_processor
        self.image_list = []
        self.current_path = None  # Lưu lại ảnh đang được chọn
        self.is_gray_mode = False # Lưu trạng thái ảnh

    def handle_add_image(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

        # Duyệt qua tất cả file trong thư mục
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_extensions):
                # Tạo đường dẫn đầy đủ cho từng ảnh
                full_path = os.path.join(folder_path, filename)
                thumbnail = self.processor.process_for_tkinter(full_path, 100, 100)
                if thumbnail:
                    self.image_list.append(thumbnail)
                    self.view.add_thumbnail_to_grid(thumbnail, full_path)

    def handle_image_selection(self, path):
        self.current_path = path
        self.is_gray_mode = False
        # Xử lý ảnh gốc to
        big_img = self.processor.process_for_tkinter(path, 600, 600)
        self.view.update_preview(big_img)

        # Xử lý 3 lớp màu RGB
        img_r, img_g, img_b = self.processor.process_rgb_layers_for_tkinter(path, 150, 150)
        if img_r and img_g and img_b:
            self.view.update_rgb_preview(img_r, img_g, img_b)

    def handle_grayscale(self):
        if self.current_path:
            self.is_gray_mode = True
            # Lấy ảnh xám từ processor dựa trên ảnh đang hiển thị
            gray_img = self.processor.process_grayscale_for_tkinter(self.current_path, 600, 600)
            if gray_img:
                # Ghi đè tấm ảnh xám vào vị trí tấm ảnh to trên View
                self.view.update_preview(gray_img)

    def handle_restart(self):
        if self.current_path:
            self.is_gray_mode = False
            # Gọi lại hàm xử lý ảnh gốc màu
            original_color_img = self.processor.process_for_tkinter(self.current_path, 600, 600)
            if original_color_img:
                # Cập nhật lại khung hiển thị Preview
                self.view.update_preview(original_color_img)

    def handle_loop_transform(self):
        if not self.current_path:
            return
        # Lấy ảnh gốc "xịn" nhất để làm gốc tính toán
        original_working_img = self.processor.get_cv_image(self.current_path, self.is_gray_mode)
        if original_working_img is None: return
        # Thu nhỏ ảnh 50 lần
        for i in range(1, 51):
            total_angle = i * 15
            total_scale = 0.9 ** i  # 0.9 lũy thừa i
            # Thực hiện xoay từ ảnh gốc
            current_frame = self.processor.rotate_and_resize_cv(
                original_working_img, total_angle, total_scale
            )
            self._display_current_cv_image(current_frame)
            time.sleep(0.02)
        # Phóng to ảnh 50 lần
        for i in range(49, -1, -1):  # Chạy ngược từ 49 về 0
            total_angle = i * 15
            total_scale = 0.9 ** i
            current_frame = self.processor.rotate_and_resize_cv(
                original_working_img, total_angle, total_scale
            )
            self._display_current_cv_image(current_frame)
            time.sleep(0.02)

    def _display_current_cv_image(self, cv_img):
        if not self.is_gray_mode:
            display_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        else:
            display_img = cv_img

        photo = self.processor._resize_and_convert(display_img, 600, 600)
        self.view.update_preview(photo)
        self.view.update()

    def handle_crop_sequence(self):
        if not self.current_path:
            return

        # Lấy ảnh hiện tại (màu hoặc xám tùy trạng thái)
        working_img = self.processor.get_cv_image(self.current_path, self.is_gray_mode)
        if working_img is None: return

        # Hiển thị vùng xám nhạt (Overlay)
        overlay_img = self.processor.create_crop_overlay(working_img)
        self._display_current_cv_image(overlay_img)

        self.view.update()
        time.sleep(1)

        # Thực hiện cắt ảnh
        cropped_img = self.processor.extract_center_quarter(working_img)

        # 4. Hiển thị kết quả cuối cùng
        self._display_current_cv_image(cropped_img)


    # Điều phối Log Transform
    def handle_log_transform(self, c_value):
        # Cập nhật số hiển thị trong Entry của View
        self.view.c_val_entry.delete(0, "end")
        self.view.c_val_entry.insert(0, f"{c_value:.1f}")
        self.handle_combined_transform()

    # Điều phối Gamma Transform
    def handle_gamma_transform(self, c_val, gamma_val):
        # Cập nhật số hiển thị trong Entry của View
        self.view.gc_val_entry.delete(0, "end")
        self.view.gc_val_entry.insert(0, f"{c_val:.1f}")
        self.view.gy_val_entry.delete(0, "end")
        self.view.gy_val_entry.insert(0, f"{gamma_val:.2f}")
        self.handle_combined_transform()

    # Điều phối cộng dồn hiệu ứng
    def handle_combined_transform(self):
        if not self.current_path: return

        # Lấy ảnh gốc (hoặc xám)
        img = self.processor.get_cv_image(self.current_path, self.is_gray_mode)
        if img is None: return

        # Lấy offset từ UI[cite: 4]
        log_c = self.view.slider_c.get()  # 0 = No effect
        gamma_c_off = self.view.slider_gc.get()  # 0 = c là 1.0
        gamma_y_off = self.view.slider_gy.get()  # 0 = y là 1.0

        # Pipeline xử lý cộng dồn
        img = ColorProcessor.apply_log_transform(img, log_c)
        img = ColorProcessor.apply_gamma_transform(img, gamma_c_off, gamma_y_off)

        # Hiển thị kết quả
        self._display_current_cv_image(img)