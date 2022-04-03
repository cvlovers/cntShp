import os
import pickle
import argparse
from picamera2.encoders.h264_encoder import *
from picamera2.picamera2 import *
import numpy as np
import time
import uploader

#returns string containing date and time
def get_date_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	
parser = argparse.ArgumentParser()
parser.add_argument("--folder_id", help="The Google Drive folder id of target folder", type=str, default='1UOhj83ehUMeUS7fncrrw1qJrPBPIu7Le')
parser.add_argument("--width", help="The width of the recorded video", type=int, default=1280)
parser.add_argument("--height", help="The height of the recorded video", type=int, default=960)
parser.add_argument("--inactivity_timer", help="If there is no motion for this amount of time the recording will stop, in seconds", type=int, default=60)
parser.add_argument("--max_duration", help="The maximum recording length, in seconds", type=int, default=600)
args = parser.parse_args()

#default id for pi_vids: 1UOhj83ehUMeUS7fncrrw1qJrPBPIu7Le
if not args.folder_id:
	sheep_folder_id = '1UOhj83ehUMeUS7fncrrw1qJrPBPIu7Le'
else:
	sheep_folder_id = args.folder_id

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.video_configuration(main={"size": (args.width, args.height), "format": "RGB888"}, 
                                          lores={"size": lsize, "format": "YUV420"})
picam2.configure(video_config)
picam2.start_preview()
encoder = H264Encoder(1000000)
picam2.encoder = encoder
picam2.start()

w, h = lsize
prev = None 
encoding = False
ltime = 0
begin_time = time.time()

local_folder_name = 'data'

while True:
    cur = picam2.capture_buffer("lores")
    cur = cur[:w*h].reshape(h, w)
    if prev is not None:
        mse = np.square(np.subtract(cur, prev)).mean()
        if mse > 5:
            if not encoding:
                #start new recording
                encoder.output = open("temp.h264", 'wb')
                picam2.start_encoder()
                encoding = True
                print("Started recording!", mse)
            ltime = time.time()
        else:
            if encoding and (time.time() - ltime > args.inactivity_timer or time.time() - begin_time > args.max_duration):
                #recording complete
                picam2.stop_encoder()
                print("Stopping recording, encoding video...")
                vid_path = f'{local_folder_name}/video-{get_date_time()}.mp4'
                os.system(f'MP4Box -add temp.h264 {vid_path}')
                os.system('rm -rf temp.h264')
                encoding = False
                #add new video to queue
                uploader.add_file(vid_path, time.time() - begin_time)
                #try to upload all videos
                u = uploader.Uploader()
                u.start()
    prev = cur

		
		


