import cv2
import numpy as np


cap = cv2.VideoCapture("./shep.mp4")

result, frame = cap.read()
h,w = frame.shape[:2]
size = (w,h)
out_size=(w,3*(h//4))
out = cv2.VideoWriter('./shep_cropped.mp4',cv2.VideoWriter_fourcc(*'mp4v'),30,out_size)
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        out_frame=frame[:3*(h//4),:]
        out.write(out_frame)
    else:
        print("An error occured")
        break

out.release()
cap.release()
