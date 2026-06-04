import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

def _compute_edge(image, kernel_x, kernel_y, threshold=50):
    gx_raw = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    gy_raw = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    magnitude = np.sqrt(gx_raw ** 2 + gy_raw ** 2)
    grad = np.clip(magnitude, 0, 255).astype(np.uint8)
    grad_x_display = np.clip(gx_raw + 128, 0, 255).astype(np.uint8)
    grad_y_display = np.clip(gy_raw + 128, 0, 255).astype(np.uint8)
    _, edge = cv2.threshold(grad, threshold, 255, cv2.THRESH_BINARY)
    return {"grad_x": grad_x_display, "grad_y": grad_y_display,
            "grad": grad, "edge": edge}

def sobel(image, threshold=50):
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    return _compute_edge(image, kx, ky, threshold)

def prewitt(image, threshold=50):
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)
    return _compute_edge(image, kx, ky, threshold)

def robert(image, threshold=50):
    kx = np.array([[1, 0], [0, -1]], dtype=np.float64)
    ky = np.array([[0, 1], [-1, 0]], dtype=np.float64)
    return _compute_edge(image, kx, ky, threshold)

def canny_edge(image, threshold=50):
    low = max(1, threshold // 2)
    high = max(low + 1, threshold)
    edge = cv2.Canny(image, low, high)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    gx_raw = cv2.filter2D(image, cv2.CV_64F, kx)
    gy_raw = cv2.filter2D(image, cv2.CV_64F, ky)
    magnitude = np.sqrt(gx_raw ** 2 + gy_raw ** 2)
    grad = np.clip(magnitude, 0, 255).astype(np.uint8)
    grad_x_display = np.clip(gx_raw + 128, 0, 255).astype(np.uint8)
    grad_y_display = np.clip(gy_raw + 128, 0, 255).astype(np.uint8)
    return {"grad_x": grad_x_display, "grad_y": grad_y_display,
            "grad": grad, "edge": edge}

def denoise_nlm(image_gray, h=6, template_window=7, search_window=21):
    return cv2.fastNlMeansDenoising(
        image_gray,
        h=h,
        templateWindowSize=template_window,
        searchWindowSize=search_window
    )

def enhance_he(image):
    return cv2.equalizeHist(image)

def enhance_clahe(image, clip_limit=2.0, tile=8):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile))
    return clahe.apply(image)

def enhance_linear(image):
    mn, mx = image.min(), image.max()
    if mx == mn:
        return image.copy()
    return ((image.astype(np.float64) - mn) / (mx - mn) * 255).astype(np.uint8)

