# Gets a list of images of license plates from kaggle for the purpose of testing
import kagglehub

# Download latest version
path = kagglehub.dataset_download("andrewmvd/car-plate-detection")

print("Path to dataset files:", path)