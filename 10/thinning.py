import sys
import PIL
from PIL import Image
import numpy as np
import os
sys.setrecursionlimit(50000)
np.set_printoptions(threshold=np.nan)

global_image = []
threshold = 0.15
def thinning(image, root_path):
    im = Image.open(root_path + '/' + image)
    image = im.load()
    h, w = im.size
    #quantize image to 0 and 1 value
    quantitized_image = np.zeros((w + 2, h + 2), dtype=int)
    for i in range(w):
        for j in range(h):
            rgb_image = image[j, i]
            if(isinstance(rgb_image, int)):
                grayscale = rgb_image
            elif (len(rgb_image) == 4):
                if (rgb_image[3] > 0):
                    grayscale = (rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3
                else:
                    grayscale = 9999
            else:
                grayscale = (rgb_image[0] + rgb_image[1] + rgb_image[2]) / 3

            if(grayscale < 120):
                quantitized_image[i + 1, j + 1] = 1
    #Algoritma Zhang-suen
    changing1 = changing2 = 1        #  the points to be removed
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
    # "Return 8-neighbours of image point P1(x,y), in a clockwise order"
    img = image
    x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
    return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1],     # P2,P3,P4,P5
                img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]    # P6,P7,P8,P9

def transitions(neighbours):
    #"No. of 0,1 patterns (transitions from 0 to 1) in the ordered sequence"
    n = neighbours + neighbours[0:1]      # P2, P3, ... , P8, P9, P2
    return sum( (n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]) )  # (P2,P3), (P3,P4), ... , (P8,P9), (P9,P2)

def get_feature_from_bone(bone):
    h, w = bone.shape
    global global_image
    global_image = bone
    datas = []
    for i in range(h):
        for j in range(w):
            if(global_image[i, j] == 1): #jika bertemu titik yg belum diperiksa
                if(path_count(i, j, global_image) == 1): #jika titik di ujung
                    corners = []
                    corners.append([i,j])
                    global_image[i, j] = 2
                    circles, branchs, corner, chain_codes= check(i, j)
                    corners = corners + corner
                    data = []
                    circles = circles/2
                    data.extend([int(circles),branchs, corners, chain_codes])
                    datas.append(data)
                elif(path_count(i, j, global_image) == 2): #jika titik di tengah
                    corners = []
                    global_image[i, j] = 2
                    circles, branchs, corner, chain_codes = check(i, j)
                    data = []
                    corners = corners + corner
                    circles = circles/2
                    #hapus cabang palsu pada titik awal
                    for x in branchs:
                        if(x[0] == i and x[1] == j):
                            branchs.remove(x)
                    data.extend([int(circles), branchs, corners, chain_codes])
                    datas.append(data)
                elif(path_count(i, j, global_image) == 0): # jika hanya satu titik
                    corners = []
                    corners.append([i,j])
                    global_image[i, j] = 2
                    circles = 0
                    branchs = []
                    chain_codes = []
                    data = []
                    data.extend([int(circles),branchs, corners, chain_codes])
                    datas.append(data)

                #clean tails and empty chaincodes
                if(data[3] != []):
                    max_length = len(max(data[3], key=len))
                    removed = [item for item in data[3] if(len(item) < ((max_length - 2) * threshold) +2)]
                    data[3] = [item for item in data[3] if(len(item) >= ((max_length - 2) * threshold) +2)]
                    #menghapus cabang dan titik ujung palsu
                    for x in removed:
                        if(len(x) > 2):
                            a = x[0]
                            b = x[-1]
                            for y in data[1]:
                                if((abs(a[0] - y[0]) <= 1 and abs(a[1] - y[1] <= 1)) or (abs(b[0] - y[0]) <= 1 and abs(b[1] - y[1] <= 1))):
                                    data[1].remove(y)
                                    for z in data[2]:
                                        if(a == z or b == z):
                                            data[2].remove(z)                
                


    datas.append([h,w])
    return datas
