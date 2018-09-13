import sys
import os.path
import math
import numpy as np
from PIL import Image

# fungsi ini digunakan untuk menghasilkan histogram dari suatu gambar
def calculate_image_matrix_histogram(matrix):
    _, _, channel = matrix.shape
    flat_matrix = matrix.flatten()
    histogram = np.zeros((256, channel))
    for i, val in enumerate(flat_matrix):
        histogram[val][i % channel] += 1
    return histogram

# fungsi ini digunakan untuk menormalisasi sebuah histogram gambar dengan cara kulmulatif
def equalize_image_matrix(matrix):
    map_value_to_cumulative = {}

    height, width, channel = matrix.shape
    cumulative_value = np.zeros(channel)
    histogram = calculate_image_matrix_histogram(matrix)
    for value, freq in enumerate(histogram):
        cumulative_value = [cumulative_value[i] + freq[i] for i in range(channel)]
        map_value_to_cumulative[value] = cumulative_value

    total_frequency = width * height
    result = np.zeros(matrix.shape)
    for y in range(height):
        for x in range(width):
            initial_value = matrix[y][x]
            result[y][x] = [math.floor(float(map_value_to_cumulative[v][c]) / float(total_frequency) * 255) for c, v in enumerate(initial_value)]
    
    return result

# fungsi ini digunakan untuk memroses input gambar dan menjalankan fungsi equalize_image_matrix
def normalize(base_image):
    MAX_WIDTH = 600
    MAX_HEIGHT = 400
    try:
        width, height = base_image.size
        print(width, height)
        if width > MAX_WIDTH:
            height, width = height * MAX_WIDTH / width, MAX_WIDTH
        if height > MAX_HEIGHT:
            width, height = width * MAX_HEIGHT / height, MAX_HEIGHT
        base_image = base_image.resize((int(width), int(height)))
    except Exception as e:
        print("Something wrong", e)
        sys.exit(1)

    result_matrix = equalize_image_matrix(np.array(base_image))
    result_image = Image.fromarray(np.uint8(result_matrix))
    return result_image

# fungsi ini digunakan untuk menormalisasi input image dengan cara scaling
def scaling(base_image,w,h):
    histogram = calculate_image_matrix_histogram(np.array(base_image))
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
