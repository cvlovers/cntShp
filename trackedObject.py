import cv2

class trackableObject:
    def __init__(self,loc,id,classid):
        self.status=True
        self.loc=list(map(int,loc))
        self.missing_frame=0
        self.diff=0
        self.tracker=None
        self.id=id
        self.classid=classid
        self.counted=False

    def updateLoc(self,new_location,w,h,line_slope, line_coef):
        if self.status==False:
            return False
        self.diff=((new_location[0]-self.loc[0])**2+(new_location[1]-self.loc[1])**2)**(0.5)
        self.loc=list(map(int,new_location))
        diff_threshold=0.01*((w*h)**0.5)
        center=(self.loc[0]+self.loc[2]//2,self.loc[1]+self.loc[3]//2) 
        
        if self.diff<diff_threshold:
            self.missing_frame+=1
        else:
            self.missing_frame=0

        if center[1]>=line_slope*center[0]+line_coef or center[1]>h:
            self.tracker=None
            self.status=False
            self.counted=True
            return self.counted

        if self.loc[0]<0 or self.loc[1]<0 or self.loc[2]<0 or self.loc[3]<0:
            self.status=False
            self.tracker=None
        
        return self.counted

    def updateTracker(self,frame,w,h,line_slope, line_coef):
        if self.status==False:
            return
        ok,rect=self.tracker.update(frame)
        self.status=ok
        is_counted=self.updateLoc(rect,w,h,line_slope,line_coef)
        return rect,is_counted
    
    def startTracking(self,frame):
        if self.status==False:
            return
        self.tracker=cv2.legacy.TrackerMedianFlow_create()
        self.tracker.init(frame,self.loc)