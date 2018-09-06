import os
from flask import Flask, render_template, request, redirect
from rgbhist import *
from normalize import *
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from PIL import Image

from werkzeug import secure_filename
import time

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/1")
def main1():
    return render_template('1.html')

@app.route("/2")
def main2():
    return render_template('2.html')

@app.route("/histogram", methods=['POST'])
def show_histogram():
    if 'imgFile' not in request.files:
        return 'No selected file'
    file = request.files['imgFile']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return 'No selected file'
    image = request.files['imgFile']
    color = request.form.get('color')
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename)))
    plt.clf()
    if(color == 'a'):
        colorname = 'Picture'
        hist = build_hist(UPLOAD_FOLDER + '/' + secure_filename(image.filename), 'a')
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
        plt.plot(build_hist(UPLOAD_FOLDER + '/' + secure_filename(image.filename), color), color=plotcolor)

    plt.savefig('static/images/plot.png')
    return render_template('plot.html', title = colorname + ' histogram', url ='static/images/plot.png?' + str(time.time()))

@app.route("/normalize", methods=['POST'])
def show_normalized():
    if 'imgFile' not in request.files:
        return 'No selected file'
    file = request.files['imgFile']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return 'No selected file'
    image = request.files['imgFile']
    method = request.form.get('method')
    img_path = 'static/images/image.png'
    image.save(img_path)
    if method == 'k':
        # kumulatif
        title = 'Cumulative'
        imagee = Image.open(img_path)
        new_image = normalize(imagee)
        norm_img_path = 'static/images/normalized_image.png'
        new_image.save(norm_img_path)
    else:
        # scaling
        title = 'Scaling'
        base_image = Image.open(img_path)
        width, height = base_image.size
        normalized_img = scaling(base_image, width, height)
        norm_img_path = 'static/images/normalized_image.png'
        normalized_img.save(norm_img_path)
        
    return render_template('result.html', title = 'Normalized Picture (' + title + ')', url_before = img_path + '?' + str(time.time()), url_after = norm_img_path + '?' + str(time.time()))

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
