import torch
import numpy as np
import cv2
from IPython.display import Image  # for displaying images
from roboflow import Roboflow
from time import time
import pafy

class PowerflexDetect:

    def __init__(self, capture_index, model_name, url, out_file):

        self._URL = url
        self.capture_index = capture_index
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.out_file = out_file
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    

    def get_video_capture(self):
        return cv2.VideoCapture(self.capture_index)

    def get_video_from_url(self):
        play = pafy.new(self._URL).streams[-1]
        assert play is not None
        return cv2.VideoCapture(play.url)


    def load_model(self, model_name):
        
        if model_name:
            model = torch.hub.load(r'C:\Users\B0WK73\Documents\Repo\Control-Panel-Detector', 'custom', path=model_name, source='local', force_reload=True)
        else:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model


    def score_frame(self, frame):
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    
    def class_to_label(self, x):
        return self.classes[int(x)]

    
    def plot_boxes(self, results, frame):
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        return frame

    
    def __call__(self):

        player = self.get_video_from_url()
        assert player.isOpened()
        x_shape = int(player.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_shape = int(player.get(cv2.CAP_PROP_FRAME_HEIGHT))
        four_cc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(self.out_file, four_cc, 20, (x_shape, y_shape))
        frame_num = 0

        while True:
            start_time = time()
            ret, frame = player.read()
            if not ret:
                break
            print(frame_num)
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)
            end_time = time()
            fps = 1/np.round(end_time - start_time, 2)
            out.write(frame)
            frame_num += 1





        # cap = self.get_video_capture()
        # assert cap.isOpened()

        # while True:

        #     ret, frame = cap.read()
        #     assert ret

        #     frame = cv2.resize(frame, (416,416))

        #     start_time = time()
        #     results = self.score_frame(frame)
        #     frame = self.plot_boxes(results, frame)

        #     end_time = time()
        #     fps = 1/np.round(end_time - start_time, 2)

        #     cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)

        #     cv2.imshow('YOLOv5 Detection', frame)

        #     if cv2.waitKey(5) & 0xFF == 27:
        #         break

        # cap.release()

detector = PowerflexDetect(capture_index=0, model_name='runs/train/exp/weights/best.pt', url="https://www.youtube.com/watch?v=3XR8CugJ7J8", out_file="video1.avi")
detector()