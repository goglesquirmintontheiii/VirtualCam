#import pyvirtualcam
#import numpy as np

#with pyvirtualcam.Camera(width=1280, height=720, fps=30) as cam:
#    while True:
#        frame = np.zeros((cam.height, cam.width, 4), np.uint8) # RGBA
#        frame[:,:,:3] = cam.frames_sent % 255 # grayscale animation
#        frame[:,:,3] = 255
#        cam.send(frame)
#        cam.sleep_until_next_frame()

# importing cv2
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time
import urllib3
import os
import typing
from datetime import datetime
import random
import string
import cv2
import numpy as np
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import concurrent
from flask import Flask, request, send_file
import threading

cap = cv2.VideoCapture(1)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

config = {"mode": 1, "erosion": True, "toptext": "Big text here", "secondtext": "Small text here", "width": 1280, "height": 720, "removebackground": False,"useipserver": True}

app = Flask(__name__)

@app.route('/')
def home():
    return send_file(os.path.join("html","index.html"))
@app.route('/js/<file>')
def jsfile(file):
    return send_file(os.path.join("js",file))
@app.route('/css/<file>')
def cssfile(file):
    return send_file(os.path.join("css",file))
@app.route('/applysettings', methods=["POST"])
def applysettings():
    global config
    config = request.json
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(config["width"]))
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(config["height"]))
    return "Ok"

def img2img_gen(raw,prompt='',banned='',steps=15,width=512,height=512,seed=1278498239,ip='127.0.0.1',cfg_scale=None,denoising_strength=0.6,mask=None):
    payload = {"init_images": [base64.b64encode(raw).decode('utf-8')], "prompt": prompt, "steps": steps, "width":width,"height":height,"negative_prompt":"lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, (((deformed))), [blurry], bad anatomy, disfigured, poorly drawn face, mutation, mutated, (extra_limb), (ugly), (poorly drawn hands), messy drawing, broken legs,"+banned}
    if seed != -1:
        payload["seed"] = seed
    if cfg_scale is not None:
        payload["cfg_scale"] = cfg_scale
    if denoising_strength is not None:
        payload["denoising_strength"] = denoising_strength
    if mask is not None:
        payload["mask"] = base64.b64encode(mask).decode('utf-8')
    res = requests.post(f'http://{ip}:7860/sdapi/v1/img2img', json=payload)
    r = res.json()
    
    for i in r['images']:
        #image = Image.open(io.BytesIO())
        #png_payload = {
        #"image": "data:image/png;base64," + i
        #}
        #response2 = requests.post(url=f'http://{ip}:7860/sdapi/v1/png-info', json=png_payload)

        #pnginfo = PngImagePlugin.PngInfo()
        #pnginfo.add_text("parameters", response2.json().get("info"))
        ##image.save(os.path.join(cwd,'output.png'), pnginfo=pnginfo)
        return base64.b64decode(i.split(",",1)[0])
    return json.loads(r['info'])

def set_background_to_black(image, avg):
    try:
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
        # Threshold the grayscale image to create a binary mask of the foreground
        _, mask = cv2.threshold(gray, avg, 255, cv2.THRESH_BINARY)
    
        # Create a mask of the background
        mask_inv = cv2.bitwise_not(mask)
    
        # Set the background to black
        background = np.zeros_like(image)
    
        # Set the background pixels to black where mask is zero
        img_with_black_background = cv2.bitwise_and(background, background, mask=mask_inv)
    
        # Combine the original image and the black background
        result = cv2.bitwise_or(img_with_black_background, image, mask=mask)
    
        return result
    except:
        return image

def picture_reset_pixels(img, from_color, to_color, target_color):
    
    mask = np.all((img >= from_color) & (img <= to_color), axis=-1)
    img[mask] = target_color
    
    # Revert back to the original shape before returning
    

    return img