def get_feature_from_array(array_feature):
    n_strokes = len(array_feature) - 1
    n_circle = array_feature[0][0]
    n_branch = len(array_feature[0][1])
    n_corner = len(array_feature[0][2])
    n_chaincode = len(array_feature[0][3])
    h,w = array_feature[-1]
    upleft = 0
    upright = 0
    downleft = 0
    downright = 0
    for x in array_feature[0][2]:
        if(x[0] < h/2 and x[1] < w / 2):
            upleft += 1
        if(x[0] < h/2 and x[1] > w / 2):
            upright += 1
        if(x[0] > h/2 and x[1] < w / 2):
            downleft += 1
        if(x[0] > h/2 and x[1] > w / 2):
            downright += 1
    chaincodes = np.zeros(8, dtype = int)

    for m in range (n_strokes):
        for x in array_feature[m][3]:
            for n in range(1, len(x) - 1):
                chaincodes[x[n]] += 1    
    corner_pos = [upleft, upright, downleft, downright]
    return [n_strokes,n_circle,n_branch,n_corner,n_chaincode, corner_pos, chaincodes]

def check(i,j):
    global global_image
    corners = []
    circles = 0
    branchs = []
    chain_codes = []
    chain_code = []
    chain_code.append([i,j])
    branch_path = 0
    #penelusuran selama masih ada jalan
    while (path_count(i,j, global_image) >= 1):
        if(path_count(i,j, global_image) == 1):
            global_image[i,j] = 2
            i, j, code = next_path(i, j, global_image)
            chain_code.append(code)
        else: #bertemu cabang, panggil fungsi secara rekursif
            global_image[i,j] = 3
            list_of_path = path_list(i,j,global_image)
            branch_path = len(list_of_path)
            for x in list_of_path:
                a,b = x
                circle, branch, corner, rec_chain_code = check(a, b)
                circles = circles + circle
                corners = corners + corner
                branchs = branchs + branch
                chain_codes = chain_codes + rec_chain_code
    #penghitungan properti gambar hasil penelurusan
    if (stop_near_branch(i,j,global_image) and passed_neighbor(i,j,global_image)):
        circles += 1
        global_image[i,j] = 2
        #print("circles", i, j)
    elif(global_image[i,j] == 1):
        corners.append([i,j])
        global_image[i,j] = 2
        #print("corners", i, j)
    elif(global_image[i,j] == 3):
        #print("branch", i, j)
        branchs.append([i,j,branch_path])
    chain_code.append([i,j])
    chain_codes.append(chain_code)
    data = []
    data.extend([circles,branchs, corners, chain_codes])
    return data

#menghitung jumlah jalan yang mungkin
def path_count(x, y, image):
    neighbor = neighbours(x, y, image)
    before = neighbor[len(neighbor) - 1]
    a = [[x-1,y],[x-1,y+1],[x,y+1],[x+1,y+1],[x+1,y],[x+1,y-1],[x, y-1],[x-1,y-1]]
    path = 0
    for i in range (len(neighbor)):
        if(neighbor[i] == 1 and before == 0):
            if(not(stop_near_branch(x,y, image)) or not(stop_near_branch(a[i][0], a[i][1], image))):
                path += 1
        before = neighbor[i]
    return path

#True jika berada di dekat cabang
def stop_near_branch(x, y, image):
    neighbor = neighbours(x, y, image)
    for i in range (len(neighbor)):
        if(neighbor[i] == 3):
            return True
    return False
#True jika berada di dekat titik yang telah dilewati
def passed_neighbor(x, y, image):
    neighbor = neighbours(x, y, image)
    for i in range (len(neighbor)):
        if(neighbor[i] == 2):
            return True
    return False
#Mengembalikan daftar titik yang bisa dilalui
def path_list(x, y, image):
    neighbor = neighbours(x, y, image)
    a = [[x-1,y],[x-1,y+1],[x,y+1],[x+1,y+1],[x+1,y],[x+1,y-1],[x, y-1],[x-1,y-1]]
    path_straight = []
    path_oblique = []
    before = neighbor[len(neighbor) - 1]
    for i in range (len(neighbor)):
        if(neighbor[i] == 1 and before == 0):
            if(i % 2 == 0):
                path_straight.append(a[i])
            else:
                path_oblique.append(a[i])
        before = neighbor[i]
    return path_straight + path_oblique

#Menentukan titik selanjutnya yang akan diambil
def next_path(x, y, image):
    neighbor = neighbours(x, y, image)
    index = 0
    a = [[x-1,y],[x-1,y+1],[x,y+1],[x+1,y+1],[x+1,y],[x+1,y-1],[x, y-1],[x-1,y-1]]
    for i in range (len(neighbor)):
        if(neighbor[i] == 1 and i % 2 == 0):
            b = a[i]
            b.append(i)
            return b
    for i in range (len(neighbor)):
        if(neighbor[i] == 1 and i % 2 == 1):
            b = a[i]
            b.append(i)
            return b
    return [-1,-1, -1]