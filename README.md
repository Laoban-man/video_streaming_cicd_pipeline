# Video-streaming pipeline

### Contents
Objectives
Process
Reference


### Objectives
Create a video streaming pipeline providing a web interface to submit data, convert it and stream it via a Kafka cluster to a back-end hosting a MongoDB database, a MLserver deploying an Scikit Learn model, and the Kafka cluster.

A subsequent project will focus on developping the CICD aspects of the pipeline.

### Process

1. A video is recorded in a .webm format directly on a browser through a javascript program.
2. The video is sent to the web server back-end through the Flask API in a binary format
3. The video is converted into a .mp4 format for simpler manipulation and stored locally
4. A kafka stream is sent containing a subset of the images via a Kafka producer
5. The Kafka stream is received by a cluster and processed by Kafka consumer which stores the data into a local MongoDB
6. A simple ML model is trained on the data
7. Outside of training, a clip is directly transformed by the front-end and sent to a server which responds with a classification result, shown on the web browser.

### Reference

A more comprehensive description of the project is available on the Medium article: https://medium.com/@nicolasmichaelroux/video-streaming-ml-pipeline-88099a7b9629

