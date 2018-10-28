from PIL import Image
import numpy as np

def median(arr):
  return sorted(arr)[4]

def gradient(arr):
  return max([abs(arr[0+i]-arr[8-i]) for i in range(4)])

def difference(arr):
  return max([abs(arr[i]-arr[4]) for i in range(9)])

def conv(image, root_path, method):
  # open image
  img = Image.open(root_path + '/' + image)
  
  # convert to grayscale
  img = img.convert('L')
  img_pix = img.load()

  new_img = img.copy()
  new_img_pix = new_img.load()

  # convolution
  width, height = img.size
  for i in range(width):
    for j in range(height):
      arr = []
      for w in [-1, 0, 1]:
        for h in [-1, 0, 1]:
          x = i + w
          y = j + h
          arr.append(img_pix[x, y]) if x >= 0 and y >= 0 and x < width and y < height else arr.append(-1)
      new_img_pix[i, j] = median(arr) if method == '1' else gradient(arr) if method == '2' else difference(arr)
  return new_img