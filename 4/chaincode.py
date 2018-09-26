import sys
import PIL
from PIL import Image
import numpy as np
from flask import Flask

app = Flask('__main__')
sys.setrecursionlimit(50000)

def build_chaincode(image):
    np.set_printoptions(threshold=np.nan)
    im = Image.open(app.root_path + '/' + image)
    image = im.load()
    w, h = im.size
    #quantize image to 0 and 1 value
    quantitized_image = np.zeros((w + 2, h + 2), dtype=int)
    # print('  ', end='')
    # for j in range(h):
    #     print(j%10, end='')
    # print()
    for i in range(w):
        # print(i, end=' ')
        # if(i < 10):
            # print(' ', end='')
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

        #     print(quantitized_image[i + 1, j + 1], end='')
        # print()
    retry =3
    chain_codes = []
    steps = 0
    for i in range(w):
        for j in range(h):

            if (quantitized_image[i,j] == 1):
                m = i
                n = j - 1
                quantitized_image[m,n] = 3 #3 menandakan titik awal
                chain_code = np.zeros((8), dtype=int) # index 0 = utara, 1 = timur laut, dst
                del_m = 0
                del_n = 0
                while True:

                    # print(m,n)
                    if(is_surrounding_black(quantitized_image, m - 1, n)):
                        del_m = - 1
                        del_n = 0
                        chain_code[0] = chain_code[0] + 1
                    elif(is_surrounding_black(quantitized_image, m, n + 1)):
                        del_m = 0
                        del_n = 1
                        chain_code[2] = chain_code[2] + 1
                    elif(is_surrounding_black(quantitized_image, m + 1, n)):
                        del_n = 0
                        del_m = 1
                        chain_code[4] = chain_code[4] + 1
                    elif(is_surrounding_black(quantitized_image, m, n - 1)):
                        del_m = 0
                        del_n = - 1
                        chain_code[6] = chain_code[6] + 1
                    elif(is_surrounding_black(quantitized_image, m - 1, n + 1)):
                        del_m = - 1
                        del_n = 1
                        chain_code[1] = chain_code[1] + 1
                    elif(is_surrounding_black(quantitized_image, m + 1, n + 1)):
                        del_m = 1
                        del_n = 1
                        chain_code[3] = chain_code[3] + 1
                    elif(is_surrounding_black(quantitized_image, m + 1, n - 1)):
                        del_m = 1
                        del_n = - 1
                        chain_code[5] = chain_code[5] + 1
                    elif(is_surrounding_black(quantitized_image, m - 1, n - 1)):
                        del_m = - 1
                        del_n = - 1
                        chain_code[7] = chain_code[7] + 1
                    else: 
                        retry = retry -1
                        # quantitized_image[m,n] = 4
                        # print('  ', end='')
                        # for r in range(h):
                        #     print(r%10, end='')
                        # print()
                        # for y in range(w):
                        #     print(y, end=' ')
                        #     if(y < 10):
                        #         print(' ', end='')
                        #     for r in range(h):
                        #         print(quantitized_image[y + 1, r + 1], end='')
                        #     print()
                        if(retry == 0):
                            return
                        if(backtrace(quantitized_image, m - 1, n)):
                            del_m = - 1
                        elif(backtrace(quantitized_image, m, n + 1)):
                            del_m = 0
                            del_n = 1
                        elif(backtrace(quantitized_image, m, n - 1)):
                            del_m = 0
                            del_n = - 1
                        elif(backtrace(quantitized_image, m + 1, n)):
                            del_n = 0
                            del_m = 1
                            del_n = 0
                        elif(backtrace(quantitized_image, m + 1, n + 1)):
                            del_m = 1
                            del_n = 1
                        elif(backtrace(quantitized_image, m - 1, n + 1)):
                            del_m = - 1
                            del_n = 1
                        elif(backtrace(quantitized_image, m + 1, n - 1)):
                            del_m = 1
                            del_n = - 1
                        elif(backtrace(quantitized_image, m - 1, n - 1)):
                            del_m = - 1
                            del_n = - 1
                        else:
                            return

                    m = m + del_m
                    n = n + del_n
                    steps = steps + 1


                    quantitized_image[m,n] = 2 #2 menandakan sudah diperiksa
                    if steps > 10:
                        if(is_finish(quantitized_image,m,n)):
                            break
                mark_area(quantitized_image, i, j)
                chain_codes.append(chain_code)
                # print('  ', end='')
                # for r in range(h):
                #     print(r%10, end='')
                # print()
                # for y in range(w):
                #     print(y, end=' ')
                #     if(y < 10):
                #         print(' ', end='')
                #     for r in range(h):
                #         print(quantitized_image[y + 1, r + 1], end='')
                #     print()
    return chain_codes

def is_surrounding_black(quantitized_image, m, n):
    
    return ((quantitized_image[m,n] == 0) and (quantitized_image[m - 1, n] == 1  or quantitized_image[m, n + 1] == 1 or  quantitized_image[m + 1, n] == 1 or quantitized_image[m, n - 1] == 1))
def backtrace(quantitized_image, m, n):
    
    return ((quantitized_image[m,n] == 2) and (quantitized_image[m - 1, n] == 0  or quantitized_image[m, n + 1] == 0 or  quantitized_image[m + 1, n] == 0 or quantitized_image[m, n - 1] == 0))

def is_finish(quantitized_image, m, n):
    return (quantitized_image[m - 1, n] == 3  or quantitized_image[m, n + 1] == 3 or  quantitized_image[m + 1, n] == 3 or quantitized_image[m, n - 1] == 3 or quantitized_image[m + 1, n-1] == 3  or quantitized_image[m-1, n + 1] == 3 or  quantitized_image[m + 1, n+1] == 3 or quantitized_image[m-1, n - 1] == 3)
def mark_area(quantitized_image, m, n):
    if (quantitized_image[m,n] == 1):
        quantitized_image[m,n] = 5
    if (quantitized_image[m - 1, n] == 1):
        mark_area(quantitized_image, m - 1, n)
    if (quantitized_image[m, n + 1] == 1):
        mark_area(quantitized_image, m, n + 1)
    if (quantitized_image[m + 1, n] == 1):
        mark_area(quantitized_image, m + 1, n)
    if (quantitized_image[m, n - 1] == 1):
        mark_area(quantitized_image, m, n - 1)