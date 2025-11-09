from getfiles import get_images
import matplotlib.pyplot as plt
import cv2
import easyocr
import run_ocr


images = get_images()
for image_path in images:
  print(run_ocr.get_plate(image_path))


# image = cv2.imread(image_path)
# plt.imshow(image)
# plt.show()

