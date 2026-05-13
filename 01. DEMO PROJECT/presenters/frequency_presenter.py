import numpy as np
import os
import cv2
from tkinter import filedialog
from core.frequency_image_processor import FrequencyImageProcessor
from core.frequency_filter_processor import FrequencyFilterProcessor
from ui.frequency_filter_view import FrequencyFilterView
from PIL import Image
import customtkinter as ctk
class FrequencyPresenter:
    def __init__(self, view, image_processor):
        self.view = view
        self.processor = image_processor
        self.image_list = []
        self.image_paths = []
        self.selected_paths = set()
        self.current_path = None
        self.current_working_img = None

    def handle_add_image(self):
        # Tái sử dụng logic mở folder giống hệ không gian
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_extensions):
                full_path = os.path.join(folder_path, filename)
                # Tái sử dụng ImageProcessor đã có
                thumbnail = self.processor.process_for_tkinter(full_path, 100, 100)
                if thumbnail:
                    self.image_list.append(thumbnail)
                    self.image_paths.append(full_path)
                    self.view.add_thumbnail_to_grid(thumbnail, full_path)

    def handle_image_selection(self, path, is_multi=False):
        # Xử lý chọn ảnh cơ bản
        self.selected_paths = {path}
        self.current_path = path

        self.view.highlight_thumbnail(self.selected_paths)

        # Đọc ảnh thông qua ImageProcessor
        self.current_working_img = self.processor.get_cv_image(path)

        if self.current_working_img is not None:
            self._display_current_cv_image(self.current_working_img)

    def _display_current_cv_image(self, cv_img):
        # Convert BGR sang RGB để hiển thị trên Tkinter
        display_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        photo = self.processor._resize_and_convert(display_img, 900, 900)
        self.view.update_preview(photo)
        self.view.update()

    def handle_show_fft(self):
        if self.current_working_img is None:
            return

        # Tính toán phổ FFT
        fft_img = FrequencyImageProcessor.compute_fft(self.current_working_img)

        if fft_img is not None:
            # Hiển thị lên preview (Lưu ý: fft_img là ảnh xám)
            photo = self.processor._resize_and_convert(fft_img, 900, 900)
            self.view.update_preview(photo)

    def handle_show_original(self):
        """Hiển thị lại ảnh gốc ban đầu từ đường dẫn hiện tại"""
        if not self.current_path:
            return

        # Sử dụng ImageProcessor để lấy lại ảnh gốc từ đường dẫn[cite: 2]
        self.current_working_img = self.processor.get_cv_image(self.current_path)

        if self.current_working_img is not None:
            # Gọi hàm hiển thị chuẩn đã viết
            self._display_current_cv_image(self.current_working_img)

    def handle_open_filter_pass(self):
        # SỬA TẠI ĐÂY: Lấy trực tiếp từ Presenter thay vì bắt View trả về
        if self.current_working_img is None:
            print("Không tìm thấy ảnh để xử lý!")
            return

        img_to_process = self.current_working_img

        # 2. TẠO BIẾN small_img ĐỂ TÍNH TOÁN NHANH (Giữ nguyên màu BGR)
        h, w = img_to_process.shape[:2]
        preview_h = 400
        preview_w = int(w * (preview_h / h))
        self.small_img = cv2.resize(img_to_process, (preview_w, preview_h))

        # 3. Tạo ma trận khoảng cách
        self.D_matrix_cache = FrequencyFilterProcessor.create_distance_matrix(self.small_img.shape[:2])

        # 4. Mở cửa sổ Filter View
        self.filter_view = FrequencyFilterView(self.view, self)

        # 5. Gọi cập nhật lần đầu
        self.update_filter()

    def update_filter(self):
        if not hasattr(self, 'small_img') or self.small_img is None:
            return

        c = self.filter_view.controls
        D = self.D_matrix_cache

        configs = [
            ("ilp", FrequencyFilterProcessor.ideal_low_pass, [c["ilp"]["d0"].get()]),
            ("blp", FrequencyFilterProcessor.butterworth_low_pass, [c["blp"]["d0"].get(), c["blp"]["n"].get()]),
            ("glp", FrequencyFilterProcessor.gaussian_low_pass, [c["glp"]["d0"].get()]),
            ("ihp", FrequencyFilterProcessor.ideal_high_pass, [c["ihp"]["d0"].get()]),
            ("bhp", FrequencyFilterProcessor.butterworth_high_pass, [c["bhp"]["d0"].get(), c["bhp"]["n"].get()]),
            ("ghp", FrequencyFilterProcessor.gaussian_high_pass, [c["ghp"]["d0"].get()])
        ]

        for key, func, params in configs:
            mask = func(D, *params)
            # Apply_filter giờ xử lý được cả ảnh màu RGB/BGR
            res_np = FrequencyFilterProcessor.apply_filter(self.small_img, mask)

            # SỬA LỖI HIỂN THỊ TRÊN MAC: Chuyển sang RGB và dùng CTkImage
            res_rgb = cv2.cvtColor(res_np, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(res_rgb)

            ctk_img = ctk.CTkImage(
                light_image=img_pil,
                dark_image=img_pil,
                size=(300, 240)  # Kích thước hiển thị trong lưới
            )

            self.filter_view.image_labels[key].configure(image=ctk_img, text="")
            self.filter_view.image_labels[key]._image = ctk_img  # Giữ tham chiếu

        self.filter_view.update_idletasks()