# Gets a list of images of license plates from kaggle for the purpose of testing
import kagglehub
import os
import cv2
import matplotlib.pyplot as plt

# Returns a list of pathnames of images and download if necessary
def get_images():
  # Download latest version of the images via kaggle
  path = kagglehub.dataset_download("rohankumara/sri-lanka-vehicle-number-plates")
  # print("Path to dataset files:", path)

  image_dir = path + '/Numberplate'
  image_files = os.listdir(image_dir)

  images = []
  for image in image_files[0:50]:
    if image[-3:] == 'jpg':
      images.append(image_dir + "/" + image)
  return images


# if name = "__main__"
# ex_image = cv2.imread(image_dir + "/" + image_files[3])
# plt.imshow(ex_image)
# plt.show()

