import PIL
from PIL import Image
from flask import Flask
import sys

app = Flask('__main__')

def build_hist(image, color):
    im = Image.open(app.root_path + '/' + image)
    loaded_img = im.load()
    w, h = im.size
    
    if (color == 'a'):
        r = [0] * 256    
        g = [0] * 256    
        b = [0] * 256    
        x = [0] * 256
    else :
        histogram = [0] * 256

    for i in range(w):
        for j in range(h):
            rgb_image = loaded_img[i,j]
            if(color == 'a'):
                r[rgb_image[0]] += 1
                g[rgb_image[1]] += 1
                b[rgb_image[2]] += 1
                x[int((rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3)] += 1
            elif(color == 'r'):
                histogram[rgb_image[0]] += 1
            elif(color == 'g'):
                histogram[rgb_image[1]] += 1
            elif(color == 'b'):
                histogram[rgb_image[2]] += 1
            else:
                histogram[int((rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3)] += 1  

    dim = float(w * h)
    if (color == 'a'):
        hist = [[0] for i in range(4)]
        for i in range(0, 256):
            hist[0].append(float(r[i])/dim)
            hist[1].append(float(g[i])/dim)
            hist[2].append(float(b[i])/dim)
            hist[3].append(float(x[i])/dim)
    else :
        hist = []
        for k in histogram:
            hist.append(float(k)/dim)
    return hist
    