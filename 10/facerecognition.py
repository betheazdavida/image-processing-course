from PIL import Image, ImageDraw

from math import sqrt, trunc
import numpy as np
import sys

import numpy as np

def lbph_conv(image, root_path):
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
      threshold = img_pix[i, j]
      arr = ""
      for w in [-1, 0, 1]:
        for h in [-1, 0, 1]:
          if(w == 0 and h == 0):
            continue
          x = i + w
          y = j + h
          if x >= 0 and y >= 0 and x < width and y < height and img_pix[x,y] > threshold:
            arr += "1" 
          else: 
            arr += "0"
      new_img_pix[i, j] = int(arr,2)
  return new_img

def lbph(image, root_path, x , y):
  img = Image.open(root_path + '/' + image)
  img_pix = np.array(img)
  width, height = img.size
  print(width,height)
  hists = []
  for i in range(x):
    for j in range(y):
      crop = []
      for a in range(i*int(width/x), (i+1)*int(width/x)):
        temp = []
        for b in range(j*int(height/y), (j+1)*int(height/y)):
          temp.append(img_pix[b, a])
        crop.append(temp)
      # crop = img_pix[i*int(width/x):(i+1)*int(width/x), j*int(height/y):(j+1)*int(height/y)]
      hists.append(lbph_hist(np.array(crop)))
      # print(np.sum(lbph_hist(crop)))

  return hists
def lbph_sim(hist1, hist2):
  error = 0
  print(len(hist1), len(hist2))
  print(len(hist1[2]), len(hist2[4]))
  for i in range(len(hist1)):
    for j in range(255):
      error += (hist1[i][j] - hist2[i][j])**2
  return sqrt(error)

def lbph_hist(matrix):
  w, h = matrix.shape
  
  histogram = [0] * 256
  for i in range(w):
    for j in range(h):
        histogram[matrix[i, j]] += 1
  return histogram