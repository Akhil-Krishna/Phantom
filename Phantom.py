'''
Phantom- A Virtual Board
Developed by Dr.Akhil Krishna

White board available to send notes

NOTE : FOR DRAWING CIRCLE AND RECTANGLE USE INDEX FINGER AND TO STOP DRAWING USE PINKY FINGER UP 


important areas of code

Line number may change

30  : importing modules
36  : video capture object
43  : Whiteboard
54  : Header image
57  : Mediapipe object creation
65  : tools and gloabal variables
79  : fingerUp function
110 : while loop
117 : Hand tracking module
149 : Selection mode
185 : Drawing mode
211 : Merging Frame with Canvas
233 : Exiting condition


Requirements
    BarUp.png,Mediapipe,numpy,opencv

'''

"""
Tags 

v1.0.0 - Basic tools
v1.1.0 - added white canvas
v1.2.0 - added clearAll and sideBar
v1.3.0 - adding other tools


"""
#importing necessary libraries
import cv2
import mediapipe as mp
import numpy as np


# video capture object created with webcam no 0
cap=cv2.VideoCapture(0)
cap.set(3,1280) #width=1280px
cap.set(4,720)  #height=720px
cap.set(10,150) #brightness=150%


#Canvas
canvas=np.zeros((720,1280,3),np.uint8)
canvas[:,:,:]=255
# Black Canvas
canvasBlack=np.zeros((720,1280,3),np.uint8)





#header bar image
overlay=cv2.imread("images/BarUp.png")[0:80,0:1280]

#SideBar image
sidebar=cv2.imread("images/BarSide.png")[80:720,1200:1280]




#Mediapipe hand object
mp_hands=mp.solutions.hands
hands=mp_hands.Hands()  #hands=mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5)

#Mediapipes Drawing tool for connecting hand landmarks
mp_draw=mp.solutions.drawing_utils


#tools
drawColor=(0,0,255)

# for displaying on screen
selectedColor='Blue'
selectedTool='Draw'

tool="Draw"  #important for selection

xp,yp=0,0           #previous position of index finger



# variable for drawing circle

isDrawindCircle=False
countCircle=0

# variable for drawing rectangle

isDrawindRectangle=False
countRectangle=0

#Function for finding how much fingers are up
tipIds=[8,12,16,20]  # finger tip ids except for thump tip (4)
def fingerUp(landmark):
    fingerList=[]
    #thump up/down finding is different if thumptip(4) is left to id 3 then up else down ie, x(id4)<x(id3)
    if landmark[4][1]<landmark[3][1]:
        fingerList.append(1)                                    # 0-id 1-x 2-y in landmark
    else:
        fingerList.append(0)

    #For the rest of fingers if y(id-tip)<y(id-middlepart) then up else down (id-2 bcz middle part of finger)
    for id in tipIds:
        if landmark[id][2]<landmark[id-2][2]:
            fingerList.append(1)
        else:
            fingerList.append(0)

    return fingerList





