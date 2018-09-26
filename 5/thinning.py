import sys
import PIL
from PIL import Image
import numpy as np
from flask import Flask

app = Flask('__main__')
sys.setrecursionlimit(50000)

def thinning(image):
    np.set_printoptions(threshold=np.nan)
    im = Image.open(app.root_path + '/' + image)
    image = im.load()
    w, h = im.size
    #quantize image to 0 and 1 value
    quantitized_image = np.zeros((w + 2, h + 2), dtype=int)
    for i in range(w):
        for j in range(h):
            rgb_image = image[i, j]

            if (len(rgb_image) == 4):
                if (rgb_image[3] > 0):
                    grayscale = (rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3
                else:
                    grayscale = 9999
            else:
                grayscale = (rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3

            if(grayscale < 127):
                quantitized_image[i + 1, j + 1] = 1
      
    changing1 = changing2 = 1        #  the points to be removed (set as 0)  
    while changing1 or changing2:   #  iterates until no further changes occur in the image
        # Step 1
        changing1 = []
        rows, columns = quantitized_image.shape               # x for rows, y for columns
        for x in range(1, rows - 1):                     # No. of  rows
            for y in range(1, columns - 1):            # No. of columns
                P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, quantitized_image)
                if (quantitized_image[x][y] == 1     and    # Condition 0: Point P1 in the object regions 
                    2 <= sum(n) <= 6   and    # Condition 1: 2<= N(P1) <= 6
                    transitions(n) == 1 and    # Condition 2: S(P1)=1  
                    P2 * P4 * P6 == 0  and    # Condition 3   
                    P4 * P6 * P8 == 0):         # Condition 4
                    changing1.append((x,y))
        for x, y in changing1: 
            quantitized_image[x][y] = 0
        # Step 2
        changing2 = []
        for x in range(1, rows - 1):
            for y in range(1, columns - 1):
                P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, quantitized_image)
                if (quantitized_image[x][y] == 1   and        # Condition 0
                    2 <= sum(n) <= 6  and       # Condition 1
                    transitions(n) == 1 and      # Condition 2
                    P2 * P4 * P8 == 0 and       # Condition 3
                    P2 * P6 * P8 == 0):            # Condition 4
                    changing2.append((x,y))    
        for x, y in changing2: 
            quantitized_image[x][y] = 0


    return quantitized_image

def neighbours(x,y,image):
    "Return 8-neighbours of image point P1(x,y), in a clockwise order"
    img = image
    x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
    return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1],     # P2,P3,P4,P5
                img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]    # P6,P7,P8,P9

def transitions(neighbours):
    "No. of 0,1 patterns (transitions from 0 to 1) in the ordered sequence"
    n = neighbours + neighbours[0:1]      # P2, P3, ... , P8, P9, P2
    return sum( (n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]) )  # (P2,P3), (P3,P4), ... , (P8,P9), (P9,P2)