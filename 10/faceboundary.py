# David T 13515131 
from PIL import Image
from math import sqrt
import numpy as np
import sys


def face_boundary(image, root_path):
    img = Image.open(root_path + '/' + image)
    img_pix = img.load()
    height, width = img.size
    bounds = []
    #remove lines
    for m in range(1, height-1):
        for n in range(1, width-1):
            if(img_pix[m,n] == 255 and ((img_pix[m,n-1] == 0 and img_pix[m,n+1] == 0) or (img_pix[m+1,n] == 0 and img_pix[m-1,n] == 0))):
                img_pix[m,n] = 0

    #iterate each pixels
    for m in range(1, height-1):
        for n in range(1, width-1):
            # find white pixels
            if(img_pix[m,n] == 255):
                density = 1
                img_pix[m,n] = 0
                #visit all neighbors and find bound: max x, min x, max y, min y
                toFill = []
                toFill.append([m,n])
                bound = [m,m,n,n]
                while toFill:
                    y,x = toFill.pop()
                    for w in [-1, 0, 1]:
                        if(w == 0):
                            h_range = [-1, 1]
                        else:
                            h_range = [0]
                        for h in h_range:
                            i = y + w
                            j = x + h
                            if (i >= 0 and j >= 0 and j < width and i < height):
                                if(img_pix[i,j] == 255):
                                    img_pix[i,j] = 0
                                    toFill.append([i,j])
                                    density += 1
                                    local_bound = [i,i,j,j]
                                    bound = [max(bound[0],local_bound[0]),min(bound[1],local_bound[1]),max(bound[2],local_bound[2]),min(bound[3],local_bound[3])]
                #bound size
                del_x = bound[0] - bound[1]
                del_y = bound[2] - bound[3]
                #some rules to decide face or not
                if(del_x > 15 and  del_y > 15 and del_y < 2.5* del_x and del_y > del_x):
                    density = density/((bound[0] - bound[1])*(bound[2] - bound[3]) + 1)
                    print(bound, density)
                    if(density > 0.35):
                        #remove neck
                        if(del_y > del_x*1.2):
                            bound[2] = bound[3] + del_x*1.2
                        #append as face
                        bounds.append(bound)


    # print(bounds)
    return bounds
