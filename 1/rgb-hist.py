import PIL
from PIL import Image
from matplotlib import pyplot as plt
import sys

path = sys.argv[1]
color = sys.argv[2]

im = Image.open(path)
loaded_img = im.load()
w, h = im.size  

def build_hist(color):
    histogram = [0] * 256
    for i in range(w):
        for j in range(h):
            rgb_image = loaded_img[i,j]
            if(color == 'r'):
                histogram[rgb_image[0]] += 1
            elif(color == 'g'):
                histogram[rgb_image[1]] += 1
            elif(color == 'b'):
                histogram[rgb_image[2]] += 1
            else:
                histogram[sum(rgb_image)/3] += 1  
    hist = []
    for k in histogram:
        hist.append(float(k)/float(w * h))
    return hist
    
if(color == 'r'):
    plt.plot(build_hist(color), 'r')
elif(color == 'g'):
    plt.plot(build_hist(color), 'g')
elif(color == 'b'):
    plt.plot(build_hist(color), 'b')
else:
    plt.plot(build_hist(color), 'k')

plt.show()