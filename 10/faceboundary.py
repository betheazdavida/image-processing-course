# David T 13515131 
from PIL import Image, ImageDraw

from math import sqrt, trunc
import numpy as np
import sys


def face_detect(image, raw_image, root_path):
    image = Image.open(root_path + '/' + image)
    img = np.array(image)
    height, width, _ = img.shape
    new_image = np.zeros((img.shape[0], img.shape[1]))
    for y in range(height):
        for x in range(width):
            R = img[y][x][0]
            G = img[y][x][1]
            B = img[y][x][2]
            Y = 16 + (65.738/256)*R + (129.057/256*G) + (25.064/256)*B
            Cb = 128 - (37.945/256)*R - (74.494/256*G) + (112.439/256)*B
            Cr = 128 + (112.439/256)*R - (94.154/256*G) - (18.285/256)*B
            if(R > 95 and G > 40 and B > 20 and R > G and R > B and abs( R - G) > 15 and Cr > 135 and Cb > 85 and Y > 80 and Cr <= (1.5862*Cb) + 20
                and Cr >= 0.3448*Cb + 76.2069 and Cr >= (-4.5652*Cb)+234.5625 and Cr <= (-1.15*Cb)+301.75 and Cr <= (-2.2857*Cb)+432.85):
                new_image[y][x] = 1

    new_image = Image.fromarray(np.uint8(new_image*255))
    new_image_path = raw_image
    new_image.save(root_path  + '/' + new_image_path)
    bounds = face_boundary(new_image_path, root_path)
    draw = ImageDraw.Draw(image)
    
    for b in bounds:
        draw.rectangle(((b[1] + 1, b[3] + 1), (b[0] - 1, b[2] - 1)), fill=None, outline="red")
    
        # left, top
        # right, below
        face_top = b[3]
        face_below = b[2]
        face_left = b[1]
        face_right = b[0]
        face_height = b[2] - b[3]
        face_width = b[0] - b[1]
        
        mouth_top = face_top + (2.4 * (face_height/3.7))
        mouth_below = face_below - (0.1 * face_height)
        mouth_right = face_right - (0.19 * face_width)
        mouth_left = face_left + (0.21 * face_width)
        draw.rectangle(((mouth_left, mouth_top), (mouth_right, mouth_below)), fill=None, outline="#81ecec")
        arr_mouth = [mouth_left, mouth_top, mouth_right, mouth_below]
        mouth_bounds = object_boundary(new_image_path, root_path, arr_mouth, "mouth")
        minb1, minb3 = 999, 999
        maxb0, maxb2 = 0, 0
        for mb in mouth_bounds:
            # draw.rectangle(((mb[1] + 1, mb[3] + 1), (mb[0] - 1, mb[2] - 1)), fill=None, outline="#0984e3")
            if maxb0 < mb[0]: maxb0 = mb[0]
            if maxb2 < mb[2]: maxb2 = mb[2]
            if minb1 > mb[1]: minb1 = mb[1]
            if minb3 > mb[3]: minb3 = mb[3]
        if minb1 != 999:
            draw.rectangle(((minb1 - 1, minb3 - 1), (maxb0 + 1, maxb2 + 1)), fill=None, outline="#0984e3")

        eye_top = face_top + (0.2 * face_height)
        eye_below = face_below - (0.5 * face_height)
        eye_right = face_right - (0.1 * face_width)
        eye_left = face_left + (0.1 * face_width)
        draw.rectangle(((eye_left, eye_top), (eye_right, eye_below)), fill=None, outline="#55efc4")
        arr_eye = [eye_left, eye_top, eye_right, eye_below]
        eye_bounds = object_boundary(new_image_path, root_path, arr_eye, "eye")
        for eb in eye_bounds:
            draw.rectangle(((eb[1]-1, eb[3]-1), (eb[0]+1, eb[2]+1)), fill=None, outline="#e84393")

        nose_top = face_top + (0.45 * face_height)
        nose_below = face_below - (0.29 * face_height)
        nose_right = face_right - (0.26 * face_width)
        nose_left = face_left + (0.26 * face_width)
        draw.rectangle(((nose_left, nose_top), (nose_right, nose_below)), fill=None, outline="#55efc4")
        arr_nose = [nose_left, nose_top, nose_right, nose_below]
        nose_bounds = object_boundary(new_image_path, root_path, arr_nose, "nose")
        minb1, minb3 = 999, 999
        maxb0, maxb2 = 0, 0
        for nb in nose_bounds:
            if maxb0 < nb[0]: maxb0 = nb[0]
            if maxb2 < nb[2]: maxb2 = nb[2]
            if minb1 > nb[1]: minb1 = nb[1]
            if minb3 > nb[3]: minb3 = nb[3]
        if minb1 != 999:
            draw.rectangle(((minb1 - 6, minb3 - 10), (maxb0 + 6, maxb2 + 1)), fill=None, outline="#e67e22")

    new_image = image
    new_image_path = 'static/images/face_detected_image.png'
    new_image.save(root_path  + '/' + new_image_path)
    return new_image_path, mouth_bounds, eye_bounds, nose_bounds

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

    # for m in range(1, height-1):
    #     i = 0
    #     for n in range(1, width-1):
    #         img_pix[m,n] = i % 255
    #         i += 1
    # img.save('lool.png')

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
                        if(del_y > del_x*1.3):
                            bound[2] = bound[3] + del_x*1.3
                        #append as face
                        bounds.append(bound)
    return bounds

