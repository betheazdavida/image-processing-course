from scipy.ndimage import imread
from scipy.misc import imsave
import sys

def normalize(img):
  '''
  Normalize the exposure of an image.
  @args:
    {numpy.ndarray} img: an array of image pixels with shape:
      (height, width)
  @returns:
    {numpy.ndarray} an image with shape of `img` wherein
      all values are normalized such that the min=0 and max=255
  '''
  _min = img.min()
  _max = img.max()
  return img - _min * 255 / (_max - _min)

img = imread(sys.argv[1])
normalized = normalize(img)
imsave('normalized.png', normalized)