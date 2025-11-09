# Gets a list of images of license plates from kaggle for the purpose of testing
import kagglehub
import os
import cv2
import matplotlib.pyplot as plt

# Returns a list of pathnames of images and download if necessary
def get_images():
  # Download latest version of the images via kaggle
  path = kagglehub.dataset_download("andrewmvd/car-plate-detection")
  # print("Path to dataset files:", path)

  image_dir = path + '/images'
  image_files = os.listdir(image_dir)

  images = []
  for image in image_files:
    images.push(image_dir + "/" + image)
  return images


ex_image = cv2.imread(image_dir + "/" + image_files[3])
plt.imshow(ex_image)
plt.show()




# if not image_files:
#   print('working')
# else:
#   print('not working')