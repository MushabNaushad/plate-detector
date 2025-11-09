import cv2
import easyocr

video = cv2.VideoCapture(1)

reader = easyocr.Reader(['en'])

frame_counter = 0

output = []
plates = ['WP QR 5029','CP BJA 1482']

while True:
    
    success, frame = video.read()
    if success == False:
        break

    if frame_counter % 10 == 0:
        results = reader.readtext(frame)
        texts = []
        for (bound_box,text,probability) in results:
            texts.append(text)
        
        for plate in plates:
            # splitting the plate numbers, sicne it doesn't read as a group
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