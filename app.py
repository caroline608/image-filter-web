from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import base64
import matplotlib.image as mpimg
import json
import numpy as np
import os

app = Flask(__name__)
socketio = SocketIO(app)

file_name = 'test.png'

def open_send(filename):
    _, file_extension = os.path.splitext(filename)
    img = open(filename, 'rb')
    image_encoded = str(base64.b64encode(img.read()))
    img.close()
    jsonStr = json.dumps({"type": "image/"+ file_extension[1:], "data": image_encoded})
    socketio.emit('image', jsonStr)

def hsv_filter(message, img):
    h = int(message["HSV"]["H"])
    s = int(message["HSV"]["S"])
    v = int(message["HSV"]["V"])
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = np.array([h, s, v])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    res = cv2.bitwise_and(img, img, mask=mask)
    gray = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)
    color_binary = np.zeros_like(gray)
    color_binary[(gray >= 10) & (gray <= 255)] = 1
    return color_binary

def hls_filter(message, img):
    h = int(message["HLS"]["H"])
    l = int(message["HLS"]["L"])
    s = int(message["HLS"]["S"])
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    lower = np.array([h, l, s])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(hls, lower, upper)
    res = cv2.bitwise_and(img, img, mask=mask)
    gray = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)
    color_binary = np.zeros_like(gray)
    color_binary[(gray >= 10) & (gray <= 255)] = 1
    return color_binary

def opencv_filter(message, filename):
    isHLS = bool(message["isHLS"])
    isHSV = bool(message["isHSV"])
    img = mpimg.imread(filename, 'rb')

    combined_binary = np.zeros_like(img[:,:,0])
    if(isHSV):
        temp = hsv_filter(message, img)
        combined_binary[(temp == 1)] = 1
        print("HSV")
    if(isHLS):
        temp = hls_filter(message, img)
        combined_binary[(temp == 1)] = 1
        print("HLS")

    mpimg.imsave("tmp/" + filename, combined_binary, cmap='gray')

@socketio.on('setup')
def setup(message):
    open_send(file_name)

@socketio.on('filter')
def filter(message):
    print(str(message))
    opencv_filter(message, file_name)
    open_send('tmp/' + file_name)

if __name__ == '__main__':
    socketio.run(app)