import os
import cv2
import time

def get_snapshot(frame, coordinates):
  cwd = os.getcwd()
  images_path = os.path.join(cwd, 'images')
  if not os.path.exists(images_path):
    os.makedirs(images_path)
  files = os.listdir(images_path)
  if len(files) >= 30:
    files.sort()
    os.remove(os.path.join(images_path, files[0]))
  x1, y1, x2, y2 = coordinates
  bounded_image = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
  rotated_image = cv2.rotate(bounded_image, cv2.ROTATE_180)
  img_name = f'{time.time()}.jpg' 
  cv2.imwrite(os.path.join(images_path, img_name), rotated_image)


  
print(os.listdir(os.path.join(os.getcwd(), 'images')))

