import customtkinter as ctk


class SelectionView(ctk.CTk):
    def __init__(self, on_spatial_selected, on_frequency_selected):
        super().__init__()
        self.title("Ứng dụng Xử lý ảnh số - Màn hình chính")

        # Căn giữa cửa sổ
        window_width = 500
        window_height = 350
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        self.attributes('-topmost', True)
        self.lift()
        self.configure(fg_color="#FFFFFF")

        # Lưu lại các hàm callback để gọi khi click button
        self.on_spatial_selected = on_spatial_selected
        self.on_frequency_selected = on_frequency_selected

        self._init_widgets()

    def _init_widgets(self):
        # Tiêu đề
        lbl_title = ctk.CTkLabel(
            self, text="CHỌN CHẾ ĐỘ XỬ LÝ",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#D32F2F"
        )
        lbl_title.pack(pady=(40, 10))

        lbl_subtitle = ctk.CTkLabel(
            self, text="Vui lòng chọn miền không gian hoặc miền tần số để tiếp tục",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#757575"
        )
        lbl_subtitle.pack(pady=(0, 40))

        # Nút chức năng 1: Miền không gian
        btn_spatial = ctk.CTkButton(
            self, text="XỬ LÝ MIỀN KHÔNG GIAN",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#D32F2F", hover_color="#B71C1C", text_color="white",
            height=50, width=300, corner_radius=10,
            command=self._handle_spatial_click
        )
        btn_spatial.pack(pady=10)

        # Nút chức năng 2: Miền tần số
        btn_frequency = ctk.CTkButton(
            self, text="XỬ LÝ MIỀN TẦN SỐ",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#2B2B2B", hover_color="#1E1E1E", text_color="white",
            height=50, width=300, corner_radius=10,
            command=self._handle_frequency_click
        )
        btn_frequency.pack(pady=10)

    def _handle_spatial_click(self):
        self.destroy()  # Đóng cửa sổ chọn
        self.on_spatial_selected()  # Kích hoạt hàm khởi chạy miền không gian

    def _handle_frequency_click(self):
        self.destroy()  # Đóng cửa sổ chọn
        self.on_frequency_selected()  # Kích hoạt hàm khởi chạy miền tần số