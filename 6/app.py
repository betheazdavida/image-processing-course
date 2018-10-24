import os, json
from flask import Flask, render_template, request, redirect
from rgbhist import *
from normalize import *
from chaincode import *
from thinning import *
from predict_ascii import *
import pickle, glob
import matplotlib
import numpy as np
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from PIL import Image
from scipy.misc import toimage

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


if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=8111)
    app.run(host='0.0.0.0',port=os.environ['PORT'])

    # i = 33
    # a = []
    # for nama_file in sorted(glob.glob('images/*')):
    #     try:
    #         bone = thinning(nama_file, app.root_path)
    #         array_feature = get_feature_from_bone(bone)
    #         print (array_feature)
    #         n_strokes = len(array_feature) - 1
    #         n_circle = array_feature[0][0]
    #         n_branch = len(array_feature[0][1])
    #         n_corner = len(array_feature[0][2])
    #         n_chaincode = len(array_feature[0][3])
    #         h,w = array_feature[-1]
    #         upleft = 0
    #         upright = 0
    #         downleft = 0
    #         downright = 0
    #         for x in array_feature[0][2]:
    #             if(x[0] < h/2 and x[1] < w / 2):
    #                 upleft += 1
    #             if(x[0] < h/2 and x[1] > w / 2):
    #                 upright += 1
    #             if(x[0] > h/2 and x[1] < w / 2):
    #                 downleft += 1
    #             if(x[0] > h/2 and x[1] > w / 2):
    #                 downright += 1
    #         chaincodes = np.zeros(8, dtype = int)
    #         corner_pos = [upleft, upright, downleft, downright]
    #         a.append([chr(i) ,n_strokes,n_circle,n_branch,n_corner,n_chaincode, corner_pos])

    #     except Exception as e:
    #         print(chr(i), "Gagal")

    #     i += 1
    # a = sorted(a, key = lambda x: (x[1], x[2], x[3], x[4], x[5], x[6][0], x[6][1], x[6][2], x[6][3]))
    # for x in a:
    #     print(x)