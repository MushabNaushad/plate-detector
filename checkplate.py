from getfiles import get_images
import matplotlib.pyplot as plt
import cv2
import easyocr
import run_ocr
from ultralytics import YOLO
import time
import numpy as np
import os
import csv


recognizer = YOLO('best.pt')
images = get_images()
# result = recognizer(images[3])
# print(result)


def plate_recognizer(image):
    
    results = recognizer(image)
    cropped_images = []
    
    for result in results:
        boxes = result.boxes
        
        # taking the first(and only) 
        for box in boxes:
            coordinates = box.xyxy.tolist()[0]

            x1 = int(coordinates[0])
            y1 = int(coordinates[1])
            x2 = int(coordinates[2])
            y2 = int(coordinates[3])

            probability = box.conf.tolist()[0]
            
            #change the value to 0.8
            if probability > 0:
                # print('data are')
                # print(probability)
                # print(y1, y2, x1, x2)
                # print(image)
                cropped_img = image[y1:y2,x1:x2]
                cropped_images.append((cropped_img,probability))
    
    sorted_cropped = sorted(cropped_images, key=lambda item: item[1], reverse=True)
    return sorted_cropped

# test_image = cv2.imread(images[3])


def crop_image(test_image):
  
  test_image = cv2.imread(test_image)
  
  cropped_image = plate_recognizer(test_image)[0][0]
  gray_plate = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
  blurred_plate = cv2.medianBlur(gray_plate, 3)
  thresh_plate = cv2.adaptiveThreshold(blurred_plate,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY ,11,2)
  
  
  return thresh_plate, cropped_image

def read_plate(image, og):
    reader = easyocr.Reader(['en'])
    texts = []
    result = reader.readtext(image)
    for (bound_box,text,probability) in result:
        texts.append(text)
    plt.subplot(1,2, 1)
    plt.title(texts)
    plt.imshow(image)
    plt.subplot(1, 2, 2)
    plt.imshow(og)
    plt.pause(2)
                    
    return texts




def crop_plate_2(frame):
    kernel = np.ones((5,5), np.uint8)
    # Image preprocessing
    frame = cv2.imread(frame)
    
  
    frame = plate_recognizer(frame)[0][0]
    frame = cv2.convertScaleAbs(frame, alpha=0.8, beta=-50)
    
    # Convert to HSV for color filtering (yellow and white plates)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Yellow plate filter
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # White plate filter
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Combine masks
    combined_mask = cv2.bitwise_or(yellow_mask, white_mask)
    masked_frame = cv2.bitwise_and(frame, frame, mask=combined_mask)

    # Convert to grayscale and apply edge detection
    gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 120)  # Adjusted Canny thresholds
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    _, thresh_roi = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Adjusted thresholding
    reader = easyocr.Reader(['en'])
    texts = []
    result = reader.readtext(image)
    for (bound_box,text,probability) in result:
        texts.append(text)
    plt.subplot(1,1, 1)
    plt.title(texts)
    plt.imshow(frame)
    
    plt.pause(1)
    # # print(f"Processing {image_name} - Number of contours found: {len(contours)}")
    # print('contours')
    # print(contours)
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     print(f"Contour area: {area}")
    #     if 200 < area < 100000:  # Adjusted threshold
    #         x, y, w, h = cv2.boundingRect(contour)
    #         aspect_ratio = float(w) / h
    #         print(f"Aspect ratio: {aspect_ratio}")
    #         if 0.5 < aspect_ratio < 6.0:  # Broadened range for plates
    #             plate_roi = frame[y:y+h, x:x+w]
    #             gray_roi = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
    #             gray_roi = cv2.resize(gray_roi, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)  # Increased resize factor
    #             gray_roi = cv2.equalizeHist(gray_roi)
    #             _, thresh_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Adjusted thresholding
    #             reader = easyocr.Reader(['en'])
    #             texts = []
    #             result = reader.readtext(image)
    #             for (bound_box,text,probability) in result:
    #                 texts.append(text)
    #             plt.subplot(1,1, 1)
    #             plt.title(texts)
    #             plt.imshow(frame)
                
    #             plt.pause(1)

# for image in images[0:20]:
#     crop, og = crop_image(image)
#     print(read_plate(crop, og))

# for image in images[0:20]:
#   crop_plate_2(image)
# for image_path in images[5:15]:
#   print(run_ocr.get_plate(image_path))
#   image = cv2.imread(image_path)
#   plt.imshow(image)
#   plt.show()

# image_path = images[1]
# print(run_ocr.get_plate(image_path))


# image = cv2.imread(image_path)
# plt.imshow(image)
# plt.show()

log_file = "recognised plates.csv"

# Initialize CSV if it doesn’t exist
if os.path.exists(log_file):
    os.remove(log_file)
with open(log_file, mode='w', newline='') as file:
  writer = csv.writer(file)
  writer.writerow(["Timestamp", "Plate Number", "Province"])
  for image in images:
    crop, og = crop_image(image)
    writer.writerow(read_plate(crop, og))
  