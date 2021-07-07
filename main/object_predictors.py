import cv2
import imutils
from imutils.video import FPS
import numpy as np
from scipy.spatial import distance as dist
import string
import random
import os
import time

class Predictors:
    def get_mask_detector(self,frame,user_name):
        # cv2.cuda.setDevice(1)
        with open("main/yolo-files/mask_config_files/obj.names","r",encoding = "utf-8" ) as f:
            labels = f.read().strip().split("\n")
        
        yolo_config_path = "main/yolo-files/mask_config_files/custom-yolov4-tiny-detector.cfg"
        yolo_weights_path = "main/yolo-files/mask_config_files/custom-yolov4-tiny-detector_best.weights"

        confidence_threshold = 0.3

        overlapping_threshold = 0.5
        net = cv2.dnn.readNetFromDarknet(yolo_config_path,yolo_weights_path)
        # cv2.getBuildInformation()
        np.random.seed(123)
        colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        W = None
        H = None

        if W is None or H is None:
            (H, W) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        
        net.setInput(blob)
        layerOutputs = net.forward(ln)
        boxes = []
        confidences = []
        classIDs = []
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > confidence_threshold:
                    # Scale the bboxes back to the original image size
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Remove overlapping bounding boxes and boundig boxes
        bboxes = cv2.dnn.NMSBoxes(
            boxes, confidences, confidence_threshold, overlapping_threshold)
        if len(bboxes) > 0:
            for i in bboxes.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                if classIDs[i]  ==  1:
                    color = (0,128,0)
                else:
                    color = (0, 0, 255)
                    
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = "{}".format(labels[classIDs[i]])
                cv2.putText(frame, text, (x, y - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
                letters = string.ascii_lowercase
                image_name = ''.join(random.choice(letters) for i in range(10))
                if classIDs[i]  ==  0:
                    if not os.path.isdir(f"./static/detection/{user_name}"):
                        os.mkdir(f"./static/detection/{user_name}")
                    image_url = f"./static/detection/{user_name}/" + image_name + ".jpg"
                    cv2.imwrite(image_url,frame)


        return frame

    def detect_people(self,frame, net, ln, personIdx=0):
        (H, W) = frame.shape[:2]
        results = []

        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(ln)

       
        boxes = []
        centroids = []
        confidences = []

        for output in layerOutputs:
            for detection in output:

                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                if classID == personIdx and confidence > 0.3:
                   
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    boxes.append([x, y, int(width), int(height)])
                    centroids.append((centerX, centerY))
                    confidences.append(float(confidence))

        
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.3)

        
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                r = (confidences[i], (x, y, x + w, y + h), centroids[i])
                results.append(r)
        return results

    def get_pedistran_detector(self,frame,user_name):
        with open("main/yolo-files/pedistration_config_files/coco.names","r",encoding = "utf-8" ) as f:
            labels = f.read().strip().split("\n")
        
        yolo_config_path = "main/yolo-files/pedistration_config_files/yolov4-tiny.cfg"
        yolo_weights_path = "main/yolo-files/pedistration_config_files/yolov4-tiny.weights"

        confidence_threshold = 0.3

        overlapping_threshold = 0.3
        
        net = cv2.dnn.readNetFromDarknet(yolo_config_path,yolo_weights_path)
        
        np.random.seed(123)
        colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        
        frame = imutils.resize(frame, width=700)
        results = self.detect_people(frame, net, ln,
        personIdx=labels.index("person"))
        violate = set()
        if len(results) >= 2:
            centroids = np.array([r[2] for r in results])
            D = dist.cdist(centroids, centroids, metric="euclidean")
            for i in range(0, D.shape[0]):
                for j in range(i + 1, D.shape[1]):
                    if D[i, j] < 50:
                        violate.add(i)
                        violate.add(j)
        for (i, (prob, bbox, centroid)) in enumerate(results):
            (startX, startY, endX, endY) = bbox
            (cX, cY) = centroid
            color = (0, 255, 0)
            if i in violate:
                color = (0, 0, 255)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.circle(frame, (cX, cY), 5, color, 1)
        text = "Social Distancing Violations: {}".format(len(violate))
        cv2.putText(frame, text, (7, frame.shape[0] - 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 2)
      
        if len(violate)> 1:
            letters = string.ascii_lowercase
            image_name = ''.join(random.choice(letters) for i in range(10))
            if not os.path.isdir(f"./static/detection/{user_name}"):
                os.mkdir(f"./static/detection/{user_name}")
            image_url = f"./static/detection/{user_name}/" + image_name + ".jpg"
            cv2.imwrite(image_url,frame)
        return frame

