import easyocr

def get_plate(imagepath):
  reader = easyocr.Reader(['en'])
  result = reader.readtext(imagepath)
  texts = []
  # print(result)
  for (bbox, text, prob) in result:
    texts.append(text)
  return texts