def edge_detection(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detector
    edges = cv2.Canny(gray, threshold1=100, threshold2=200)  # You can adjust the thresholds
    
    # Create a mask using the edges
    mask = np.zeros_like(image)
    mask[edges != 0] = [255, 255, 255]  # Set detected edges to white color
    
    return mask

col = 0;

def process_frame(frame_bytes):
    global col
    
    col += 1
    if (col > 255):
        col = 1
    # Open the frame from bytes and convert to RGB
    image = Image.open(io.BytesIO(frame_bytes))
    image = image.convert("RGB")
    width, height = image.size

    # Convert the image to a NumPy array for efficient processing
    image_array = np.array(image)

    # Calculate the average brightness of the image
    if (config["mode"] in [1,3,6]) or config["removebackground"]:
        average_brightness = np.mean(image_array)

    # RGB to grayscale image
    if config["mode"] in [1,2,6]:
        # Convert the image to grayscale
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Black/White image
    if config["mode"] in [1,3,6]:
        _, image_array = cv2.threshold(image_array, average_brightness, 255, cv2.THRESH_BINARY)
    

    
    # Rainbow chaos
    if config["mode"] == 3:
        image_array = np.stack([image_array] * 3, axis=-1)
        image_array = picture_reset_pixels(image_array, (255,255,255),(255,255,255),tuple(np.random.randint(0, 256, size=3)))
        image_array = picture_reset_pixels(image_array, (0,0,0),(0,0,0),tuple(np.random.randint(0, 256, size=3)))
        image_array = image_array[:, :, 0]

    # Blur
    if config["mode"] == 5:
        # Apply blur to the image
        image_array = cv2.GaussianBlur(image_array, (15, 15), 7)

    # Pixel color inversion
    if config["mode"] in [4,6]:
        # Invert the colors of every pixel
        image_array = 255 - image_array
    
    # Edges
    if config["mode"] in [7,8]:
        image_array = edge_detection(image_array)
        image_array = np.stack([image_array] * 3, axis=-1)
        image_array = picture_reset_pixels(image_array, (255,255,255),(255,255,255),tuple(np.random.randint(0, 256, size=3)))
        #image_array = picture_reset_pixels(image_array, (0,0,0),(0,0,0),tuple(np.random.randint(0, 256, size=3)))
        image_array = image_array[:, :, 0]

    # Background removal
    if config["removebackground"]:
        image_array = set_background_to_black(image_array,average_brightness)

    # Apply erosion to reduce noise
    if config["erosion"]:
        kernel = np.ones((3, 3), np.uint8)
        image_array = cv2.erode(image_array, kernel, iterations=1)

    output = Image.fromarray(image_array.astype(np.uint8))
    
    return output
## Function to process frames as bytes and return processed bytes
#def process_frame(frame_bytes):
#    image = Image.open(io.BytesIO(frame_bytes))
#    # Get the width and height of the image
#    width1, height1 = image.size
#    image = image.convert("RGB")
#    image = image.resize((int(width1/3),int(height1/3)))
#    width, height = image.size
#    # Loop through each pixel and process it
#    for x in range(width):
#        for y in range(height):
#            # Get the RGB values of the current pixel
#            current_pixel = image.getpixel((x, y))

#            # Example: Invert the colors of the image
#            if (current_pixel[0] + current_pixel[1] + current_pixel[2])/3 > 127.5:
#                inverted_pixel = (255,255,255)
#            else:
#                inverted_pixel = (0,0,0)
#            #inverted_pixel = (255 - current_pixel[0], 255 - current_pixel[1], 255 - current_pixel[2])

#            # Set the pixel to the inverted color
#            image.putpixel((x, y), inverted_pixel)
#    return image 

# Open the USB webcam (change the index if you have multiple webcams, usually 0 or 1)

tframes = 0

def fps_reader():
    global tframes
    while True:
        sleep(1)
        print(f"FPS: {tframes}")
        tframes = 0

threading.Thread(target=app.run,args=('0.0.0.0',8080,)).start()
threading.Thread(target=fps_reader).start()

img2 = None
ret, frame = cap.read()

def framethread():
     global tframes
     global img2
     global config
     if ret:
        # Encode the frame as bytes
        _, frame_bytes = cv2.imencode('.png', frame)
        pili = process_frame(frame_bytes.tobytes())
        img2 = cv2.cvtColor(np.array(pili), cv2.COLOR_RGB2BGR)

        
        font = cv2.FONT_HERSHEY_SIMPLEX
  
        # org
        org = (50, 50)
  
        # fontScale
        fontScale = 1
   
        # Blue color in BGR
        color = (0, 0, 255)
  
        # Line thickness of 2 px
        thickness = 2
        if config["useipserver"]:
            # Using cv2.putText() method
            try:
                ipstat = requests.get('http://192.168.11.34:9999/stat').json()

                img2 = cv2.putText(img2, ipstat['ip'],  (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                   1, (0, 0, 255), 2, cv2.LINE_AA)
                img2 = cv2.putText(img2, f'{ipstat["region"]}, {ipstat["country"]}',  (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (0, 0, 255), 2, cv2.LINE_AA)
            except:
                config['useipserver'] = False
                print("FAILED TO CONNECT TO IP SERVER")
        else:
            # Using cv2.putText() method
            img2 = cv2.putText(img2, config["toptext"],  (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 0, 255), 2, cv2.LINE_AA)
            img2 = cv2.putText(img2, config["secondtext"],  (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (0, 0, 255), 2, cv2.LINE_AA)
        # Show the processed frame in an OpenCV window (virtual webcam)

        tframes += 1;
        

while True:
    try:
        ret, frame = cap.read()
        threading.Thread(target=framethread).start()
        try:
            cv2.imshow("Virtual Webcam", img2)
        except:
            pass
        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except:
        print("FRAME GRAB FAIL")
# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()