import cv2
from picamera2 import Picamera2
import numpy as np
import easyocr
from ultralytics import YOLO

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
				cropped_img = image[y1:y2,x1:x2]
				cropped_images.append((cropped_img,probability))
	
	sorted_cropped = sorted(cropped_images, key=lambda item: item[1], reverse=True)
	return sorted_cropped
	
def read_text(image):
	result = reader.readtext(image)
	texts = []
	for (bound_box,text,probability) in result:
		texts.append(text)
					
	return texts
            
     
# initialize Camera
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (640, 640)}))
camera.start()

# initialize Model

recognizer = YOLO('best.pt')
reader = easyocr.Reader(['en'])

# control variables
frame_counter = 0
check_frame = 20
allowed_plates = [['WP','MQ','5196']]

while True:
	frame_4_ch = camera.capture_array()
	frame = cv2.cvtColor(frame_4_ch,cv2.COLOR_RGBA2RGB)
	
	frame_counter += 1
	
	if frame_counter % check_frame == 0:
		frame_counter = 0
		cropped_set = plate_recognizer(frame)
		# taking the best possible set
		if cropped_set:
			plate,prob = cropped_set[0]
			cv2.imshow('plate',plate)
			ocr_results = read_text(plate)
			print(ocr_results)
			found = False
			 
			for plate_list in allowed_plates:
				for word in plate_list:
					if word in ocr_results:
						found =True
					else:
						found = False
						break
			if found:
				print('OPEN GATE')
			
		else:
			print('NO VECHICLE')
		 
	#cv2.imshow('Live',frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

camera.stop()
cv2.destroyAllWindows()
