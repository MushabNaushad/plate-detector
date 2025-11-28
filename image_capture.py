import os
import cv2
import time

def get_snapshot(frame, plate, coordinates):
  cwd = os.getcwd()
  images_path = os.path.join(cwd, 'images')
  if not os.path.exists():
    os.makedirs(images_path)
  if len(os.listdir(images_path)) >= 30:
    os.remove(os.path.join(images_path, os.listdir(images_path)[0]))
  x1, y1, x2, y2 = coordinates
  bounded_image = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
  cv2.imwrite(os.path.join(images_path, time.time()), bounded_image)


  
print(os.listdir(os.path.join(os.getcwd(), 'images')))



