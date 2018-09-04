from scipy.ndimage import imread
from scipy.misc import imsave
import sys

def normalize(img):
  _min = img.min()
  _max = img.max()
  return img - _min * 255 / (_max - _min)

img = imread(sys.argv[1])
normalized = normalize(img)
imsave('normalized.png', normalized)