def object_boundary(image, root_path, arr, obj):
    print('-------------------------------------------entering object boundary: ' + obj)
    img = Image.open(root_path + '/' + image)
    img_pix = img.load()
    height, width = img.size
    bounds = []

    xt, yt, xb, yb = arr
    xt = trunc(xt) # left
    yt = trunc(yt) # top
    xb = trunc(xb) # right
    yb = trunc(yb) # below
    yy = yb - yt
    xx = xb - xt

    #remove lines
    for m in range(xt, xb):
        for n in range(yt, yb):
            if(img_pix[m,n] == 255 and ((img_pix[m,n-1] == 0 and img_pix[m,n+1] == 0) or (img_pix[m+1,n] == 0 and img_pix[m-1,n] == 0))):
                img_pix[m,n] = 0
    
    #iterate each pixels
    for m in range(xt, xb-1):
        for n in range(yt, yb-1):
            # find black pixels
            if(img_pix[m,n] == 0):
                density = 1
                img_pix[m,n] = 255
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
                            if (i >= xt and j >= yt and j < yb and i < xb):
                                if(img_pix[i,j] == 0):
                                    img_pix[i,j] = 255
                                    toFill.append([i,j])
                                    density += 1
                                    local_bound = [i,i,j,j]
                                    bound = [max(bound[0],local_bound[0]),min(bound[1],local_bound[1]),max(bound[2],local_bound[2]),min(bound[3],local_bound[3])]
                #bound size
                del_x = bound[0] - bound[1]
                del_y = bound[2] - bound[3]

                print("=-=--=-=-=-==-=-=--=")
                print("del_x: " + str(del_x))
                print("del_y: " + str(del_y))
                print("density: " + str(density))
                
                if obj == "mouth":
                    if(del_x > 5 and del_y > 1 and del_x > del_y and density > 12 and del_x/del_y > 3):
                        bounds.append(bound)
                    
                elif obj == "eye":
                    if(del_x > 6 and del_y > 2 and del_x > del_y and density > 30):
                        bounds.append(bound)

                elif obj == "nose":
                    delxy = abs(del_x - del_y)
                    if(del_y - del_x < 3 and delxy <= 8 and 23 <= density and density <= 80 and (del_x*del_y)/2.0 < density):
                        bounds.append(bound)
    return bounds