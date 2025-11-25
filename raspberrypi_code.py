import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO
import re
from collections import Counter
import sys
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time
import subprocess

def cleanup():
    camera.stop()
    if Gate_Position:
        # Close the Gate
        control_gate()
    GPIO.cleanup()

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
            if probability > 0.5:
                cropped_img = image[y1:y2,x1:x2]
                cropped_images.append(cropped_img)

    return cropped_images

def read_text(image) -> list:
    ''' This function reads the Numberplate and returns a list of strings '''
    
    # read the plate
    results = reader.ocr(image) 
    if not results or results[0] is None:
        return None

    detected_lines = results[0]
    final_texts = []

    # turn all the detected text to uppercase and return a list of text
    for line in detected_lines:
        text_content = line[1][0].upper()
        final_texts.append(text_content)
    
    # output the strings that may or may not be in the actual order
    return final_texts

def find_plate(texts:list,plate:list)->bool:
    ''' This function finds whether the correct plate is read by the OCR '''

    jumbled_plate = str()
    for text in texts:
        # remove -, spaces from the detected text
        alphanum_in_plate = text.replace('-', '').replace(' ', '')
        jumbled_plate += alphanum_in_plate
    
    # find any permutation of the letters and numbers given to be identical to the plate
    pattern_of_plate = '|'.join(plate)
    parts = re.findall(rf'({pattern_of_plate})', jumbled_plate)
    
    Found_plate = Counter(parts) == Counter(plate)

    return Found_plate

def check_presence(address):
    # l2ping sends a ping to the bluetooth device
    # -c 1 sends 1 packet, -t 1 sets timeout to 1 second
    command = f"sudo l2ping -c 1 -t 1 {address}"
    try:
        subprocess.check_output(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def control_gate():
    print("Operating Gate")
    GPIO.output(GATE_PIN, GPIO.HIGH)
    time.sleep(1) # Simulate button press duration
    GPIO.output(GATE_PIN, GPIO.LOW)

def second_authentication():
    for address in target_macs:
        for _ in range(2):
            if check_presence(address):
                control_gate()
                return True
            time.sleep(2)  # Wait between scans to save CPU/interference

if __name__ == '__main__':
    # initialize Camera
    camera = Picamera2()
    camera.configure(camera.create_video_configuration(main={"size": (640, 640)}))
    camera.start()

    # initialize Model
    reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)  
    recognizer = YOLO('modelv2.pt')

    # control variables
    frame_counter = 0
    check_frame = 20
    allowed_plates = [
        ['CP','MQ','5196']
    ]
    target_macs = [
        "90:B7:90:07:FC:F0",
        "F0:55:01:BF:53:13"
    ]
    GATE_PIN = 17
    Gate_Position = False # True = Open and False = closed
    sec_auth = True # set true to check for phone

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GATE_PIN, GPIO.OUT)
    GPIO.output(GATE_PIN, GPIO.LOW)

    try:
        while True:
            frame_4_ch = camera.capture_array()
            if frame_4_ch is not None:
                frame = cv2.cvtColor(frame_4_ch, cv2.COLOR_RGBA2RGB)
                frame_counter += 1
        
                if frame_counter % check_frame == 0:
                    frame_counter = 0
                    cropped_set = plate_recognizer(frame)
                    # taking the best possible set
            
                    if cropped_set:
                        plate = cropped_set[0]
                        # check whether the plate is image is empty
                        if plate.size == 0 or plate.shape[0] <= 0 or plate.shape[1] <= 0:
                            print("Skipping empty or invalid crop.")
                            continue
                        
                        ocr_results = read_text(plate)

                        if ocr_results:
                            # check for each allowed plates
                            for plate in allowed_plates:
                                found = find_plate(ocr_results, plate)
                                if found:
                                    break
                                else:
                                    found = False
                            print(ocr_results)
                            if found and not Gate_Position:
                                print('Plate Detected')
                                if sec_auth:
                                    isOpen = second_authentication()
                                    if isOpen:
                                        Gate_Position = True
                                else:
                                    control_gate()
                                    Gate_Position = True

                            else:
                                if Gate_Position:
                                    print('Car is at the Gate')
                                else:
                                    print('Wrong VEHICLE')
                
                    else:
                        print('NO VEHICLE')
                        if Gate_Position:
                            print('Waiting')
                            time.sleep(30)
                            print('Closing Gate')
                            # close gate
                            control_gate()
                            Gate_Position = False
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{e}')
    finally:
        cleanup()