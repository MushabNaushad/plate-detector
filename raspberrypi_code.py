import cv2
from picamera2 import Picamera2
from paddleocr import PaddleOCR
from ultralytics import YOLO
import re
from collections import Counter
import sys

def cleanup():
    camera.stop()

    

def plate_recognizer(image):
    ''' This Function recognizes the numberplate and return the cropped image of the plate'''

    # initialize recognizer and get results
    results = recognizer(image,verbose=False)

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
            # set the threshold probability
            if probability > 0:
                cropped_img = image[y1:y2,x1:x2]
                cropped_images.append(cropped_img)

    return cropped_images

def read_text(image)->list:
    ''' This function outputs Reads the Numberplate '''

    results = reader.predict(image)
    text = results[0]['rec_texts']
    if text:
        return text
    else:
        return None

def find_plate(texts:list,plate:list)->bool:
    ''' This function finds whether the correct plate is read by the OCR '''

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
            
     
# initialize Camera
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (640, 640)}))
camera.start()

# initialize Model
recognizer = YOLO('modelv2.pt')
reader = PaddleOCR(
    use_textline_orientation=True,
    lang='en'
)

# control variables
frame_counter = 0
check_frame = 20
allowed_plates = [
	['CP','VS','4035']
]
try:
    while True:
        frame_4_ch = camera.capture_array()
        if frame_4_ch is not None:
            frame = cv2.cvtColor(frame_4_ch,cv2.COLOR_RGBA2RGB)
            frame_counter += 1
    
            if frame_counter % check_frame == 0:
                frame_counter = 0
                cropped_set = plate_recognizer(frame)
                # taking the best possible set
	    
                if cropped_set:
                    plate = cropped_set[0]
                    if plate.size == 0 or plate.shape[0] <= 0 or plate.shape[1] <= 0:
                        print("Skipping empty or invalid crop.")
                        continue

                    ocr_results = read_text(plate)

                    if ocr_results:
                        for plate in allowed_plates:
                            found = find_plate(ocr_results,plate)
                            if found:
                                break
                            else:
                                found = False
        
                        if found:
                            print('OPEN GATE')
                        else:
                            print('Wrong VEHICLE')
            
                else:
                    print('NO VEHICLE')
		 
	    #cv2.imshow('Live',frame)
	
	    #if cv2.waitKey(1) & 0xFF == ord('q'):
	    #	break
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    print(f'{e}')
finally:
    cleanup()