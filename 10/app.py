import os, json
from flask import Flask, render_template, request, redirect
from rgbhist import *
from normalize import *
from chaincode import *
from thinning import *
from predict_ascii import *
from faceboundary import *
from convolution import conv, conv_kernel
import pickle, glob
import matplotlib
import numpy as np
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw
from scipy.misc import toimage
import numpy as np

import time

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ROOT_PATH'] = app.root_path
app_bone = []

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/1", methods=['GET'])
def main1():
    return render_template('1.html')

@app.route("/1", methods=['POST'])
def show_histogram():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    color = request.form.get('color')
    image.save(app.root_path + '/' + os.path.join(app.config['UPLOAD_FOLDER'], 'image.png'))
    plt.clf()
    if(color == 'a'):
        colorname = 'Picture'
        hist = build_hist(UPLOAD_FOLDER + '/image.png', 'a', app.root_path)
        plt.plot(hist[0], color=(1, 0, 0))
        plt.plot(hist[1], color=(0, 1, 0))
        plt.plot(hist[2], color=(0, 0, 1))
        plt.plot(hist[3], color=(0.66, 0.66, 0.66))
    else :
        if(color == 'r'):
            colorname = 'Red'
            plotcolor = (1, 0, 0)
        elif(color == 'g'):
            plotcolor = (0, 1, 0)
            colorname = 'Green'
        elif(color == 'b'):
            colorname = 'Blue'
            plotcolor = (0, 0, 1)
        else:
            colorname = 'Grayscale'
            plotcolor = (0.5, 0.5, 0.5)
        plt.plot(build_hist(UPLOAD_FOLDER + '/image.png', color, app.root_path), color=plotcolor)

    plt.savefig(app.root_path + '/' + 'static/images/plot.png')
    return json.dumps({'url_after': 'static/images/plot.png?' + str(time.time()) })

@app.route("/2", methods=['GET'])
def main2():
    return render_template('2.html')

@app.route("/2", methods=['POST'])
def show_normalized():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    method = request.form.get('method')
    img_path = 'static/images/image.png'
    image.save(app.root_path + '/' + img_path)
    if method == 'k':
        # kumulatif
        title = 'Cumulative'
        imagee = Image.open(app.root_path + '/' + img_path)
        new_image = normalize(imagee, app.root_path)
        norm_img_path = 'static/images/normalized_image.png'
        new_image.save(app.root_path + '/' + norm_img_path)
    else:
        # scaling
        title = 'Scaling'
        base_image = Image.open(app.root_path + '/' + img_path)
        width, height = base_image.size
        normalized_img = scaling(base_image, width, height, app.root_path)
        norm_img_path = 'static/images/normalized_image.png'
        normalized_img.save(app.root_path + '/' + norm_img_path)
        
    return json.dumps({'url_after': norm_img_path + '?' + str(time.time()) })

@app.route("/3", methods=['GET'])
def main3get():
    return render_template('3.html', url_before = '', url_after = '')

@app.route("/3", methods=['POST'])
def main3():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    image.save(app.root_path + '/' + img_path)
    equalizers = [0 for i in range(6)] 
    for i in range(6):
        equalizers[i] = int(request.form['myRange' + str(i+1)])
    to_edit = Image.open(app.root_path + '/' + img_path)
    new_image = equalize(to_edit, equalizers, app.root_path)
    norm_img_path = 'static/images/normalized_image.png'
    new_image.save(app.root_path + '/' + norm_img_path)
        
    return json.dumps({'url_after': norm_img_path + '?' + str(time.time()) })

@app.route("/4", methods=['GET'])
def main4get():
    return render_template('4.html', url_before = '', url_after = '')

@app.route("/4", methods=['POST'])
def main4post():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    image.save(app.root_path + '/' + img_path)
    chain = build_chaincode(img_path, app.root_path)
    with open(app.root_path + '/static/pickle/knn.pickle','rb') as handle:
        knn = pickle.load(handle)
    pred = knn.predict(chain)
    return json.dumps({'angka': pred[0]})

@app.route("/5", methods=['GET'])
def main5get():
    return render_template('5.html', url_before = '', url_after = '')

@app.route("/5", methods=['POST'])
def main5post():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    image.save(app.root_path + '/' + img_path)
    bone = thinning(img_path, app.root_path)
    global app_bone
    app_bone = bone
    bone_img = toimage(bone)
    bone_img_path = 'static/images/bone_image.png'
    bone_img.save(app.root_path + '/' + bone_img_path)
    return json.dumps({'url_after': bone_img_path + '?' + str(time.time()) })

@app.route("/6", methods=['GET'])
def main6get():
    return render_template('6.html', url_before = '', url_after = '')

