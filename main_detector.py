import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO
import re
from collections import Counter


def recognize_plate(image):
    ''' This Function recognizes the numberplate and return the cropped image of the plate'''

    # initialize recognizer and get results
    results = recognizer(image)

    # to store cropped plates if there is more than one
    cropped_images = []

    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            coordinates = box.xyxy.tolist()[0]

            x1 = int(coordinates[0])
            y1 = int(coordinates[1])
            x2 = int(coordinates[2])
            y2 = int(coordinates[3])

            probability = box.conf.tolist()[0]
            if probability > 0.8:
                cropped_img = image[y1:y2,x1:x2]
                cropped_images.append(cropped_img)

    return cropped_images

def detect_text(image)->list:
    ''' This function outputs Reads the Numberplate '''

    results = reader.predict(image)
    # to hold texts read
    texts = []
    text = results[0]['rec_texts']
    if text:
        texts.append(text)

    return texts

def find_plate(texts:list,plate:list)->bool:
    ''' This function finds whether the plate is read by the OCR '''

    jumbled_plate = str()
    # split any words inorder to match
    for text in texts:
        words = []
        if '-' in text:
            words = text.split('-')
        if ' ' in text:
            words = text.split()
        if words:
            for word in words:
                jumbled_plate += word
        else:
            jumbled_plate += text
    
    pattern_of_plate = '|'.join(plate)
    parts = re.findall(rf'({pattern_of_plate})',jumbled_plate)
    
    Found_plate = Counter(parts) == Counter(plate)

    return Found_plate

video = cv2.VideoCapture(1)

recognizer = YOLO('modelv1.pt')
reader = PaddleOCR(
    use_textline_orientation=True,
    lang='en'
)

frame_counter = 0

output = []
plates = [
    ['WP', 'QR' ,'5029'],
    ['CP','BJA','1482']
]

while True:
    
    success, frame = video.read()
    if success == False:
        break

    if frame_counter % 10 == 0:
        cropped = recognize_plate(frame)
        
        #we take the first(and only) results since only one plate appears for our purpose
        texts = detect_text(cropped[0])
        for plate in plates:
            isFound = find_plate(texts,plate)
            if isFound:
                break
        else:
            isFound = False
        
        if isFound:
            output.append(1)
        else:
            output.append(0)

        

print('successful')
