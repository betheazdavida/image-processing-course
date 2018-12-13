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
    raw_img_path = 'static/images/face_raw_image.png'
    new_image_path ,_, _, _ = face_detect(img_path, raw_img_path, app.root_path)
    return json.dumps({'url_after': new_image_path + '?' + str(time.time()) })

@app.route("/11", methods=['GET'])
def main11get():
    return render_template('11.html', url_before = '', url_after = '')

@app.route("/11", methods=['POST'])
def main11():
    
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
    raw_img_path = 'static/images/face_raw_image.png'
    new_image_path ,a, b, c = face_detect(img_path, raw_img_path, app.root_path)
    raw_img = Image.open(app.root_path + '/' + raw_img_path)
    raw_img = np.array(raw_img)
    print(a,b,c)
    return json.dumps({'url_after': new_image_path + '?' + str(time.time()) })

if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=8111)
    app.run(host='0.0.0.0',port=os.environ['PORT'])