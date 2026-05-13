import customtkinter as ctk
import tkinter as tk


class FrequencyFilterView(ctk.CTkToplevel):
    def __init__(self, master, presenter):
        super().__init__(master)
        self.title("Frequency Domain Filtering - 6 Outputs")
        self.geometry("1400x900")
        self.presenter = presenter
        self.configure(fg_color="#FFFFFF")

        # Layout chính: Trái (Ảnh) - Phải (Tool)
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.pack(fill="both", expand=True)

        self.image_container = ctk.CTkFrame(self.main_frame, fg_color="#F0F0F0")
        self.image_container.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.tool_sidebar = ctk.CTkScrollableFrame(self.main_frame, width=350, fg_color="#2B2B2B")
        self.tool_sidebar.pack(side="right", fill="y")

        self.image_labels = {}
        self._init_image_grid()
        self._init_controls()

    def _init_image_grid(self):
        # Tạo lưới 2 hàng 3 cột để hiển thị 6 ảnh
        titles = [
            "Ideal Lowpass", "Butterworth Lowpass", "Gaussian Lowpass",
            "Ideal Highpass", "Butterworth Highpass", "Gaussian Highpass"
        ]
        keys = ["ilp", "blp", "glp", "ihp", "bhp", "ghp"]

        for i in range(6):
            r, c = divmod(i, 3)
            frame = ctk.CTkFrame(self.image_container, fg_color="white", corner_radius=10)
            frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(frame, text=titles[i], font=("Segoe UI", 12, "bold")).pack(pady=5)
            lbl = ctk.CTkLabel(frame, text="Processing...")
            lbl.pack(expand=True, fill="both", padx=5, pady=5)
            self.image_labels[keys[i]] = lbl

        self.image_container.grid_columnconfigure((0, 1, 2), weight=1)
        self.image_container.grid_rowconfigure((0, 1), weight=1)

    def _init_controls(self):
        # Hàm tiện ích tạo cụm slider
        def create_group(title, key, has_n=False):
            ctk.CTkLabel(self.tool_sidebar, text=title.upper(), text_color="#D32F2F",
                         font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))

            # Slider D0
            ctk.CTkLabel(self.tool_sidebar, text="Cutoff Frequency (D0)", text_color="white").pack()
            s_d0 = ctk.CTkSlider(self.tool_sidebar, from_=1, to=200, command=lambda v: self.presenter.update_filter())
            s_d0.set(30)
            s_d0.pack(fill="x", padx=20)

            res = {"d0": s_d0}
            if has_n:
                ctk.CTkLabel(self.tool_sidebar, text="Order (n)", text_color="white").pack()
                s_n = ctk.CTkSlider(self.tool_sidebar, from_=1, to=10, number_of_steps=9,
                                    command=lambda v: self.presenter.update_filter())
                s_n.set(2)
                s_n.pack(fill="x", padx=20)
                res["n"] = s_n
            return res

        self.controls = {
            "ilp": create_group("Ideal Lowpass", "ilp"),
            "blp": create_group("Butterworth Lowpass", "blp", True),
            "glp": create_group("Gaussian Lowpass", "glp"),
            "ihp": create_group("Ideal Highpass", "ihp"),
            "bhp": create_group("Butterworth Highpass", "bhp", True),
            "ghp": create_group("Gaussian Highpass", "ghp")
        }

    def update_images(self, images_dict):
        for key, img in images_dict.items():
            self.image_labels[key].configure(image=img, text="")
            self.image_labels[key]._image = img