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

        self.image_paths = []  # Lưu toàn bộ đường dẫn ảnh cho Ctrl+A
        self.selected_paths = set()  # Lưu các đường dẫn đang được highlight (Multi-select)

        self.current_path = None
        self.is_gray_mode = False

        self.current_working_img = None
        self.selection_box = None
        self.drag_start = None

        self.image_cache = {}
        self.image_params = {}

    def handle_add_image(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_extensions):
                full_path = os.path.join(folder_path, filename)
                thumbnail = self.processor.process_for_tkinter(full_path, 100, 100)
                if thumbnail:
                    self.image_list.append(thumbnail)
                    self.image_paths.append(full_path)
                    self.view.add_thumbnail_to_grid(thumbnail, full_path)

    def handle_select_all(self):
        if not self.image_paths: return
        self.selected_paths = set(self.image_paths)
        self.view.highlight_thumbnail(self.selected_paths)

    def handle_image_selection(self, path, is_multi=False):
        # 1. Lưu tham số của ảnh ĐANG HIỂN THỊ trước khi chuyển sang ảnh mới
        if self.current_path and self.current_path in self.selected_paths:
            self.image_params[self.current_path] = {
                'log_c': self.view.slider_c.get(),
                'gamma_c_off': self.view.slider_gc.get(),
                'gamma_y_off': self.view.slider_gy.get()
            }

        # 2. Xử lý Multi-select bằng phím Control/Command
        if is_multi:
            if path in self.selected_paths:
                self.selected_paths.remove(path)
                # Nếu lỡ tay bỏ chọn ảnh đang xem ở chính giữa, lùi về xem ảnh liền trước đó trong tệp
                if path == self.current_path:
                    self.current_path = list(self.selected_paths)[-1] if self.selected_paths else None
            else:
                self.selected_paths.add(path)
                self.current_path = path
        else:
            # Chọn đơn lẻ bình thường
            self.selected_paths = {path}
            self.current_path = path

        self.view.highlight_thumbnail(self.selected_paths)

        # Xóa khung ROI đang làm dở
        self.selection_box = None
        if hasattr(self.view, 'btn_update_region'):
            self.view.btn_update_region.pack_forget()

        # Nếu không còn ảnh nào được chọn (khi bấm bỏ chọn ảnh duy nhất), hủy nạp ảnh
        if not self.current_path:
            return

        self.is_gray_mode = False

        # 3. Nạp ảnh mới vào preview
        target_path = self.current_path
        if target_path in self.image_cache:
            self.current_working_img = self.image_cache[target_path].copy()
        else:
            self.current_working_img = self.processor.get_cv_image(target_path)

        # 4. Phục hồi tham số thanh trượt tương ứng với ảnh
        params = self.image_params.get(target_path, {'log_c': 0.0, 'gamma_c_off': 0.0, 'gamma_y_off': 0.0})

        self.view.slider_c.set(params['log_c'])
        self.view.slider_gc.set(params['gamma_c_off'])
        self.view.slider_gy.set(params['gamma_y_off'])

        self.view.c_val_entry.delete(0, "end");
        self.view.c_val_entry.insert(0, f"{params['log_c']:.1f}")
        self.view.gc_val_entry.delete(0, "end");
        self.view.gc_val_entry.insert(0, f"{params['gamma_c_off']:.1f}")
        self.view.gy_val_entry.delete(0, "end");
        self.view.gy_val_entry.insert(0, f"{params['gamma_y_off']:.2f}")

        # Áp dụng tham số
        if self.current_working_img is not None:
            self.handle_combined_transform()

        img_r, img_g, img_b = self.processor.process_rgb_layers_for_tkinter(target_path, 150, 150)
        if img_r and img_g and img_b:
            self.view.update_rgb_preview(img_r, img_g, img_b)

    def handle_grayscale(self):
        if self.current_path:
            self.is_gray_mode = True
            gray_cv = self.processor.get_cv_image(self.current_path, is_grayscale=True)
            if gray_cv is not None:
                self.current_working_img = gray_cv.copy()
                self.image_cache[self.current_path] = self.current_working_img.copy()

                self._sync_thumbnail()
                self.handle_combined_transform()

    def handle_restart(self):
        if self.current_path:
            self.is_gray_mode = False
            original_cv = self.processor.get_cv_image(self.current_path)
            if original_cv is not None:
                self.current_working_img = original_cv.copy()

                if self.current_path in self.image_cache:
                    del self.image_cache[self.current_path]
                if self.current_path in self.image_params:
                    del self.image_params[self.current_path]

                self.selection_box = None
                if hasattr(self.view, 'btn_update_region'):
                    self.view.btn_update_region.pack_forget()

                self._sync_thumbnail()
                self.handle_combined_transform()

    def handle_loop_transform(self):
        if not self.current_path:
            return

        original_working_img = self.processor.get_cv_image(self.current_path, self.is_gray_mode)
        if original_working_img is None: return

        for i in range(1, 51):
            total_angle = i * 15
            total_scale = 0.9 ** i
            current_frame = self.processor.rotate_and_resize_cv(original_working_img, total_angle, total_scale)
            self._display_current_cv_image(current_frame)
            time.sleep(0.02)

        for i in range(49, -1, -1):
            total_angle = i * 15
            total_scale = 0.9 ** i
            current_frame = self.processor.rotate_and_resize_cv(original_working_img, total_angle, total_scale)
            self._display_current_cv_image(current_frame)
            time.sleep(0.02)

        self.handle_combined_transform()

    def handle_crop_sequence(self):
        if not self.current_path:
            return

        working_img = self.processor.get_cv_image(self.current_path, self.is_gray_mode)
        if working_img is None: return

        overlay_img = self.processor.create_crop_overlay(working_img)
        self._display_current_cv_image(overlay_img)

        self.view.update()
        time.sleep(1)

        cropped_img = self.processor.extract_center_quarter(working_img)
        self.current_working_img = cropped_img.copy()

        self.image_cache[self.current_path] = self.current_working_img.copy()

        self.selection_box = None
        if hasattr(self.view, 'btn_update_region'):
            self.view.btn_update_region.pack_forget()

        self._sync_thumbnail()
        self.handle_combined_transform()

    def handle_log_transform(self, c_value):
        self.view.c_val_entry.delete(0, "end");
        self.view.c_val_entry.insert(0, f"{c_value:.1f}")
        self.handle_combined_transform()

    def handle_gamma_transform(self, c_val, gamma_val):
        self.view.gc_val_entry.delete(0, "end");
        self.view.gc_val_entry.insert(0, f"{c_val:.1f}")
        self.view.gy_val_entry.delete(0, "end");
        self.view.gy_val_entry.insert(0, f"{gamma_val:.2f}")
        self.handle_combined_transform()

    def _map_coordinates(self, x, y, label_w, label_h):
        if self.current_working_img is None: return 0, 0
        h_orig, w_orig = self.current_working_img.shape[:2]
        ratio = min(850 / w_orig, 850 / h_orig)
        disp_w, disp_h = int(w_orig * ratio), int(h_orig * ratio)

        offset_x = (label_w - disp_w) // 2
        offset_y = (label_h - disp_h) // 2

        img_x = int((x - offset_x) / ratio)
        img_y = int((y - offset_y) / ratio)
        return img_x, img_y

    def on_mouse_down(self, x, y, label_w, label_h):
        if self.current_working_img is None: return
        self.drag_start = self._map_coordinates(x, y, label_w, label_h)
        self.selection_box = None

    def on_mouse_drag(self, x, y, label_w, label_h):
        if not self.drag_start or self.current_working_img is None: return
        img_x, img_y = self._map_coordinates(x, y, label_w, label_h)

        x1 = min(self.drag_start[0], img_x)
        y1 = min(self.drag_start[1], img_y)
        x2 = max(self.drag_start[0], img_x)
        y2 = max(self.drag_start[1], img_y)

        h, w = self.current_working_img.shape[:2]
        x1, x2 = max(0, min(w - 1, x1)), max(0, min(w - 1, x2))
        y1, y2 = max(0, min(h - 1, y1)), max(0, min(h - 1, y2))

        if x2 - x1 > 5 and y2 - y1 > 5:
            self.selection_box = (x1, y1, x2, y2)
            self.handle_combined_transform()

    def on_mouse_up(self):
        if self.selection_box:
            if hasattr(self.view, 'btn_update_region'):
                self.view.btn_update_region.pack(side="right", padx=(0, 10), pady=(30, 0))
            self.drag_start = None

    def handle_combined_transform(self):
        if self.current_working_img is None: return

        img = self.current_working_img.copy()

        log_c = self.view.slider_c.get()
        gamma_c_off = self.view.slider_gc.get()
        gamma_y_off = self.view.slider_gy.get()

        if self.selection_box:
            x1, y1, x2, y2 = self.selection_box
            roi = img[y1:y2, x1:x2].copy()

            roi = ColorProcessor.apply_log_transform(roi, log_c)
            roi = ColorProcessor.apply_gamma_transform(roi, gamma_c_off, gamma_y_off)

            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (img.shape[1], img.shape[0]), (30, 30, 30), -1)
            cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

            img[y1:y2, x1:x2] = roi
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
        else:
            img = ColorProcessor.apply_log_transform(img, log_c)
            img = ColorProcessor.apply_gamma_transform(img, gamma_c_off, gamma_y_off)

        self._display_current_cv_image(img)
        self._sync_thumbnail(preview_img=img)

    def handle_update_region(self):
        if not self.selection_box or self.current_working_img is None: return

        log_c = self.view.slider_c.get()
        gamma_c_off = self.view.slider_gc.get()
        gamma_y_off = self.view.slider_gy.get()

        x1, y1, x2, y2 = self.selection_box
        roi = self.current_working_img[y1:y2, x1:x2]

        roi = ColorProcessor.apply_log_transform(roi, log_c)
        roi = ColorProcessor.apply_gamma_transform(roi, gamma_c_off, gamma_y_off)
        self.current_working_img[y1:y2, x1:x2] = roi

        self.image_cache[self.current_path] = self.current_working_img.copy()

        self.selection_box = None
        if hasattr(self.view, 'btn_update_region'):
            self.view.btn_update_region.pack_forget()

        self.view.slider_c.set(0.0);
        self.view.slider_gc.set(0.0);
        self.view.slider_gy.set(0.0)
        self.view.c_val_entry.delete(0, "end");
        self.view.c_val_entry.insert(0, "0.0")
        self.view.gc_val_entry.delete(0, "end");
        self.view.gc_val_entry.insert(0, "0.0")
        self.view.gy_val_entry.delete(0, "end");
        self.view.gy_val_entry.insert(0, "0.00")

        if self.current_path in self.image_params:
            self.image_params[self.current_path] = {'log_c': 0.0, 'gamma_c_off': 0.0, 'gamma_y_off': 0.0}

        self._sync_thumbnail()
        self.handle_combined_transform()

    def handle_export(self):
        # Xuất file đồng loạt đối với toàn bộ các ảnh được đánh dấu trong selected_paths
        if not self.selected_paths:
            return

        export_dir = filedialog.askdirectory(title="Chọn thư mục xuất ảnh")
        if not export_dir:
            return

        for path in self.selected_paths:
            # 1. Lấy bản ghi bộ nhớ (đã qua Crop, Gray, ROI...) hoặc ảnh gốc
            if path in self.image_cache:
                out_img = self.image_cache[path].copy()
            else:
                out_img = self.processor.get_cv_image(path)

            if out_img is not None:
                # --- SỬA LỖI 1: ÁP DỤNG THAM SỐ MÀU SẮC (LOG/GAMMA) ---
                # Lấy tham số: Nếu là ảnh đang xem thì lấy trực tiếp từ thanh trượt UI,
                # ngược lại lấy từ bộ nhớ lưu trữ tham số image_params
                if path == self.current_path:
                    log_c = self.view.slider_c.get()
                    gamma_c_off = self.view.slider_gc.get()
                    gamma_y_off = self.view.slider_gy.get()
                else:
                    params = self.image_params.get(path, {'log_c': 0.0, 'gamma_c_off': 0.0, 'gamma_y_off': 0.0})
                    log_c = params['log_c']
                    gamma_c_off = params['gamma_c_off']
                    gamma_y_off = params['gamma_y_off']

                # Áp dụng màu sắc vào ảnh chuẩn bị xuất
                out_img = ColorProcessor.apply_log_transform(out_img, log_c)
                out_img = ColorProcessor.apply_gamma_transform(out_img, gamma_c_off, gamma_y_off)

                # --- SỬA LỖI 2: CHỐNG GHI ĐÈ FILE ---
                original_filename = os.path.basename(path)
                base_name, ext = os.path.splitext(original_filename)

                save_path = os.path.join(export_dir, original_filename)
                counter = 1

                # Kiểm tra nếu file đã tồn tại thì thêm hậu tố _export_1, _export_2...
                while os.path.exists(save_path):
                    new_filename = f"{base_name}{counter}{ext}"
                    save_path = os.path.join(export_dir, new_filename)
                    counter += 1

                # Hàm imencode hỗ trợ việc ghi và xử lý những định dạng đường dẫn có ký tự đặc biệt
                is_success, im_buf_arr = cv2.imencode(ext, out_img)
                if is_success:
                    im_buf_arr.tofile(save_path)

    def _display_current_cv_image(self, cv_img):
        if not self.is_gray_mode:
            display_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        else:
            display_img = cv_img

        photo = self.processor._resize_and_convert(display_img, 900, 900)
        self.view.update_preview(photo)

        hist_photo = ColorProcessor.get_histogram_image(cv_img)
        self.view.update_histogram_view(hist_photo)

        self.view.update()

    def _sync_thumbnail(self, preview_img=None):
        if not self.current_path:
            return

        source_img = preview_img if preview_img is not None else self.current_working_img

        if source_img is None:
            return

        display_img = source_img.copy()
        if not self.is_gray_mode:
            display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

        thumb_photo = self.processor._resize_and_convert(display_img, 100, 100)
        self.view.update_thumbnail_image(self.current_path, thumb_photo)