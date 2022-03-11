import cv2

class trackableObject:
    def __init__(self,loc,id):
        self.status=True
        self.loc=list(map(int,loc))
        self.missing_frame=0
        self.diff=0
        self.tracker=None
        self.id=id

    def updateLoc(self,new_location):
        self.diff=((new_location[0]-self.loc[0])**2+(new_location[1]-self.loc[1])**2)**(0.5)
        self.loc=list(map(int,new_location))
        if self.diff<30:
            self.missing_frame+=1
        else:
            self.missing_frame=0
        if self.loc[0]<0 or self.loc[1]<0 or self.loc[2]<0 or self.loc[3]<0 or self.missing_frame>100:
            self.status=False
            self.tracker=None

    def updateTracker(self,frame):
        if self.status==False:
            return
        ok,rect=self.tracker.update(frame)
        self.status=ok
        self.updateLoc(rect)
        return rect
    
    def startTracking(self,frame):
        if self.status==False:
            return
        self.tracker=cv2.legacy.TrackerMedianFlow_create()
        self.tracker.init(frame,self.loc)