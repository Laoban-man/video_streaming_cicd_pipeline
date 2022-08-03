# Import Modules
import os
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import requests
from datetime import datetime
import logging
import base64  # Usedto decode image sent from client
import cv2
from collections import Counter
import time
#from vision import label_image,extract_text # Helper File

# function query mlflow model directly
def queryModel(video_path):
    print(video_path)
    img_class = []
    video = cv2.VideoCapture(video_path)
    video_name = os.path.basename(video_path).split(".")[0]
    frame_no = 1
    while video.isOpened():
        _, frame = video.read()
        try:
            frame = cv2.resize(frame, (224, 224))
            # pushing every 3rd frame
            if frame_no % 3 == 0:
                payload = {
                    "inputs": [
                         {
                        "name": "metadata-np",
                        "datatype": "INT32",
                        "shape": [224,224,3],
                        "data": frame.flatten().tolist(),
                        }
                        ]
                }
                response = requests.post(
                    "http://35.238.232.235:8080/v2/models/content-type-example/infer",
                    json=payload
                )
                # Append results to empty list
                img_class.append(json.loads(response.text)["outputs"][0]["data"][0])
        except:
            print("End of file")
            break

        time.sleep(0.1)
        frame_no += 1
    # Get most frequent classiciation    
    occurence_count = Counter(img_class)
    result=occurence_count.most_common(1)[0][0]

    # Close connecction to video 
    video.release()
    return result


# Socket IO Flask App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Flask App

@app.route('/')
def index():
    return render_template('camera.html')

@socketio.on('connection_msg')
def connected(message):
    print("Connected")
    data = message

@socketio.on('train_img')
def main1(message):
    # message contains the image from the client side and the type of ml service to use: 
    # label detection or text extraction
    #data = np.array(list(message.values()))
    
    # The type of ml service to use - stored in image_analysis.
    #image_analysis = data[0][0]
    
    # The image to encode - from the client side
    #img_to_encode = data[0][1]
    #print(img_to_encode)
        
    # Then split the list, and encode everything after the ',' and store in img_encoded
    #img_encoded = img_to_encode.split(',')[1].encode()
    print(len(message["data"][0]))
    data=message["data"][0]
    
    # Get Current Timestamp in ms - append timestamp to image name so we always save a new image
    timestamp = datetime.now()
    time_formatted = timestamp.strftime("%Y%m%d%H%M%S")
    file_name = "pic_" + time_formatted + ".webm"
    
    # folder to store the image
    folder = '/home/nicolasmichaelroux/videos/'
    uri = folder + file_name
    
    # Need to decode it using base64
    with open(uri, "wb") as fh:
        fh.write(data)
    os.system("webm -i "+uri+" "+folder+"pic_"+time_formatted+".mp4")
    os.system("rm "+uri)    
    # Send data back to the client in the form of a label detected or text extracted

@socketio.on('classify_img')
def main2(message):
    print(len(message["data"][0]))
    data=message["data"][0]

    # Get Current Timestamp in ms - append timestamp to image name so we always save a new image
    timestamp = datetime.now()
    time_formatted = timestamp.strftime("%Y%m%d%H%M%S")
    file_name = "pic_" + time_formatted + ".webm"

    # folder to store the image
    folder = '/home/nicolasmichaelroux/videos/'
    uri = folder + file_name

    # Need to decode it using base64
    with open(uri, "wb") as fh:
        fh.write(data)
    os.system("webm -i "+uri+" "+folder+"pic_"+time_formatted+".mp4")
    os.system("rm "+uri)
    
    print("starting query")
    result=queryModel(folder + "pic_" + time_formatted+".mp4")
    # Send data back to the client in the form of a label detected or text extracted
    emit('my_response', {'data': result})


if __name__ == '__main__':
    socketio.run(app)

