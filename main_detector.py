import cv2
import easyocr
from ultralytics import YOLO


def recognize_plate(image):
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


video = cv2.VideoCapture(1)

recognizer = YOLO('modelv1.pt')
reader = easyocr.Reader(['en'])

frame_counter = 0

output = []
plates = ['WP QR 5029','CP BJA 1482']

while True:
    
    success, frame = video.read()
    if success == False:
        break

    if frame_counter % 10 == 0:
        cropped = recognize_plate(frame)
        
        #we take the first(and only) results since only one plate appears for our purpose
        results = reader.readtext(cropped[0])
        texts = []
        
        for (bound_box,text,probability) in results:
            texts.append(text)
        
        for plate in plates:
            # splitting the plate numbers, since it doesn't read as a group
            splitted = plate.split()
            found = False
            for word in splitted:
                if word in texts:
                    found = True
                else:
                    found = False
            
            if found:
                output.append(1)
                break
        else:
            output.append(0)

print('successful')