def enhance_gamma(image, gamma=0.5):
    table = np.array([(i / 255.0) ** gamma * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(image, table)

class AT3App:
    DISPLAY_W = 260
    DISPLAY_H = 195

    def __init__(self, root):
        self.root = root
        self.root.title("23110116 - Nguyễn Quốc Khoa")
        self.root.geometry("1150x750")
        self.root.resizable(True, True)
        
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self._draw_gradient)

        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.place(x=0, y=0, relwidth=1, relheight=1)

        self.noise_on = tk.BooleanVar(value=True)
        self.contrast_on = tk.BooleanVar(value=False)
        self.contrast_mode = tk.StringVar(value="CLAHE")
        self.clahe_clip = tk.DoubleVar(value=3.0)
        self.gamma_val = tk.DoubleVar(value=0.6)
        self.operator = tk.StringVar(value="Canny")
        self.threshold = tk.IntVar(value=40)
        self.view_mode = tk.StringVar(value="edge")
        self.nlm_h = tk.IntVar(value=6)

        self._cur_input = None
        self._cur_contrast = None
        self._cur_output = None

        self._load_image()
        self._build_ui()
        self._update_all()

    def _draw_gradient(self, event=None):
        self.bg_canvas.delete("gradient")
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width <= 1 or height <= 1:
            return
        
        color1 = "#FCE4EC"
        color2 = "#F8BBD0"
        
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height

        for i in range(0, height, 2):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr>>8:02x}{ng>>8:02x}{nb>>8:02x}"
            self.bg_canvas.create_rectangle(0, i, width, i+2, tags=("gradient",), fill=color, outline="")

    def _load_image(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "AT3_1m4_08.tif")
        if not os.path.exists(path):
            alt = os.path.join(script_dir, "uploads", "AT3_1m4_08.tif")
            if os.path.exists(alt):
                path = alt
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy:\n{path}")
                self.root.destroy()
                return
        pil = Image.open(path).convert("L")
        self.img_original = np.array(pil)
        self.img_denoised = denoise_nlm(self.img_original, h=self.nlm_h.get())

    def _build_ui(self):
        topbar = ctk.CTkFrame(self.main_container, fg_color="#E91E63", corner_radius=0)
        topbar.pack(fill="x")
        ctk.CTkLabel(topbar, text="23110116 - Nguyễn Quốc Khoa",
                     font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="white").pack(side="left", padx=20, pady=10)
        self.badge = ctk.CTkLabel(topbar, text="", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.badge.pack(side="right", padx=20)

        main = ctk.CTkFrame(self.main_container, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        self._build_left_panel(main)
        self._build_canvas_area(main)
        self._build_right_panel(main)

    def _build_left_panel(self, parent):
        panel = ctk.CTkScrollableFrame(parent, width=260, fg_color="white", corner_radius=15, border_width=2, border_color="#F48FB1")
        panel.pack(side="left", fill="y", padx=(0, 10))

        self._sec(panel, "1. NOISE CONTROL [NLM]")
        self.noise_btn = ctk.CTkButton(panel, text="NOISE CONTROL", font=ctk.CTkFont(weight="bold"), command=self._toggle_noise, fg_color="#E91E63", hover_color="#C2185B")
        self.noise_btn.pack(fill="x", pady=6)
        
        nlm_row = ctk.CTkFrame(panel, fg_color="transparent")
        nlm_row.pack(fill="x", pady=4)
        ctk.CTkLabel(nlm_row, text="Filter h:", text_color="black").pack(side="left")
        self.nlm_label = ctk.CTkLabel(nlm_row, text=str(self.nlm_h.get()), text_color="#C2185B", font=ctk.CTkFont(weight="bold"))
        self.nlm_label.pack(side="right")
        ctk.CTkSlider(panel, from_=1, to=20, variable=self.nlm_h, command=self._on_nlm_h, button_color="#E91E63", progress_color="#E91E63").pack(fill="x", pady=2)
        
        self.noise_stat = ctk.CTkLabel(panel, text="", text_color="black", justify="left")
        self.noise_stat.pack(anchor="w")

        self._sec(panel, "2. CONTRAST ENHANCEMENT")
        self.contrast_btn = ctk.CTkButton(panel, text="CONTRAST", font=ctk.CTkFont(weight="bold"), command=self._toggle_contrast, fg_color="#E91E63", hover_color="#C2185B")
        self.contrast_btn.pack(fill="x", pady=6)

        methods = ["HE", "CLAHE", "Linear", "Gamma"]
        for val in methods:
            ctk.CTkRadioButton(panel, text=val, variable=self.contrast_mode, value=val, command=self._update_all, text_color="black", fg_color="#E91E63", hover_color="#C2185B").pack(anchor="w", pady=3)

        self.clahe_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.clahe_frame.pack(fill="x", pady=4)
        ctk.CTkLabel(self.clahe_frame, text="Clip Limit:", text_color="black").pack(side="left")
        self.clahe_label = ctk.CTkLabel(self.clahe_frame, text="3.0", text_color="#C2185B", font=ctk.CTkFont(weight="bold"))
        self.clahe_label.pack(side="right")
        ctk.CTkSlider(panel, from_=1.0, to=8.0, variable=self.clahe_clip, command=self._on_clahe, button_color="#E91E63", progress_color="#E91E63").pack(fill="x", pady=2)

        self.gamma_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.gamma_frame.pack(fill="x", pady=4)
        ctk.CTkLabel(self.gamma_frame, text="Gamma:", text_color="black").pack(side="left")
        self.gamma_label = ctk.CTkLabel(self.gamma_frame, text="0.60", text_color="#C2185B", font=ctk.CTkFont(weight="bold"))
        self.gamma_label.pack(side="right")
        ctk.CTkSlider(panel, from_=0.1, to=3.0, variable=self.gamma_val, command=self._on_gamma, button_color="#E91E63", progress_color="#E91E63").pack(fill="x", pady=2)

        self.contrast_stat = ctk.CTkLabel(panel, text="", text_color="black", justify="left")
        self.contrast_stat.pack(anchor="w")

        self._sec(panel, "3. EDGE DETECTION")
        edge_ops = ["Canny", "Sobel", "Prewitt", "Robert"]
        for val in edge_ops:
            ctk.CTkRadioButton(panel, text=val, variable=self.operator, value=val, command=self._update_all, text_color="black", fg_color="#E91E63", hover_color="#C2185B").pack(anchor="w", pady=3)

        thr_row = ctk.CTkFrame(panel, fg_color="transparent")
        thr_row.pack(fill="x", pady=4)
        ctk.CTkLabel(thr_row, text="Threshold:", text_color="black").pack(side="left")
        self.thr_label = ctk.CTkLabel(thr_row, text="40", text_color="#C2185B", font=ctk.CTkFont(weight="bold"))
        self.thr_label.pack(side="right")
        ctk.CTkSlider(panel, from_=0, to=255, variable=self.threshold, command=self._on_threshold, button_color="#E91E63", progress_color="#E91E63").pack(fill="x", pady=2)

        self._sec(panel, "OUTPUT VIEW")
        views = [("Biên (Edge)", "edge"), ("Magnitude", "grad"), ("Gradient X", "grad_x"), ("Gradient Y", "grad_y")]
        for label, val in views:
            ctk.CTkRadioButton(panel, text=label, variable=self.view_mode, value=val, command=self._update_all, text_color="black", fg_color="#E91E63", hover_color="#C2185B").pack(anchor="w", pady=3)

    def _build_canvas_area(self, parent):
        center = ctk.CTkFrame(parent, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True)

        r1 = ctk.CTkFrame(center, fg_color="transparent")
        r1.pack(fill="both", expand=True)
        c1 = self._card2(r1, "INPUT IMAGE [click to zoom]")
        c1.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.canvas_input = tk.Canvas(c1, bg="#FFF0F5", highlightthickness=0)
        self.canvas_input.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas_input.bind("<Button-1>", lambda e: self._open_zoom("INPUT", lambda: self._cur_input))

        c2 = self._card2(r1, "AFTER CONTRAST [click to zoom]")
        c2.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.canvas_contrast = tk.Canvas(c2, bg="#FFF0F5", highlightthickness=0)
        self.canvas_contrast.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas_contrast.bind("<Button-1>", lambda e: self._open_zoom("CONTRAST", lambda: self._cur_contrast))

        r2 = ctk.CTkFrame(center, fg_color="transparent")
        r2.pack(fill="both", expand=True)
        c3 = self._card2(r2, "EDGE OUTPUT [click to zoom]")
        c3.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.canvas_output = tk.Canvas(c3, bg="#FFF0F5", highlightthickness=0)
        self.canvas_output.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas_output.bind("<Button-1>", lambda e: self._open_zoom("EDGE", lambda: self._cur_output))

        c4 = self._card2(r2, "HISTOGRAM COMPARISON")
        c4.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.canvas_hist = tk.Canvas(c4, bg="#FFF0F5", highlightthickness=0)
        self.canvas_hist.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas_hist.bind("<Configure>", self._on_hist_resize)

    def _on_hist_resize(self, event=None):
        if hasattr(self, '_cur_input') and hasattr(self, '_cur_contrast'):
            if self._cur_input is not None and self._cur_contrast is not None:
                self._draw_hist_compare(self._cur_input, self._cur_contrast)

    def _build_right_panel(self, parent):
        panel = ctk.CTkFrame(parent, width=220, fg_color="white", corner_radius=15, border_width=2, border_color="#F48FB1")
        panel.pack(side="left", fill="y", padx=(10, 0))

        self._sec(panel, "STATISTICS")
        self.stats_text = ctk.CTkTextbox(panel, fg_color="#FCE4EC", text_color="black", corner_radius=10, border_width=1, border_color="#F48FB1")
        self.stats_text.pack(fill="both", expand=True, padx=12, pady=12)

    def _sec(self, p, text):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", pady=(15, 6), padx=5)
        ctk.CTkLabel(f, text=text, font=ctk.CTkFont(weight="bold", size=13), text_color="#C2185B").pack(anchor="w")

    def _card2(self, parent, title):
        c = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=2, border_color="#F48FB1")
        ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#C2185B").pack(pady=6)
        return c

    def _open_zoom(self, title, img_getter):
        win = ctk.CTkToplevel(self.root)
        win.title(f"Zoom - {title}")
        win.geometry("800x600")
        img = img_getter()
        if img is None:
            win.destroy()
            return
        
        h, w = img.shape[:2]
        canvas = tk.Canvas(win, bg="#FFF0F5", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=12)

        def resize_img(event):
            win_w = event.width
            win_h = event.height
            scale = min(win_w / w, win_h / h)
            zoom_w, zoom_h = int(w * scale), int(h * scale)
            if zoom_w <= 0 or zoom_h <= 0:
                return
            pil = Image.fromarray(img).resize((zoom_w, zoom_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil)
            canvas._tk_img = tk_img
            canvas.delete("all")
            canvas.create_image(win_w//2, win_h//2, anchor="center", image=tk_img)

        canvas.bind("<Configure>", resize_img)
        canvas.bind("<Button-1>", lambda e: win.destroy())
        win.bind("<Escape>", lambda e: win.destroy())

    def _toggle_noise(self):
        self.noise_on.set(not self.noise_on.get())
        self._update_all()

    def _toggle_contrast(self):
        self.contrast_on.set(not self.contrast_on.get())
        self._update_all()

    def _on_threshold(self, val):
        self.thr_label.configure(text=str(int(float(val))))
        self._update_all()

    def _on_clahe(self, val):
        self.clahe_label.configure(text=f"{float(val):.1f}")
        self._update_all()

    def _on_gamma(self, val):
        self.gamma_label.configure(text=f"{float(val):.2f}")
        self._update_all()

    def _on_nlm_h(self, val):
        h_val = int(float(val))
        self.nlm_label.configure(text=str(h_val))
        self.img_denoised = denoise_nlm(self.img_original, h=h_val)
        self._update_all()

    def _update_all(self):
        use_noisy = self.noise_on.get()
        img_after_noise = self.img_original if use_noisy else self.img_denoised

        if use_noisy:
            self.noise_btn.configure(text="NHIỄU: BẬT (Gốc)", fg_color="#F06292", hover_color="#E91E63")
            self.badge.configure(text="NOISY", text_color="white")
        else:
            h_val = int(self.nlm_h.get())
            self.noise_btn.configure(text=f"NHIỄU: TẮT (NLM h={h_val})", fg_color="#D81B60", hover_color="#C2185B")
            self.badge.configure(text="CLEAN", text_color="white")

        lap_var = cv2.Laplacian(img_after_noise, cv2.CV_64F).var()
        sp = np.sum((img_after_noise < 10) | (img_after_noise > 245))
        self.noise_stat.configure(text=f"Var: {lap_var:.0f} SP: {sp}")

        use_contrast = self.contrast_on.get()
        mode = self.contrast_mode.get()

        if use_contrast:
            if mode == "HE":
                img_after_contrast = enhance_he(img_after_noise)
                c_color = "#D81B60"
            elif mode == "CLAHE":
                clip = float(self.clahe_clip.get())
                img_after_contrast = enhance_clahe(img_after_noise, clip_limit=clip)
                c_color = "#AD1457"
            elif mode == "Linear":
                img_after_contrast = enhance_linear(img_after_noise)
                c_color = "#880E4F"
            else:
                g = float(self.gamma_val.get())
                img_after_contrast = enhance_gamma(img_after_noise, gamma=g)
                c_color = "#C2185B"

            self.contrast_btn.configure(text=f"TƯƠNG PHẢN: {mode}", fg_color=c_color, hover_color=c_color)
            
            orig_std = img_after_noise.std()
            new_std = img_after_contrast.std()
            gain = new_std / orig_std if orig_std > 0 else 1.0
            self.contrast_stat.configure(text=f"Std: {orig_std:.1f} -> {new_std:.1f}\nGain: {gain:.2f}x")
        else:
            img_after_contrast = img_after_noise
            self.contrast_btn.configure(text="TƯƠNG PHẢN: TẮT", fg_color="#F8BBD0", hover_color="#F48FB1")
            self.contrast_stat.configure(text="")

        op = self.operator.get()
        thr = int(self.threshold.get())
        fn_map = {
            "Sobel": sobel,
            "Prewitt": prewitt,
            "Robert": robert,
            "Canny": canny_edge,
        }
        result = fn_map[op](img_after_contrast, threshold=thr)
        view_key = self.view_mode.get()
        output_img = result[view_key]

        self._cur_input = img_after_noise.copy()
        self._cur_contrast = img_after_contrast.copy()
        self._cur_output = output_img.copy()

        self._draw(self.canvas_input, img_after_noise)
        self._draw(self.canvas_contrast, img_after_contrast)
        self._draw(self.canvas_output, output_img)
        self._draw_hist_compare(img_after_noise, img_after_contrast)

        self._update_stats(img_after_noise, img_after_contrast, output_img, result, thr)

    def _draw(self, canvas, img_gray):
        canvas.update_idletasks()
        W, H = canvas.winfo_width(), canvas.winfo_height()
        if W <= 1 or H <= 1:
            W, H = 260, 195
        pil = Image.fromarray(img_gray).resize((W, H), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)
        canvas._tk_img = tk_img
        canvas.delete("all")
        canvas.create_image(W//2, H//2, anchor="center", image=tk_img)

    def _draw_hist_compare(self, img_before, img_after):
        canvas = self.canvas_hist
        canvas.update_idletasks()
        W, H = canvas.winfo_width(), canvas.winfo_height()
        if W <= 1 or H <= 1:
            W, H = 260, 195
        canvas.delete("all")

        mid = H // 2
        canvas.create_text(4, 4, anchor="nw", text="Before", fill="#C2185B")
        hist_b = cv2.calcHist([img_before], [0], None, [64], [0, 256]).flatten()
        if hist_b.max() > 0: hist_b = hist_b / hist_b.max()
        bar_w = W / 64
        for i, v in enumerate(hist_b):
            x0, x1 = int(i * bar_w), int((i + 1) * bar_w)
            y0 = mid - 4 - int(v * (mid - 10))
            canvas.create_rectangle(x0, y0, x1, mid - 4, fill="#F06292", outline="")

        canvas.create_line(0, mid, W, mid, fill="#F48FB1", width=1)

        canvas.create_text(4, mid + 2, anchor="nw", text="After", fill="#C2185B")
        hist_a = cv2.calcHist([img_after], [0], None, [64], [0, 256]).flatten()
        if hist_a.max() > 0: hist_a = hist_a / hist_a.max()
        for i, v in enumerate(hist_a):
            x0, x1 = int(i * bar_w), int((i + 1) * bar_w)
            y1 = mid + 4 + int(v * (mid - 10))
            canvas.create_rectangle(x0, mid + 4, x1, y1, fill="#E91E63", outline="")

    def _update_stats(self, inp, contrasted, out, result, thr):
        edge_px = int(np.sum(result["edge"] > 0))
        total = result["edge"].size
        op = self.operator.get()
        lines = [
            ("INPUT", None),
            ("Mean", f"{inp.mean():.1f}"),
            ("Std", f"{inp.std():.1f}"),
            ("Min/Max", f"{inp.min()}/{inp.max()}"),
            ("", None),
            ("CONTRAST", None),
            ("Mean", f"{contrasted.mean():.1f}"),
            ("Std", f"{contrasted.std():.1f}"),
            ("Min/Max", f"{contrasted.min()}/{contrasted.max()}"),
            ("", None),
            ("EDGES", None),
            ("Operator", op),
            ("Threshold", f"{thr}"),
            ("Edge px", f"{edge_px:,}"),
            ("Edge %", f"{100 * edge_px / total:.1f}%"),
            ("Grad max", f"{result['grad'].max()}"),
            ("Grad avg", f"{result['grad'].mean():.1f}"),
            ("", None),
            ("SIZE", None),
            ("W x H", f"{inp.shape[1]}x{inp.shape[0]}"),
        ]
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        for label, val in lines:
            if val is None:
                if label:
                    self.stats_text.insert("end", f"\n{label}\n")
                else:
                    self.stats_text.insert("end", "\n")
            else:
                self.stats_text.insert("end", f"{label:<10} {val}\n")
        self.stats_text.configure(state="disabled")

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    AT3App(root)
    root.mainloop()