@app.route("/6", methods=['POST'])
def predict_ascii():
    global app_bone
    if (app_bone == []):
        return json.dumps({'status':'Error1'})
    array_feature = get_feature_from_bone(app_bone)
    if(array_feature != []):
        karakter =  predict(array_feature)
    else:
        karakter = 'Not Found'
    return json.dumps({'karakter': karakter })

@app.route("/7", methods=['GET'])
def main7get():
    return render_template('7.html', url_before = '', url_after = '')

@app.route("/7", methods=['POST'])
def predict_letter():
    global app_bone
    with open(app.root_path + '/static/pickle/knn_letter.pickle','rb') as handle:
        knn = pickle.load(handle)
    if (app_bone == []):
        return json.dumps({'status':'Error1'})
    array_feature = get_feature_from_bone(app_bone)
    feature = get_feature_from_array(array_feature)
    if(array_feature != []):
        temp = []
        for j in range(len(feature)):
            if(j<=4):
                temp.append(feature[j])
            else:
                for k in feature[j]:
                    temp.append(k)
        karakter = knn.predict([temp])
    else:
        karakter = 'Not Found'
    return json.dumps({'karakter': karakter[0] })

@app.route("/8", methods=['GET'])
def main8get():
    return render_template('8.html', url_before = '', url_after = '')

@app.route("/8", methods=['POST'])
def convolution():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    
    method = request.form.get('method')
    image.save(app.root_path + '/' + img_path)

    new_image = conv(img_path, app.root_path, method, 0)

    norm_img_path = 'static/images/normalized_image.png'
    new_image.save(app.root_path + '/' + norm_img_path)
        
    return json.dumps({'url_after': norm_img_path + '?' + str(time.time()) })

@app.route("/9", methods=['GET'])
def main9get():
    return render_template('9.html', url_before = '', url_after = '')

@app.route("/9", methods=['POST'])
def kernel():
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    
    method = request.form.get('method')
    image.save(app.root_path + '/' + img_path)

    matrix = []
    for i in range(9):
        matrix.append(float(request.form.get('input'+str(i+1))))

    new_image = conv_kernel(img_path, app.root_path, matrix)

    norm_img_path = 'static/images/normalized_image.png'
    new_image.save(app.root_path + '/' + norm_img_path)
        
    return json.dumps({'url_after': norm_img_path + '?' + str(time.time()) })

@app.route("/10", methods=['GET'])
def main10get():
    return render_template('10.html', url_before = '', url_after = '')

@app.route("/10", methods=['POST'])
def main10():
    
    if 'imgFile' not in request.files:
        return json.dumps({'status':'Error1'})
    file = request.files['imgFile']
    if file.filename == '':
        return json.dumps({'status':'Error2'})
    image = request.files['imgFile']
    img_path = 'static/images/image.png'
    image.save(app.root_path + '/' + img_path)
    size = 480, 480
    image = Image.open(app.root_path + '/' + img_path)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(app.root_path + '/' + img_path)

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
    new_image_path = 'static/images/face_raw_image.png'
    new_image.save(app.root_path  + '/' + new_image_path)
    bounds = face_boundary(new_image_path, app.root_path)
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
        mouth_bounds = object_boundary(new_image_path, app.root_path, arr_mouth, "mouth")
        minb1, minb3 = 999, 999
        maxb0, maxb2 = 0, 0
        for mb in mouth_bounds:
            # draw.rectangle(((mb[1] + 1, mb[3] + 1), (mb[0] - 1, mb[2] - 1)), fill=None, outline="#0984e3")
            if maxb0 < mb[0]: maxb0 = mb[0]
            if maxb2 < mb[2]: maxb2 = mb[2]
            if minb1 > mb[1]: minb1 = mb[1]
            if minb3 > mb[3]: minb3 = mb[3]
        if minb1 != 0:
            draw.rectangle(((minb1 - 1, minb3 - 1), (maxb0 + 1, maxb2 + 1)), fill=None, outline="#0984e3")

        eye_top = face_top + (0.2 * face_height)
        eye_below = face_below - (0.5 * face_height)
        eye_right = face_right - (0.1 * face_width)
        eye_left = face_left + (0.1 * face_width)
        draw.rectangle(((eye_left, eye_top), (eye_right, eye_below)), fill=None, outline="#55efc4")
        arr_eye = [eye_left, eye_top, eye_right, eye_below]
        eye_bounds = object_boundary(new_image_path, app.root_path, arr_eye, "eye")
        for eb in eye_bounds:
            draw.rectangle(((eb[1]-1, eb[3]-1), (eb[0]+1, eb[2]+1)), fill=None, outline="#e84393")

    new_image = image
    new_image_path = 'static/images/face_detected_image.png'
    new_image.save(app.root_path  + '/' + new_image_path)
    return json.dumps({'url_after': new_image_path + '?' + str(time.time()) })

if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=8111)
    app.run(host='0.0.0.0',port=os.environ['PORT'])