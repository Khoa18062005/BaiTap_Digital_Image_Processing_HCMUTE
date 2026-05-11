import cv2
import numpy as np
import matplotlib.pyplot as plt

def custom_convolve2d(image, kernel):
    kernel_h, kernel_w = kernel.shape
    img_h, img_w = image.shape

    # Tính toán kích thước padding để giữ nguyên kích thước ảnh đầu ra
    pad_h = kernel_h // 2
    pad_w = kernel_w // 2

    # Thêm padding (viền số 0) xung quanh ảnh
    padded_img = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant')

    # Khởi tạo ma trận kết quả
    result = np.zeros_like(image, dtype=np.float64)

    # Theo đúng định nghĩa toán học của tích chập (Convolution),
    # ta cần lật ngược kernel 180 độ. (Nếu không lật thì gọi là Correlation).
    kernel_flipped = np.flipud(np.fliplr(kernel))

    # Lặp qua từng pixel của ảnh gốc để tính tích chập
    for i in range(img_h):
        for j in range(img_w):
            # Trích xuất vùng lân cận (Region of Interest)
            region = padded_img[i:i + kernel_h, j:j + kernel_w]
            # Nhân từng phần tử và tính tổng
            result[i, j] = np.sum(region * kernel_flipped)

    return result

def process_bone_scan(image_path):
    # a. Ảnh gốc
    img_a = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_float = img_a.astype(np.float64)

    # b. Ảnh laplacian sử dụng kernel
    laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
    img_b = cv2.filter2D(img_float, -1, laplacian_kernel)

    # c. Ảnh làm sắc nét Sharpened = (a) - (b)
    img_c = img_float - img_b
    # Đưa các giá trị về khoảng hợp lệ
    img_c = np.clip(img_c, 0, 255)

    # d. Ảnh sobel gradient (Tích chập thủ công)
    sobel_kernel_x = np.array([[-1, 0, 1],
                               [-2, 0, 2],
                               [-1, 0, 1]])

    sobel_kernel_y = np.array([[-1, -2, -1],
                               [0, 0, 0],
                               [1, 2, 1]])

    # Tính đạo hàm theo hướng x và y
    gx = custom_convolve2d(img_float, sobel_kernel_x)
    gy = custom_convolve2d(img_float, sobel_kernel_y)
    # Tính độ lớn Gradient của Sobel (Magnitude)
    img_d = np.sqrt(gx ** 2 + gy ** 2)

    # e. Ảnh làm mịn Sobel bằng Box filter 5x5
    img_e = cv2.blur(img_d, (5, 5))

    # f. Ảnh mặt nạ mask (nhận từng điểm ảnh pixel)
    # Chuẩn hóa ảnh (e) về khoảng [0, 1] để nó đóng vai trò là trọng số (mask)
    mask_weight = img_e / (np.max(img_e) + 1e-5)
    img_f = img_c * mask_weight

    # g. Ảnh sắc nét cải tiến = (a) + (f)
    img_g = img_float + img_f
    img_g = np.clip(img_g, 0, 255)

    # h. Ảnh được tăng độ tương phản (áp dụng hàm gamma)
    gamma = 0.5
    img_g_norm = img_g / 255.0  # Chuẩn hóa về [0, 1] trước khi lấy lũy thừa
    img_h = np.power(img_g_norm, gamma) * 255.0

    # Hàm hỗ trợ hiển thị ảnh
    display_images(img_a, img_b, img_c, img_d, img_e, img_f, img_g, img_h)


def display_images(a, b, c, d, e, f, g, h):
    titles = ['(a) Original', '(b) Laplacian', '(c) a + b', '(d) Sobel (Manual)',
              '(e) Smoothed Sobel', '(f) Mask: c * e', '(g) a + f', '(h) Power-law on g']

    # Chuyển đổi các ảnh về định dạng uint8 để hiển thị an toàn
    images = [a, b, c, d, e, f, g, h]
    processed_images = []

    for img in images:
        # Chuẩn hóa min-max để hiển thị rõ các chi tiết âm/dương (đặc biệt là Laplacian)
        img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        processed_images.append(np.uint8(img_norm))

    plt.figure(figsize=(16, 8))
    for i in range(8):
        plt.subplot(2, 4, i + 1)
        plt.imshow(processed_images[i], cmap='gray')
        plt.title(titles[i], fontsize=12)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

# Gọi hàm thực thi (Bạn thay đổi đường dẫn bằng tên file ảnh của bạn)
process_bone_scan('XGrey.jpg')