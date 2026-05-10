import customtkinter as ctk
import tkinter as tk

# Cấu hình giao diện chung
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Homework week 01 - design by Nguyen Quoc Khoa 23110116")
        self.geometry("1450x850")  # Tăng chiều rộng để chứa đủ 3 cột

        # --- BẢNG MÀU ---
        self.colors = {
            "bg_main": "#FFFFFF",
            "bg_sidebar": "#F8F9FA",
            "bg_tools": "#2B2B2B",  # Màu nền tối cho thanh công cụ bên phải
            "red_primary": "#D32F2F",
            "red_hover": "#B71C1C",
            "text_main": "#212121",
            "text_dim": "#757575",
            "text_tool": "#CCCCCC",
            "divider": "#3A3A3A"
        }

        self.configure(fg_color=self.colors["bg_main"])
        self.presenter = None
        self.thumb_count = 0

        # ==========================================
        # BỐ CỤC CHÍNH (CẦN TUÂN THỦ THỨ TỰ PACK NÀY)
        # ==========================================

        # 1. PHẦN 1: SIDEBAR TRÁI
        self.sidebar = ctk.CTkFrame(self, width=320, fg_color=self.colors["bg_sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 2. PHẦN 3: TOOL SIDEBAR PHẢI
        self.tool_sidebar = ctk.CTkFrame(self, width=320, fg_color=self.colors["bg_tools"], corner_radius=0)
        self.tool_sidebar.pack(side="right", fill="y")
        self.tool_sidebar.pack_propagate(False)

        # 3. PHẦN 2: MAIN CONTENT GIỮA
        self.main_content = ctk.CTkFrame(self, fg_color=self.colors["bg_main"], corner_radius=0)
        self.main_content.pack(side="left", expand=True, fill="both")

        # Gọi các hàm khởi tạo giao diện con
        self._init_sidebar_widgets()
        self._init_preview_widgets()
        self._init_tool_widgets()

    # ==========================================
    # PHẦN 1: GIAO DIỆN SIDEBAR TRÁI
    # ==========================================
    def _init_sidebar_widgets(self):
        ctk.CTkLabel(
            self.sidebar, text="HOMEWORK 01",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.colors["red_primary"]
        ).pack(pady=(40, 5), padx=25, anchor="center")

        ctk.CTkLabel(
            self.sidebar, text="Professional Image Viewer",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=self.colors["text_dim"]
        ).pack(padx=25, anchor="center", pady=(0, 10))

        self.btn_add = ctk.CTkButton(
            self.sidebar, text="ADD NEW FOLDER",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.colors["red_primary"], hover_color=self.colors["red_hover"],
            text_color="white", height=45, corner_radius=15,
            command=self._on_add_click
        )
        self.btn_add.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#EEEEEE").pack(fill="x", padx=25, pady=10)

        # Scrollable Canvas cho lưới ảnh
        self.canvas = tk.Canvas(self.sidebar, bg=self.colors["bg_sidebar"], highlightthickness=0, borderwidth=0)
        self.scrollbar = ctk.CTkScrollbar(self.sidebar, orientation="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=self.colors["bg_sidebar"])

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=10)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta)), "units")

    # ==========================================
    # PHẦN 2: GIAO DIỆN MAIN CONTENT GIỮA
    # ==========================================
    def _init_preview_widgets(self):
        header = ctk.CTkFrame(self.main_content, fg_color=self.colors["bg_main"], height=80, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="IMAGE PREVIEW",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left", padx=40, pady=(30, 0))

        # Các nút chức năng
        self.btn_grayscale = ctk.CTkButton(
            header, text="CONVERT TO GRAY", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#607D8B", hover_color="#455A64", text_color="white", height=32, width=140, corner_radius=10,
            command=self._on_grayscale_click
        )
        self.btn_grayscale.pack(side="right", padx=(0, 40), pady=(30, 0))

        self.btn_transform = ctk.CTkButton(
            header, text="LOOP TRANSFORM", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#FF9800", hover_color="#F57C00", text_color="white", height=32, width=140, corner_radius=10,
            command=self._on_transform_click
        )
        self.btn_transform.pack(side="right", padx=(0, 10), pady=(30, 0))

        self.btn_crop = ctk.CTkButton(
            header, text="CROP CENTER", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#9C27B0", hover_color="#7B1FA2", text_color="white", height=32, width=100, corner_radius=10,
            command=self._on_crop_click
        )
        self.btn_crop.pack(side="right", padx=(0, 10), pady=(30, 0))

        self.btn_restart = ctk.CTkButton(
            header, text="RESTART", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#757575", hover_color="#616161", text_color="white", height=32, width=80, corner_radius=10,
            command=self._on_restart_click
        )
        self.btn_restart.pack(side="right", padx=(0, 10), pady=(30, 0))

        red_line = ctk.CTkFrame(header, width=100, height=3, fg_color=self.colors["red_primary"])
        red_line.place(x=40, y=65)

        self.preview_container = ctk.CTkFrame(self.main_content, fg_color=self.colors["bg_main"], corner_radius=0)
        self.preview_container.pack(expand=True, fill="both", padx=40, pady=20)

        self.empty_label = ctk.CTkLabel(
            self.preview_container,
            text="Hiện không có ảnh nào,\n\nHãy thêm các bức ảnh vào cửa sổ làm việc nhé!",
            font=ctk.CTkFont(family="Segoe UI", size=18), text_color=self.colors["text_dim"]
        )
        self.empty_label.pack(expand=True)

        self.preview_label = ctk.CTkLabel(self.preview_container, text="")

        self.rgb_container = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.lbl_red = ctk.CTkLabel(self.rgb_container, text="")
        self.lbl_red.pack(side="left", expand=True, padx=10)
        self.lbl_green = ctk.CTkLabel(self.rgb_container, text="")
        self.lbl_green.pack(side="left", expand=True, padx=10)
        self.lbl_blue = ctk.CTkLabel(self.rgb_container, text="")
        self.lbl_blue.pack(side="left", expand=True, padx=10)

    # ==========================================
    # PHẦN 3: GIAO DIỆN TOOL SIDEBAR PHẢI
    # ==========================================
    def _init_tool_widgets(self):
        ctk.CTkLabel(
            self.tool_sidebar, text="ADJUSTMENTS",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(35, 10), padx=20, anchor="w")

        ctk.CTkFrame(self.tool_sidebar, height=1, fg_color=self.colors["divider"]).pack(fill="x", padx=20, pady=(0, 10))

        # --- MODULE 1: LOG TRANSFORMATION ---
        log_frame = ctk.CTkFrame(self.tool_sidebar, fg_color="transparent")
        log_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            log_frame, text="˅ Log Transformation",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors["text_tool"]
        ).pack(anchor="w")

        log_slider_row = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_slider_row.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(log_slider_row, text="Constant (c)", font=ctk.CTkFont(size=12), text_color="#AAAAAA", width=70,
                     anchor="w").pack(side="left")

        # Chuyển đổi sang CTkEntry và set gốc = 0.0
        self.c_val_entry = ctk.CTkEntry(log_slider_row, width=45, height=25, font=ctk.CTkFont(size=12),
                                        fg_color="#1E1E1E", text_color="#FFFFFF", border_width=0, corner_radius=4)
        self.c_val_entry.insert(0, "0.0")
        self.c_val_entry.pack(side="right")
        self.c_val_entry.bind("<Return>", lambda e: self._on_manual_input())

        self.slider_c = ctk.CTkSlider(log_slider_row, from_=0.0, to=100.0, command=self._on_log_slider_change)
        self.slider_c.set(0.0)
        self.slider_c.pack(side="left", expand=True, fill="x", padx=10)

        ctk.CTkFrame(self.tool_sidebar, height=1, fg_color=self.colors["divider"]).pack(fill="x", padx=20, pady=15)

        # --- MODULE 2: POWER-LAW (GAMMA) TRANSFORMATION ---
        gamma_frame = ctk.CTkFrame(self.tool_sidebar, fg_color="transparent")
        gamma_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            gamma_frame, text="˅ Power-law (Gamma)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors["text_tool"]
        ).pack(anchor="w")

        # Hàng cho tham số c (Gamma)
        gc_row = ctk.CTkFrame(gamma_frame, fg_color="transparent")
        gc_row.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(gc_row, text="Constant (c)", font=ctk.CTkFont(size=12), text_color="#AAAAAA", width=70,
                     anchor="w").pack(side="left")

        self.gc_val_entry = ctk.CTkEntry(gc_row, width=45, height=25, font=ctk.CTkFont(size=12),
                                         fg_color="#1E1E1E", text_color="#FFFFFF", border_width=0, corner_radius=4)
        self.gc_val_entry.insert(0, "0.0")
        self.gc_val_entry.pack(side="right")
        self.gc_val_entry.bind("<Return>", lambda e: self._on_manual_input())

        self.slider_gc = ctk.CTkSlider(gc_row, from_=0.0, to=2.0, command=self._on_gamma_params_change)
        self.slider_gc.set(0.0)
        self.slider_gc.pack(side="left", expand=True, fill="x", padx=10)

        # Hàng cho tham số Gamma (y)
        gy_row = ctk.CTkFrame(gamma_frame, fg_color="transparent")
        gy_row.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(gy_row, text="Gamma (y)", font=ctk.CTkFont(size=12), text_color="#AAAAAA", width=70,
                     anchor="w").pack(side="left")

        self.gy_val_entry = ctk.CTkEntry(gy_row, width=45, height=25, font=ctk.CTkFont(size=12),
                                         fg_color="#1E1E1E", text_color="#FFFFFF", border_width=0, corner_radius=4)
        self.gy_val_entry.insert(0, "0.00")
        self.gy_val_entry.pack(side="right")
        self.gy_val_entry.bind("<Return>", lambda e: self._on_manual_input())

        self.slider_gy = ctk.CTkSlider(gy_row, from_=0.0, to=5.0, command=self._on_gamma_params_change)
        self.slider_gy.set(0.0)
        self.slider_gy.pack(side="left", expand=True, fill="x", padx=10)

        ctk.CTkFrame(self.tool_sidebar, height=1, fg_color=self.colors["divider"]).pack(fill="x", padx=20, pady=20)

    # ==========================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN (EVENTS)
    # ==========================================
    def set_presenter(self, presenter):
        self.presenter = presenter

    def _on_add_click(self):
        if self.presenter: self.presenter.handle_add_image()

    def _on_grayscale_click(self):
        if self.presenter: self.presenter.handle_grayscale()

    def _on_restart_click(self):
        # Reset Log sliders & entries về 0.0
        self.slider_c.set(0.0)
        self.c_val_entry.delete(0, "end")
        self.c_val_entry.insert(0, "0.0")

        # Reset Gamma sliders & entries về 0.0
        self.slider_gc.set(0.0)
        self.gc_val_entry.delete(0, "end")
        self.gc_val_entry.insert(0, "0.0")
        self.slider_gy.set(0.0)
        self.gy_val_entry.delete(0, "end")
        self.gy_val_entry.insert(0, "0.00")

        if self.presenter: self.presenter.handle_restart()

    def _on_transform_click(self):
        if self.presenter: self.presenter.handle_loop_transform()

    def _on_crop_click(self):
        if self.presenter: self.presenter.handle_crop_sequence()

    def _on_log_slider_change(self, value):
        self.c_val_entry.delete(0, "end")
        self.c_val_entry.insert(0, f"{value:.1f}")
        if self.presenter:
            self.presenter.handle_combined_transform()

    def _on_gamma_params_change(self, _):
        c_val = self.slider_gc.get()
        y_val = self.slider_gy.get()
        # Cập nhật nhãn hiển thị
        self.gc_val_entry.delete(0, "end")
        self.gc_val_entry.insert(0, f"{c_val:.1f}")
        self.gy_val_entry.delete(0, "end")
        self.gy_val_entry.insert(0, f"{y_val:.2f}")

        if self.presenter:
            self.presenter.handle_combined_transform()

    def _on_manual_input(self):
        """Hàm xử lý khi người dùng nhập số trực tiếp và nhấn Enter"""
        try:
            val_c = float(self.c_val_entry.get())
            val_gc = float(self.gc_val_entry.get())
            val_gy = float(self.gy_val_entry.get())

            # Giới hạn giá trị để không vượt quá mức cho phép của Slider
            val_c = max(0.0, min(100.0, val_c))
            val_gc = max(0.0, min(2.0, val_gc))
            val_gy = max(0.0, min(5.0, val_gy))

            # Cập nhật ngược lại thanh trượt
            self.slider_c.set(val_c)
            self.slider_gc.set(val_gc)
            self.slider_gy.set(val_gy)

            # Cập nhật lại Entry với giá trị đã format chuẩn
            self.c_val_entry.delete(0, "end")
            self.c_val_entry.insert(0, f"{val_c:.1f}")
            self.gc_val_entry.delete(0, "end")
            self.gc_val_entry.insert(0, f"{val_gc:.1f}")
            self.gy_val_entry.delete(0, "end")
            self.gy_val_entry.insert(0, f"{val_gy:.2f}")

            # Gọi luồng xử lý ảnh cộng dồn từ Presenter
            if self.presenter:
                self.presenter.handle_combined_transform()
        except ValueError:
            pass  # Bỏ qua nếu nhập ký tự không phải là số

    # ==========================================
    # CÁC HÀM CẬP NHẬT GIAO DIỆN TỪ PRESENTER
    # ==========================================
    def add_thumbnail_to_grid(self, photo_image, path):
        if self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
            self.preview_label.pack(pady=(0, 20))
            self.rgb_container.pack(fill="x", pady=10)

        btn = ctk.CTkButton(
            self.grid_frame, image=photo_image, text="", width=110, height=110,
            fg_color="transparent", hover_color="#EEEEEE", corner_radius=10,
            command=lambda p=path: self.presenter.handle_image_selection(p)
        )

        row = self.thumb_count // 2
        col = self.thumb_count % 2
        btn.grid(row=row, column=col, padx=12, pady=12)
        self.thumb_count += 1

    def update_preview(self, photo_image):
        self.preview_label.configure(image=photo_image)

    def update_rgb_preview(self, img_r, img_g, img_b):
        self.lbl_red.configure(image=img_r)
        self.lbl_green.configure(image=img_g)
        self.lbl_blue.configure(image=img_b)

    def run(self):
        self.mainloop()