import cv2
import numpy as np
import mediapipe as mp
import json
import sys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image 
import requests
import time
url = "https://hozencollection.com/cdn/shop/articles/muilti1_180x.jpg"

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 5
FONT_THICKNESS = 5
TEXT_COLOR = (255, 0, 0)  # red

def getLocation(image, top_left, bottom_right):
    topBottom_boundary = image.shape[0]//2
    leftMid_boundary = int(image.shape[1]*0.25)
    midRight_boundary = image.shape[1]-leftMid_boundary
    inTopLeft = top_left[0] < leftMid_boundary and top_left[1] < topBottom_boundary
    inBottomRight = bottom_right[0] > midRight_boundary and bottom_right[1] > topBottom_boundary
    full = ""
    LoR = "" 
    ToB= "" 
    middle=""
    if inTopLeft and inBottomRight:
        return "CLOSE"
    elif inTopLeft and (bottom_right[0] <= midRight_boundary):
        LoR =  "LEFT"
    elif inBottomRight and (top_left[0] >= leftMid_boundary):
        LoR =  "RIGHT"
    if (top_left[1] < topBottom_boundary) and (bottom_right[1] <= topBottom_boundary):
        ToB =  "TOP"
    elif (top_left[1] >= topBottom_boundary) and (bottom_right[1] > topBottom_boundary):
        ToB = "BOTTOM"
    
    if LoR=="":
        middle = "MIDDLE"
    return ToB+" "+middle+LoR
    
def visualize(image, detection_result) -> np.ndarray:
    detections = []
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        top_left = bbox.origin_x, bbox.origin_y
        bottom_right = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        space_location = getLocation(image, top_left, bottom_right)
        
        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        result_text = category_name + ' ' + space_location
        detections.append(result_text)
        '''
        print(result_text)
        text_location = (MARGIN + bbox.origin_x,
                         MARGIN + ROW_SIZE + bbox.origin_y)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)'''
        
        response = {
            "num" : len(detection_result.detections),
            "objects": detections
        }

    return response

time.sleep(3)
# STEP 2: Create an ObjectDetector object.
base_options = python.BaseOptions(model_asset_path='efficientdet.tflite')
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

# STEP 3: Load the input image.
image = mp.Image.create_from_file("public/snapshot.jpeg")

# STEP 4: Detect objects in the input image.
detection_result = detector.detect(image)

# STEP 5: Process the detection result. In this case, visualize it.
image_copy = np.copy(image.numpy_view())
response = visualize(image_copy, detection_result)
print(json.dumps(response["objects"]))
sys.stdout.flush()