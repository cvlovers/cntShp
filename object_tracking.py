# USAGE
# python3 object_tracking.py --video ./shep.mp4 --yolo ./yolov5-master --weights ./best.pt
import argparse
import os
import random
import shutil
import time

import cv2
import numpy as np
import json

import trackedObject

#split command line arguments and assign them to variables
parser = argparse.ArgumentParser()
parser.add_argument('--video','-v',type=str, required=True, help="path to video with '/'")
parser.add_argument('--yolo','-y',type=str,default='./yolov5-master',help='path to yolo')
parser.add_argument('--weights','-w',type=str,required=True,help='path to pt file')
parser.add_argument('--frame','-f',type=int, default=20)
args = vars(parser.parse_args())

vid_path = args['video']
video_nameLong = vid_path.split('/')[-1]
video_name = video_nameLong.split('.')[0]
yolo_path = args['yolo']
weight_path = args['weights']
jump_frame = args['frame']
originalVid = cv2.VideoCapture(vid_path)
length = int(originalVid.get(cv2.CAP_PROP_FRAME_COUNT))
jumped_len = int(length/jump_frame)


#create temp folders and open source vid
os.mkdir('./objectTrackTemp')
os.mkdir('./objectTrackTemp/imgs')
if originalVid.isOpened():
    print('Video path is true.')
else:
    print('Error, video path might be wrong.')

fid = 1 # Frame counter
# Save the every N frame of the video.
result, frame = originalVid.read() #Read the current frame
h,w = frame.shape[:2]
size = (w,h)
print('Splitting...')
while originalVid.isOpened():
    result, frame = originalVid.read() #Read the current frame
    if result:
        if fid % jump_frame == 0:
            cv2.imwrite(f'./objectTrackTemp/imgs/{video_name}_{fid}.jpg',frame)
    else:
        break
    fid += 1
print(f'Video splitted to the image per {jump_frame} frame.')

# Return the images to a new video.
out = cv2.VideoWriter('./objectTrackTemp/temp.mp4',cv2.VideoWriter_fourcc(*'mp4v'),30,size)
for img_path in sorted(os.listdir('./objectTrackTemp/imgs'),key=lambda x:(len(x),x)): ##I changed this line
    img = cv2.imread(f'./objectTrackTemp/imgs/{img_path}')
    out.write(img)
out.release()
print('Temp video created')

#run yolo
print('Detection started')
yolo = f'python3 {yolo_path}/detect.py --weights {weight_path} --source ./objectTrackTemp/temp.mp4 --save-txt --project ./objectTrackTemp --name yolo_out' #yolo_out/labels contains labels.txt
os.system(yolo)
print('Detection ends.')

#get labels and put them into a list
#top left x y w h
label_files = sorted(os.listdir('./objectTrackTemp/yolo_out/labels'),key=lambda x:(len(x),x))  ##Also this line
label_list = []
j = 0
for i in range(jumped_len):
    txt_list = []
    label_txt = label_files[j]
    number = int(label_txt[5:-4])
    if number != i:
        label_list.append([])
        continue
    if j + 1 < len(label_files):
        j += 1
    txt = open(f'./objectTrackTemp/yolo_out/labels/{label_txt}')
    lines = txt.readlines()
    for line in lines:
        temp = line[2:-1].split(' ')
        lab_w = float(temp[2])*w
        lab_h = float(temp[3])*h
        x_cent = float(temp[0])*w
        y_cent = float(temp[1])*h
        top_x = x_cent - lab_w/2
        top_y = y_cent - lab_h/2
        line_list = [int(top_x),int(top_y),int(lab_w),int(lab_h)]
        txt_list.append(line_list)
    label_list.append(txt_list)

#draw bounding boxes and write ids
def draw_boxes(frame,rects,i):
    for object in rects:
        if object.status==True:
            cv2.rectangle(frame, object.loc, 255, 2)
            cv2.putText(frame,str(object.id),object.loc[:2],cv2.FONT_HERSHEY_SIMPLEX, 1,(209, 80, 0, 255), 3)

def intersection_over_union(new_box, old_box):#to calculate a similarity ratio between boxes
    boxA=(new_box[0],new_box[1],new_box[0]+new_box[2],new_box[1]+new_box[3])
    boxB=(old_box[0],old_box[1],old_box[0]+old_box[2],old_box[1]+old_box[3])
	# determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
	# compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
	# compute the area of both the prediction and ground-truth
	# rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
	# return the intersection over union value
    return iou


def find_Similar_Box(new_found_box,old_boxes):
    #find the most similar old box for new_found_box
    if old_boxes==[]:
        return -1
    similarity_points=np.array([])
    for box in old_boxes:
        s_point=intersection_over_union(new_found_box,box.loc)
        similarity_points=np.append(similarity_points,s_point)
    sim_ind=np.argmax(similarity_points)
    if similarity_points[sim_ind]<0.1:
        return -1
    return sim_ind
    

cap = cv2.VideoCapture(vid_path)

out2= cv2.VideoWriter('./result.mp4',cv2.VideoWriter_fourcc(*'mp4v'),30,size)

i=0
id=0
#loc_history=[]
trackablesList=[]
color_list=[]
loc_dict=dict()

while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if i%jump_frame==0:
        #detection mode
        try:
            bboxes=label_list[int(i/jump_frame)]
        except:
            break

        #delete all trackers
        for object in trackablesList:
            object.tracker=None
        
        #update all locations with boxes from detection
        for j in bboxes:
            close_ind=find_Similar_Box(j,trackablesList)
            if close_ind<0:#create new box
                new_object_found=trackedObject.trackableObject(j,id)
                trackablesList.append(new_object_found)
                #loc_history.append([j[:2]])
                loc_dict[id]=[j[:2]]
                color_list.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
                id+=1
            else:#match with existing object
                trackablesList[close_ind].updateLoc(j)
                #loc_history[close_ind].append(j[:2])
                loc_dict[close_ind].append(j[:2])

        #start tracking again for active boxes
        for object in trackablesList:
            object.startTracking(frame)

    else:
        #tracking mode
        for ind,current_object in enumerate(trackablesList):
            rect=current_object.updateTracker(frame)
            if current_object.status==True:
                #loc_history[ind].append(list(map(int,rect[:2])))
                loc_dict[ind].append(list(map(int,rect[:2])))
            else:
                pass
                #loc_history[ind]=[]
    
    print(len(trackablesList))
    #print frame number to image
    cv2.putText(frame,str(i),(10,10),cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 255, 255), 3)
    
    #if we detected objects, draw their bboxes
    if len(trackablesList)>0:
        draw_boxes(frame,trackablesList,i)

    #draw colorful path
    for key in loc_dict:
        if trackablesList[key].status==True:
            color=color_list[key]
            for box in loc_dict[key]:
                cv2.circle(frame,(box[0],box[1]),4,color,-1)

    i=i+1
    cv2.imshow('window', frame)
    out2.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out2.release()
cv2.destroyAllWindows()
json_obj = json.dumps(loc_dict)
file = open(vid_path.split(".")[0]+".json", 'w',encoding="utf-8")
file.write(json_obj)
shutil.rmtree('./objectTrackTemp',ignore_errors=True)
shutil.rmtree('./objectTrackTemp',ignore_errors=True)
