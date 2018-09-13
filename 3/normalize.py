import sys
import os.path
import math
import numpy as np
from PIL import Image

def calculate_histogram(matrix):
    _, _, channel = matrix.shape
    flat_matrix = matrix.flatten()
    histogram = np.zeros((256, channel))
    for i, val in enumerate(flat_matrix):
        histogram[val][i % channel] += 1
    return histogram
def create_equalizer_histogram(matrix, equalizer):
    _, _, channel = matrix.shape
    histogram = np.zeros((256, channel))
    for i in range(256):
        index = int(i / 50)

        if index > len(equalizer) - 2 :
            index = len(equalizer) - 2
        value = equalizer[index] + (((equalizer[index + 1] - equalizer[index])/50) * (i % 50))
        for j in range(channel):
            histogram[i][j] = value
    
    return histogram

def cumulative_equalizer(matrix, histogram):
    map_value_to_cumulative = {}

    height, width, channel = matrix.shape
    cumulative_value = np.zeros(channel)
    for value, freq in enumerate(histogram):
        cumulative_value = [cumulative_value[i] + freq[i] for i in range(channel)]
        map_value_to_cumulative[value] = cumulative_value

    total_frequency = width * height
    result = np.zeros(matrix.shape)
    for y in range(height):
        for x in range(width):
            initial_value = matrix[y][x]
            result[y][x] = [math.floor(float(map_value_to_cumulative[v][c]) / float(total_frequency) * 255) for c, v in enumerate(initial_value)]
    for i in result:
        for j in i:
            if(j[0]>255):
                j[0] = 255
            if(j[1]>255):
                j[1] = 255
            if(j[2]>255):
                j[2] = 255
    return result

def normalize(base_image):
    base_image = resize(base_image, 600, 400)
    matrix = np.array(base_image)
    result_matrix = cumulative_equalizer(matrix, calculate_histogram(matrix))
    result_image = Image.fromarray(np.uint8(result_matrix))
    return result_image

def scaling(base_image,w,h):
    base_image = resize(base_image, 600, 400)
    histogram = calculate_histogram(np.array(base_image))
    sum_hist = 0
    for i in range(len(histogram)):
        sum_hist += (histogram[i][0] + histogram[i][1] + histogram[i][2])/3
    covered_area = sum_hist * 0.9
    sum_hist = 0
    for i in range(len(histogram)):
        sum_hist += (histogram[i][0] + histogram[i][1] + histogram[i][2])/3
        if(sum_hist > covered_area):
            _max = i
            break
    _min = 0
    normalized_img = np.array(base_image) * (255 / _max)
    for i in normalized_img:
        for j in i:
            if(j[0]>255):
                j[0] = 255
            if(j[1]>255):
                j[1] = 255
            if(j[2]>255):
                j[2] = 255
    result_image = Image.fromarray(np.uint8(normalized_img))
    return result_image

def equalize(base_image, equalizer):
    base_image = resize(base_image, 600, 400)   
    matrix = np.array(base_image)
    result_matrix = cumulative_equalizer(matrix, create_equalizer_histogram(matrix, equalizer))
    result_image = Image.fromarray(np.uint8(result_matrix))
    return result_image

def resize(image,max_width, max_height):
    try:
        width, height = image.size
        if width > max_width:
            height, width = height * max_width / width, max_width
        if height > max_height:
            width, height = width * max_height / height, max_height
        image = image.resize((int(width), int(height)))
        image.save('static/images/image.png')
    except Exception as e:
        print("Something wrong", e)
        sys.exit(1)
    return image
