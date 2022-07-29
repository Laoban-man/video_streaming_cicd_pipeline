# Import Modules
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import requests
from datetime import datetime
import logging
import base64  # Used to decode image sent from client
#from vision import label_image,extract_text # Helper File

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

@socketio.on('send_img')
def main(message):
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

    # Determine which Google Vision API Service to use: 1) Label Image OR 2) Extract Text From Image
    
    #if image_analysis == 'label':
        
     #   print("Determining image...")
        # From vision.py helper file
      #  data = label_image(uri)
       # print(data)
    
   # else:
    #    print("Getting ready to " + image_analysis)
        # Access OCR API using the vision.py helper file.
    #    data = extract_text(uri)
     #   print(data)
    
    
    # Send data back to the client in the form of a label detected or text extracted.
    data="failed"
    emit('my_response', {'data': data})
    

if __name__ == '__main__':
    socketio.run(app)
