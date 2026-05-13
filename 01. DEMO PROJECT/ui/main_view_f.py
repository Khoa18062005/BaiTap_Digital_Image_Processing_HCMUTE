import customtkinter as ctk
import tkinter as tk


class MainViewF(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Homework - Xử lý miền tần số (Frequency Domain)")

        # Cấu hình kích thước màn hình tương tự miền không gian
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        try:
            self.attributes('-zoomed', True)
        except:
            pass

        # Hệ màu đồng nhất để tạo sự nhất quán cho ứng dụng[cite: 5]
        self.colors = {
            "bg_main": "#FFFFFF",
            "bg_sidebar": "#F8F9FA",
            "bg_tools": "#2B2B2B",
            "red_primary": "#D32F2F",
            "red_hover": "#B71C1C",
            "text_main": "#212121",
            "text_dim": "#757575",
            "divider": "#3A3A3A"
        }
        self.configure(fg_color=self.colors["bg_main"])

        self.presenter = None
        self.on_back_callback = None
        self.thumb_count = 0
        self.thumbnail_buttons = {}

        # Phân chia bố cục chính (Thứ tự pack: Sidebar trái -> Tool phải -> Content giữa)[cite: 5]
        self.sidebar = ctk.CTkFrame(self, width=320, fg_color=self.colors["bg_sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.tool_sidebar = ctk.CTkFrame(self, width=320, fg_color=self.colors["bg_tools"], corner_radius=0)
        self.tool_sidebar.pack(side="right", fill="y")
        self.tool_sidebar.pack_propagate(False)

        self.main_content = ctk.CTkFrame(self, fg_color=self.colors["bg_main"], corner_radius=0)
        self.main_content.pack(side="left", expand=True, fill="both")

        # Khởi tạo các Widgets
        self._init_sidebar_widgets()
        self._init_preview_widgets()
        self._init_tool_widgets()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_back_callback(self, callback):
        """Thiết lập hàm điều hướng quay lại menu chính"""
        self.on_back_callback = callback

    def _on_back_click(self):
        """Xử lý đóng cửa sổ hiện tại và gọi hàm quay về"""
        if self.on_back_callback:
            self.on_back_callback()
        self.destroy()

    # ==========================================
    # PHẦN 1: SIDEBAR TRÁI (LOAD ẢNH & ĐIỀU HƯỚNG)
    # ==========================================
    def _init_sidebar_widgets(self):
        # Nút Quay về Menu chính[cite: 3]
        self.btn_back = ctk.CTkButton(
            self.sidebar, text="← QUAY VỀ MENU",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="transparent", hover_color="#EBEBEB", text_color=self.colors["text_dim"],
            anchor="w", width=150, height=35,
            command=self._on_back_click
        )
        self.btn_back.pack(anchor="nw", padx=15, pady=(15, 0))

        ctk.CTkLabel(
            self.sidebar, text="MIỀN TẦN SỐ",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.colors["red_primary"]
        ).pack(pady=(20, 5), padx=25)

        ctk.CTkLabel(
            self.sidebar, text="Frequency Domain Processing",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.colors["text_dim"]
        ).pack(padx=25, pady=(0, 10))

        # Nút nạp thư mục ảnh[cite: 5]
        self.btn_add = ctk.CTkButton(
            self.sidebar, text="ADD NEW FOLDER",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.colors["red_primary"], hover_color=self.colors["red_hover"],
            text_color="white", height=45, corner_radius=15,
            command=lambda: self.presenter.handle_add_image() if self.presenter else None
        )
        self.btn_add.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#EEEEEE").pack(fill="x", padx=25, pady=10)

        # Danh sách ảnh thu nhỏ (Grid)
        self.canvas = tk.Canvas(self.sidebar, bg=self.colors["bg_sidebar"], highlightthickness=0, borderwidth=0)
        self.scrollbar = ctk.CTkScrollbar(self.sidebar, orientation="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=self.colors["bg_sidebar"])

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=10)

    # ==========================================
    # PHẦN 2: MIỀN HIỂN THỊ (CONTENT GIỮA)
    # ==========================================
    def _init_preview_widgets(self):
        header = ctk.CTkFrame(self.main_content, fg_color=self.colors["bg_main"], height=80, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="IMAGE PREVIEW", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=self.colors["text_main"]).pack(side="left", padx=40, pady=(30, 0))

        red_line = ctk.CTkFrame(header, width=100, height=3, fg_color=self.colors["red_primary"])
        red_line.place(x=40, y=65)

        self.preview_container = ctk.CTkFrame(self.main_content, fg_color=self.colors["bg_main"], corner_radius=0)
        self.preview_container.pack(expand=True, fill="both", padx=40, pady=20)

        self.empty_label = ctk.CTkLabel(
            self.preview_container,
            text="Hãy thêm các bức ảnh vào cửa sổ làm việc nhé!",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=self.colors["text_dim"]
        )
        self.empty_label.pack(expand=True)

        self.preview_label = ctk.CTkLabel(self.preview_container, text="")

    # ==========================================
    # PHẦN 3: SIDEBAR PHẢI (CÔNG CỤ TẦN SỐ)
    # ==========================================
    def _init_tool_widgets(self):
        ctk.CTkLabel(self.tool_sidebar, text="FREQUENCY OPERATIONS",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#FFFFFF").pack(
            pady=(40, 10), padx=20, anchor="w")

        ctk.CTkFrame(self.tool_sidebar, height=1, fg_color=self.colors["divider"]).pack(fill="x", padx=20, pady=(0, 10))

        # Nút Hiển thị FFT (Màu xanh lá)
        self.btn_fft = ctk.CTkButton(
            self.tool_sidebar, text="HIỂN THỊ PHỔ FFT",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#4CAF50", hover_color="#388E3C", text_color="white",
            height=40, corner_radius=10,
            command=lambda: self.presenter.handle_show_fft() if self.presenter else None
        )
        self.btn_fft.pack(fill="x", padx=20, pady=(20, 10))

        # Nút Xem Ảnh Gốc (Màu đỏ đặc trưng)[cite: 5]
        self.btn_original = ctk.CTkButton(
            self.tool_sidebar, text="XEM ẢNH GỐC",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.colors["red_primary"], hover_color=self.colors["red_hover"],
            text_color="white", height=40, corner_radius=10,
            command=lambda: self.presenter.handle_show_original() if self.presenter else None
        )
        self.btn_original.pack(fill="x", padx=20, pady=10)

        self.btn_filter_pass = ctk.CTkButton(
            self.tool_sidebar, text="FILTER PASS",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#673AB7", hover_color="#512DA8",
            text_color="white", height=40, corner_radius=10,
            command=lambda: self.presenter.handle_open_filter_pass() if self.presenter else None
        )
        self.btn_filter_pass.pack(fill="x", padx=20, pady=10)
        # Placeholder cho các bộ lọc sau này
        ctk.CTkLabel(self.tool_sidebar, text="FILTER SETTINGS",
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     text_color="#AAAAAA").pack(pady=(20, 10), padx=20, anchor="w")

    # ==========================================
    # CÁC HÀM CẬP NHẬT GIAO DIỆN
    # ==========================================
    def add_thumbnail_to_grid(self, photo_image, path):
        if self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
            self.preview_label.pack(expand=True)

        btn = ctk.CTkButton(
            self.grid_frame, image=photo_image, text="", width=110, height=110,
            fg_color="transparent", hover_color="#EEEEEE", corner_radius=10,
            command=lambda p=path: self.presenter.handle_image_selection(p)
        )
        self.thumbnail_buttons[path] = btn
        row, col = divmod(self.thumb_count, 2)
        btn.grid(row=row, column=col, padx=12, pady=12)
        self.thumb_count += 1

    def update_preview(self, photo_image):
        """Cập nhật ảnh chính trên màn hình preview"""
        self.preview_label.configure(image=photo_image)
        self.preview_label._image = photo_image  # Ngăn Garbage Collection xóa ảnh[cite: 2]

    def highlight_thumbnail(self, selected_paths):
        """Tạo viền highlight cho ảnh đang được chọn[cite: 3]"""
        for path, btn in self.thumbnail_buttons.items():
            if path in selected_paths:
                btn.configure(border_width=3, border_color=self.colors["red_primary"], fg_color="#EBEBEB")
            else:
                btn.configure(border_width=0, fg_color="transparent")

    def run(self):
        self.mainloop()