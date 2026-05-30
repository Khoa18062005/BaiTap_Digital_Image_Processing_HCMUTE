import cv2
import numpy as np

# Tạo nền ảnh
img2 = np.zeros((400, 800), dtype=np.uint8)

# Vẽ ngôi sao 5 cánh
pts_star5 = np.array([[150, 50], [180, 140], [260, 140], [195, 190],
                      [220, 270], [150, 220], [80, 270], [105, 190], [40, 140], [120, 140]], np.int32)
cv2.fillPoly(img2, [pts_star5], 255)

# Vẽ hình tròn khuyết
cv2.circle(img2, (180, 310), 60, 255, -1)
cv2.circle(img2, (220, 290), 60, 0, -1)

# Vẽ ngôi sao 6 cánh
pts_star6_1 = np.array([[450, 110], [510, 210], [390, 210]], np.int32)
pts_star6_2 = np.array([[450, 230], [510, 130], [390, 130]], np.int32)
cv2.fillPoly(img2, [pts_star6_1, pts_star6_2], 255)

# Vẽ hình vuông khoét góc
cv2.rectangle(img2, (600, 50), (760, 210), 255, -1)
cv2.circle(img2, (600, 50), 20, 0, -1)
cv2.circle(img2, (760, 50), 20, 0, -1)
cv2.circle(img2, (600, 210), 20, 0, -1)
cv2.circle(img2, (760, 210), 20, 0, -1)

# Vẽ hình ellipse
cv2.ellipse(img2, (680, 310), (90, 35), 0, 0, 360, 255, -1)


# Cách 1: Tìm biên bằng Morphology Gradient
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
border_morph = cv2.morphologyEx(img2, cv2.MORPH_GRADIENT, kernel)


# Cách 2: Tìm biên bằng hàm findContours
img_contour_draw = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
contours, hierarchy = cv2.findContours(img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img_contour_draw, contours, -1, (0, 255, 0), 2)


# Hiển thị kết quả
cv2.imshow("1. Anh goc", img2)
cv2.imshow("2. Bien bang Morphology", border_morph)
cv2.imshow("3. Bien bang findContours", img_contour_draw)

cv2.waitKey(0)
cv2.destroyAllWindows()