import numpy as np
import cv2
img = np.zeros((300,700), dtype=np.uint8)
# Vẽ hình chữ L
cv2.rectangle(img, (50, 40), (150, 260), 255, -1)   # Thanh đứng
cv2.rectangle(img, (150, 170), (280, 260), 255, -1) # Thanh ngang

# Vẽ hình tròn khuyết
cv2.circle(img, (520, 150), (100), 255, -1)
cv2.rectangle(img, (520, 50), (630, 150), 0, -1)

# Tạo ma trận kernel
kernel = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
], dtype=np.uint8)

# Erosion (làm teo nhỏ vật thể)
img_erosion = cv2.erode(img, kernel, iterations=1)
# Dilation (làm phình to vật thể)
img_dilation = cv2.dilate(img, kernel, iterations=1)

# Hiển thị kết quả
cv2.imshow("1. Anh goc (Original)", img)
cv2.imshow("2. Xoi mon (Erosion)", img_erosion)
cv2.imshow("3. Gian no (Dilation)", img_dilation)

cv2.waitKey(0)
cv2.destroyAllWindows()