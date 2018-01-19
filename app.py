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

def opencv_filter(message, filename):
    h = int(message["h"])
    s = int(message["s"])
    v = int(message["v"])
    img = mpimg.imread(filename, 'rb')
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = np.array([h, s, v])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    res = cv2.bitwise_and(img, img, mask=mask)
    gray = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)
    color_binary = np.zeros_like(gray)
    color_binary[(gray >= 10) & (gray <= 255)] = 1
    mpimg.imsave("tmp/" + filename, color_binary, cmap='gray')

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