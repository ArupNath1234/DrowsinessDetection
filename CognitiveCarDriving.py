
import cv2
import numpy as np
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
def ratioCal( left,right,up,down):
    horizontal_distance,_=detector.findDistance(left,right)
    vertical_distance,_=detector.findDistance(up,down)  
    ratio=int((horizontal_distance/vertical_distance)*10)
    return ratio 

cap=cv2.VideoCapture(0)
detector=FaceMeshDetector(maxFaces=1)
plotY=LivePlot(w=300,h=200,yLimit=[50,85],invert=True)

def createDashBoard():
    dashborad = np.zeros([120,640,3],dtype=np.uint8)
    dashborad.fill(0)
    
    cv2.putText(dashborad,'Instruction: ',[0,50],cv2.FONT_HERSHEY_DUPLEX,.7,[255,255,0],2)
    cv2.putText(dashborad,'Press P to start,W to Accelerate,Press S to Break,Press Q to Close ',[0,70],cv2.FONT_HERSHEY_PLAIN,1,[255,255,0],2)
    return dashborad

def createinstructionboard():
    instructionboard = np.zeros([400,300,3],dtype=np.uint8)
    instructionboard.fill(0)
    cv2.putText(instructionboard,'DashBorad:',[0,200],cv2.FONT_HERSHEY_DUPLEX,1,[255,255,0],2)
    cv2.putText(instructionboard,'Driver Status:',[0,230],cv2.FONT_HERSHEY_PLAIN,1.2,[255,255,0],2)
    cv2.putText(instructionboard,'Engine Status:',[0,250],cv2.FONT_HERSHEY_PLAIN,1.2,[255,255,0],2)
    cv2.putText(instructionboard,'Speed:',[0,270],cv2.FONT_HERSHEY_PLAIN,1.2,[255,255,0],2)
    return instructionboard



def currentStatus(face,ratioAvg,driver):
    engineStatus="Off"
    if(face==True and driver==True):
        engineStatus="Started"
        if ratioAvg>65.0 :
            status="Closed"
        elif ratioAvg > 59.0 :
            status="Sleepy"
        elif ratioAvg > 0.0 : 
            status="Active"
        else:
            status="No"
    elif(face==True and driver==False):
        status="Press P to Start"
    else:
        status="No Driver"

    return status,engineStatus



leftidList=[22,23,24,25,26,110,157,158,159,160,161,130,243]
rightidList=[463,256,252,253,254,339,341,384,385,386,387,388,359]
ratioList=[]
status="No Driver Found"
dashboard=createDashBoard()
instructionboard=createinstructionboard()
leftratio=0
rightratio=0
driver=False
while True:
    success,img=cap.read()
    img,faces=detector.findFaceMesh(img) 
    #img=cv2.flip(img,1)
    if faces:
        face=faces[0]
        for lid in leftidList:
            cv2.circle(img,face[lid],2,(255,0,255),cv2.FILLED)
        for rid in rightidList:
            cv2.circle(img,face[rid],2,(255,0,255),cv2.FILLED)
        #right eye
        rightUp=face[386]
        rightDown=face[253]
        rightLeft=face[463]
        rightRight=face[359]
        cv2.line(img,rightUp,rightDown,(0,255,0),2)
        cv2.line(img,rightLeft,rightRight,(0,255,0),2)
        rightratio=ratioCal( rightLeft,rightRight,rightUp,rightDown)

        
        #left eye points
        leftUp=face[159]
        leftDown=face[23]
        leftLeft=face[130]
        leftRight=face[243]

        '''horizontal_distance,_=detector.findDistance(leftLeft,leftRight)
        vertical_distance,_=detector.findDistance(leftUp,leftDown)'''
        #left eye
        cv2.line(img,leftUp,leftDown,(0,255,0),2)
        cv2.line(img,leftLeft,leftRight,(0,255,0),2)
        leftratio=ratioCal( leftLeft,leftRight,leftUp,leftDown)

        #int((horizontal_distance/vertical_distance)*10)
        ratioList.append(leftratio+rightratio)
        if len(ratioList)>30:
            ratioList.pop(0)
        ratioAvg=sum(ratioList)/len(ratioList)
        imgPlot=plotY.update(ratioAvg)
        driverStatus,engineStatus=currentStatus(True,ratioAvg,driver)
        if(cv2.waitKey(1) & 0xFF == ord('p')):
            driver=True

    else:
        ratioAvg=0
        imgPlot=plotY.update(ratioAvg)
        driverStatus,engineStatus=currentStatus(False,ratioAvg,driver)
        driver=False

    '''if(ratioAvg>65.0):
        print(str(leftratio+rightratio) +" closed")
        status="Eyes are Closed"
    elif ratioAvg > 59.0 :
        print(str(leftratio+rightratio) +" sleepy")
        status="Eyes are Sleepy"
    else:
        status="Active"
        print(str(leftratio+rightratio)+" ok")'''

    #img=cv2.resize(img,(640,360))
    
    imgstack1=cvzone.stackImages([img,dashboard],1,1)
    imgstack2=cvzone.stackImages([instructionboard,imgPlot],1,1)
    lstImg=cvzone.stackImages([imgstack2,imgstack1],2,1)
    cvzone.putTextRect(lstImg,f'Warning!! {driverStatus}',(0,300),1,2,(0,0,255),colorR=(0,0,0))
    cvzone.putTextRect(lstImg,f'{driverStatus}',(150,230),1,1,(255,255,255),colorR=(0,0,0))
    cvzone.putTextRect(lstImg,f'{engineStatus}',(170,250),1,1,(255,255,255),colorR=(0,0,0))
    #cv2.imshow("Live Ratio",imgPlot)
    #cv2.imshow("Video",img)
    cv2.imshow("imgstack",lstImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()