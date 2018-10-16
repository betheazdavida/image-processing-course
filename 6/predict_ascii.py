import sys
import PIL
from PIL import Image
import numpy as np

def predict(array_feature):
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
    x = [upleft, upright, downleft, downright]

    if(n_strokes == 3):
        return '%'
    elif(n_strokes == 2):
        if(n_circle == 0):
            if(n_branch == 0):
                if(n_corner == 1):
                    return 'N w'
                if(n_corner == 2):
                    if(x[0] == 1 and x[1] == 1 and x[2] == 0 and x[3] == 0):
                        return '='
                    if(x[0] == 2 and x[1] == 0 and x[2] == 0 and x[3] == 0):
                        return ';'
            elif(n_branch == 1):
                if(n_corner == 2):
                    return 'n'
                if(n_corner == 4):
                    return '+'
        elif(n_circle == 1):
            if(n_branch == 0):
                return 'X'
            elif(n_branch == 1):
                if(n_corner == 0):
                    return '9'
                if(n_corner == 3):
                    return 'x'          
    elif(n_strokes == 1):
        if(n_circle == 0):
            if(n_branch == 0):
                if(n_corner == 2):
                    if(n_chaincode == 1):
                        if(x[0] == 0 and x[1] == 0 and x[2] == 1 and x[3] == 1):
                            return '_'
                        if(x[0] == 0 and x[1] == 0 and x[2] == 2 and x[3] == 1):
                            return '-'
                        if(x[0] == 0 and x[1] == 1 and x[2] == 0 and x[3] == 1):
                            return ') < I ['
                        if(x[0] == 0 and x[1] == 1 and x[2] == 1 and x[3] == 0):
                            return '/ J'
                        if(x[0] == 1 and x[1] == 0 and x[2] == 0 and x[3] == 1):
                            return '\' L Z \\ z'
                        if(x[0] == 1 and x[1] == 0 and x[2] == 1 and x[3] == 0):
                            return '* 7 > ] l | } '
                        if(x[0] == 1 and x[1] == 1 and x[2] == 0 and x[3] == 0):
                            return 'U V W v ~'
                        if(x[0] == 2 and x[1] == 0 and x[2] == 0 and x[3] == 0):
                            return '( `'            
                    if(n_chaincode == 2):
                        if(x[0] == 0 and x[1] == 1 and x[2] == 0 and x[3] == 1):
                            return 'C c {'
                        if(x[0] == 0 and x[1] == 1 and x[2] == 1 and x[3] == 0):
                            return 'S r s'
                        if(x[0] == 0 and x[1] == 2 and x[2] == 0 and x[3] == 0):
                            return 'G'
                        if(x[0] == 1 and x[1] == 0 and x[2] == 0 and x[3] == 1):
                            return '1 2 ?'
                        if(x[0] == 1 and x[1] == 1 and x[2] == 0 and x[3] == 0):
                            return '^ u'
                    if(n_chaincode == 3):
                        if(x[0] == 0 and x[1] == 0 and x[2] == 1 and x[3] == 1):
                            return 'M'
                        if(x[0] == 0 and x[1] == 1 and x[2] == 1 and x[3] == 0):
                            return '5'
                        if(x[0] == 1 and x[1] == 0 and x[2] == 1 and x[3] == 0):
                            return '3'
                    if(n_chaincode == 4):
                        return 'g'
                if(n_corner == 3):
                    return 't'
            elif(n_branch == 1):
                if(n_corner == 2):
                    return 'a'
                if(n_corner == 3):
                    if(n_chaincode == 3):
                        if(x[0] == 1 and x[1] == 0 and x[2] == 1 and x[3] == 1):
                            return 'h'
                        if(x[0] == 1 and x[1] == 1 and x[2] == 1 and x[3] == 0):
                            return 'T Y y'
                    if(n_chaincode == 4):
                        if(x[0] == 0 and x[1] == 2 and x[2] == 0 and x[3] == 1):
                            return 'E'
                        if(x[0] == 0 and x[1] == 2 and x[2] == 1 and x[3] == 0):
                            return 'F'
                    if(n_chaincode == 5):
                        return 'm'
                if(n_corner == 4):
                    if(x[0] == 1 and x[1] == 2 and x[2] == 1 and x[3] == 0):
                        return 'f'
                    if(x[0] == 2 and x[1] == 1 and x[2] == 1 and x[3] == 0):
                            return ','                  
                    return ', f'
            elif(n_branch == 2):
                return 'H K k'
        elif(n_circle == 1):
            if(n_branch == 0):
                if(n_corner == 0):
                    return '0 D O o'
                if(n_corner == 1):
                    if(n_chaincode == 2):
                        return 'Q'
                    if(n_chaincode == 3):
                        return '4 @'                        
            elif(n_branch == 1):
                if(n_corner == 1):
                    if(n_chaincode == 3):
                        if(x[0] == 0 and x[1] == 0 and x[2] == 0 and x[3] == 1):
                            return 'e'
                        if(x[0] == 0 and x[1] == 0 and x[2] == 1 and x[3] == 0):
                                return 'P'
                        if(x[0] == 0 and x[1] == 1 and x[2] == 0 and x[3] == 0):
                            return '6 d'
                        if(x[0] == 1 and x[1] == 0 and x[2] == 0 and x[3] == 0):
                                return 'b'
                    if(n_chaincode == 4):
                        if(x[0] == 0 and x[1] == 0 and x[2] == 0 and x[3] == 1):
                            return 'q'
                        if(x[0] == 0 and x[1] == 0 and x[2] == 1 and x[3] == 0):
                            return 'p'
            elif(n_branch == 2):
                if(n_corner == 2):
                    return 'A R'
                if(n_corner == 3):
                    return '$'
                if(n_corner == 8):
                    return '#'
        elif(n_circle == 2):
            if(n_branch == 1):
                return '&'
            elif(n_branch == 2):
                return '8 B'    
    return 'belum dapat diprediksi'