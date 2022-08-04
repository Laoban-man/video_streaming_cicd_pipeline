import threading
from confluent_kafka import Consumer, KafkaError, KafkaException
from consumer_config import config as consumer_config
from utils import *
from pymongo import MongoClient

import cv2
import numpy as np
import time

class ConsumerThread:
    def __init__(self, config, topic, batch_size, db, videos_map):
        self.config = config
        self.topic = topic
        self.batch_size = batch_size
        self.db = db
        self.videos_map = videos_map

    def read_data(self):
        consumer = Consumer(self.config)
        consumer.subscribe(self.topic)
        self.run(consumer, 0, [], [])

    def run(self, consumer, msg_count, msg_array, metadata_array):
        try:
            img_array2=[]
            while True:
                msg = consumer.poll(0.5)
                if msg == None:
                    continue
                elif msg.error() == None:

                    # convert image bytes data to numpy array of dtype uint8
                    nparr = np.frombuffer(msg.value(), np.uint8)

                    # decode image
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    img = cv2.resize(img, (224, 224))
                    msg_array.append(img)
                    img_array2.append(msg.value())

                    # get metadata
                    frame_no = msg.timestamp()[1]
                    video_name = msg.headers()[0][1].decode("utf-8")

                    metadata_array.append((frame_no, video_name))

                    # bulk process
                    msg_count += 1
                    if msg_count % self.batch_size == 0:
                        # predict on batch
                        img_array = np.asarray(msg_array)
                        img_array = preprocess_input(img_array)
                        predictions = self.model.predict(img_array)
                        labels = decode_predictions(predictions)

                        self.videos_map = reset_map(self.videos_map)
                        for metadata,image in zip(metadata_array,img_array2):
                            frame_no, video_name = metadata
                            doc = {
                                "image":image,
                                "frame": frame_no,
                            }
                            self.videos_map[video_name].append(doc)

                        # insert bulk results into mongodb
                        insert_data_unique(self.db, self.videos_map)

                        # commit synchronously
                        consumer.commit(asynchronous=False)
                        # reset the parameters
                        msg_count = 0
                        metadata_array = []
                        msg_array = []
                        img_array2=[]

                elif msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached {0}/{1}'
                        .format(msg.topic(), msg.partition()))
                else:
                    print('Error occured: {0}'.format(msg.error().str()))

        except KeyboardInterrupt:
            print("Detected Keyboard Interrupt. Quitting...")
            pass

        finally:
            consumer.close()

    def start(self, numThreads):
        # Note that number of consumers in a group shouldn't exceed the number of partitions in the topic
        for _ in range(numThreads):
            t = threading.Thread(target=self.read_data)
            t.daemon = True
            t.start()
            while True: time.sleep(10)

if __name__ == "__main__":

    topic = ["video-stream"]

    client=MongoClient("mongodb://localhost:27017")
    db = client['video-stream-records']

    video_names = ["sample_1", "sample_2", "sample_3"]
    videos_map = create_collections_unique(db, video_names)
    
    consumer_thread = ConsumerThread(consumer_config, topic, 32, db, videos_map)
    consumer_thread.start(3)
