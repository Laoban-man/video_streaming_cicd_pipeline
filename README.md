# ml-camera

### Contents
What is ml-camera?<br/>
How does this app work?<br/>
Requirements<br/>



### What is ml-camera?

This is a demo flask app where you can take a picture in a mobile browser and send the pic to Google's ML Vision API for label and text extraction.

<br/>

### How does this app work?

At a high level, this app does the following:

1. Asks the user for access to their phone's camera (Front or Back)
2. Once the user grants access, video starts streaming.
3. The user can choose whether they want to detect what an image is or extract text from an image by clicking on the appropriate link.
4. The image is then sent server side along with the image service to be used (text extraction or label). 
5. After sending the image to the Vision API, it returns either a label or text that was extracted from the image and then sends this information back to the client. 

### What does this app look like?

Example of the Google ML Vision API successfully labeling a laptop. In addition to the label, a confidence score is also returned. In the case below, Google is 95% confident that the image is a laptop. <br/><br/>
<img src="https://raw.githubusercontent.com/garethcull/ml-camera/master/static/img/label_image.png" width="400" />
<br/><br/>
Example of the Google ML Vision API extracting text off of a keyboard.<br/><br/>
<img src="https://raw.githubusercontent.com/garethcull/ml-camera/master/static/img/text_extraction.png" width="400" />


### Requirements

This app uses the following python libraries, which you will need to install:

- numpy
- google.cloud.vision
- io
- datetime
- flask
- flask_socketio
- requests

On the client side:

- jquery


### Main files to review how it works

Essentially, main functionality of the app is contained within the following files:

1. app.py - this is the main script
2. vision.py - this is a helper script which sends the image to either the label detection or text extraction service.
3. /static/js/camera.js - this is the main javascript file which sends the data to python and renders results from the Vision API. 


### Useful Reference Links

Here are some links that I found very useful with code examples.

- Flask: http://flask.pocoo.org/
- SocketIO: https://flask-socketio.readthedocs.io/en/latest/
- Google Cloud Vision API: https://cloud.google.com/vision/
- How to build a camera: https://developer.mozilla.org/en-US/docs/Archive/B2G_OS/API/Camera_API/Introduction