#loop
"""
Tasks to perform
1.Import frame with flipping it and overlay it
2.find hand landmarks by using HandLandmark detector
3.find the fingers that are opened using FingerUp method
4.Selection Mode : Index and middle finger
5.Drawing Mode : Only Index finger
6.Add canvas and real frame
"""
while cap.isOpened():
    success,img=cap.read()

    #flipping to make correct aligned(1=horizontally)
    img=cv2.flip(img,1)


    # 2. Landmark and position finding
    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)  # bcz mediapipe prefer RGB as it is trained in RGB
    results=hands.process(imgRGB)               # Hand Detected

    #IT IS IMPORTANT THAT IT MUST BE PLACED INSIDE LOOP
    landMark = []   #Landmark list for storing position of each finger                   ERROR 1 CAUSED


    #if hand is detected
    if results.multi_hand_landmarks:
        lndmrk = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(img, lndmrk, mp_hands.HAND_CONNECTIONS)  # drawing connection not necessary

        for id, lm in enumerate(lndmrk.landmark):
            height, width, _ = img.shape
            # this is done because lm.x gives ratio of x position but we need pixel value so multiply by width , same for height
            x, y = int(lm.x * width), int(lm.y * height)
            # appending each landmarks id and position as a list to landMark
            landMark.append([id, x, y])



        xi,yi=landMark[8][1:]       #index fingers position
        xm,ym=landMark[12][1:]      #middle fingers position
       # print(xm,ym)

        #3.opened fingers
        fingerList=fingerUp(landMark)




        # 4. Selection Mode=================================================================================
        if fingerList[1] and fingerList[2]:


            #to make discontinuity after selection
            xp,yp=0,0

            cv2.rectangle(img,(xi-10,yi-15),(xm+10,ym+20),drawColor,-1)

            #check if finger on header portion   check later y 125 not 80
            if yi < 85:
                # check if fingers are in which x position

                #Red Color
                if 342 < xm < 480:
                    drawColor = (0, 0, 255)

                    selectedColor = "Red"

                #Blue Color
                elif 576 < xm < 720:
                    drawColor = (255, 100, 0)
                    selectedColor = "Blue"

                #Green Color
                elif 810 < xm < 960:
                    drawColor = (0, 255, 0)
                    selectedColor = "Green"


                #Eraser
                elif 1020 < xi < 1200:
                    drawColor = (0, 0, 0)
                    selectedColor = "none"
                    selectedTool='Eraser'
                    tool="Eraser"
            
            #side tool selection
            if xm>1220:
                if 81<ym<167:
                    #print("Clear all")
                    canvasBlack = np.zeros((720, 1280, 3), np.uint8)
                    canvas[:, :, :] = 255
                elif 192<ym<294:
                    #print("Draw tool")
                    tool="Draw"
                elif 320<ym<408:
                    #print("Circle tool")
                    tool="Circle"
                elif 440<ym<550:
                    #print("Rectangle")
                    tool="Rectangle"






        #5. Drawing Mode==================================================================================
        if fingerList[1] and fingerList[2]==0:

            #print("Drawing Mode")

            cv2.circle(img,(xi,yi),15,drawColor,-1)

            if tool=="Eraser":
                #when frame start dont make a line from 0,0 so draw a line from xi,yi to xi,yi ie a point
                if xp==0 and yp==0:
                    xp,yp=xi,yi

                #it is to automatically make drawing back to normal size
                if drawColor==(0,0,0):
                    cv2.line(img, (xp, yp), (xi, yi), drawColor, 70)
                    cv2.line(canvas, (xp, yp), (xi, yi), (255,255,255), 70)
                    cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 70)
                else:
                    cv2.line(img, (xp, yp), (xi, yi), drawColor, 10)
                    cv2.line(canvas, (xp, yp), (xi, yi), drawColor, 10)
                    cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 10)
                #update xp and yp
                xp,yp=xi,yi


            #Drawing
            if tool=="Draw":
                #when frame start dont make a line from 0,0 so draw a line from xi,yi to xi,yi ie a point
                if xp==0 and yp==0:
                    xp,yp=xi,yi

                # it is to automatically make eraser back to normal size
                if drawColor!=(0,0,0):
                    cv2.line(img,(xp,yp),(xi,yi),drawColor,10)
                    cv2.line(canvas,(xp,yp),(xi,yi),drawColor,10)
                    cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 10)
                else:
                    cv2.line(img, (xp, yp), (xi, yi), drawColor, 70)
                    cv2.line(canvas, (xp, yp), (xi, yi), (255,255,255), 70)
                    cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 70)
                #update xp and yp
                xp,yp=xi,yi

            elif tool=="Circle":
                if isDrawindCircle==False and fingerList[4]!=1:
                    countCircle=1
                    xstart,ystart=xi,yi
                if fingerList[4]==0:
                    cv2.circle(img, (xstart, ystart), int(((xstart - xi) ** 2 + (ystart - yi) ** 2) ** 0.5), drawColor, 10)
                    xlast,ylast=xi,yi
                    isDrawindCircle=True
                if fingerList[4]==1 and countCircle==1:
                    isDrawindCircle=False
                    countCircle=0
                    cv2.circle(canvasBlack, (xstart, ystart), int(((xstart - xlast) ** 2 + (ystart - ylast) ** 2) ** 0.5), drawColor, 10)
                    cv2.circle(canvas, (xstart, ystart), int(((xstart - xlast) ** 2 + (ystart - ylast) ** 2) ** 0.5),drawColor, 10)
            elif tool=="Rectangle":
                if isDrawindRectangle==False and fingerList[4]!=1:
                    countRectangle=1
                    xstart_rect,ystart_rect=xi,yi
                if fingerList[4]==0:
                    cv2.rectangle(img, (xstart_rect, ystart_rect), (xi,yi), drawColor, 10)
                    xlast_rect,ylast_rect=xi,yi
                    isDrawindRectangle=True
                if fingerList[4]==1 and countRectangle==1:
                    isDrawindRectangle=False
                    countRectangle=0
                    cv2.rectangle(canvasBlack, (xstart_rect, ystart_rect),(xlast_rect,ylast_rect), drawColor, 10)
                    cv2.rectangle(canvas, (xstart_rect, ystart_rect),(xlast_rect,ylast_rect),drawColor, 10)






    #6 . Adding canvas and real fram


    imgGray=cv2.cvtColor(canvasBlack,cv2.COLOR_BGR2GRAY)
    _,imgBin=cv2.threshold(imgGray,50,255,cv2.THRESH_BINARY_INV)
    imgBin=cv2.cvtColor(imgBin,cv2.COLOR_GRAY2BGR)
    img=cv2.bitwise_and(img,imgBin)
    img=cv2.bitwise_or(img,canvasBlack)


    #or
    #img = cv2.addWeighted(img, 0.5, canvas, 0.5, 0)


    #trying to overlay header , sidebar to webcam
    img[0:80,0:1280]=overlay
    img[80:720,1200:1280]=sidebar




    #showing frame
    cv2.imshow("Phantom- White Board",canvas)
    cv2.imshow("Phantom - A Virtual Board",img)

    #exit condition by using esc
    if cv2.waitKey(1)==27:
        break

