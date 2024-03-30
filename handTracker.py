"""
handTracker.py is a python program that uses mediapipe library to track hands and its positions
it also provides a function to track which all fingers are closed and opened

This sample is used for sign language detector program , phantom - virtual board ,color picker etc

Developer : Akhil Krishna
"""

import cv2
import mediapipe as mp


#video capture object
cap=cv2.VideoCapture(0)

#mediapipe hand object created   (solution class has various sub classes like hands, face detections etc )
mp_hands=mp.solutions.hands
hands=mp_hands.Hands()

#mediapipe drawing landmark tool
mp_draw=mp.solutions.drawing_utils



tipids=[8,12,16,20]
def fingerUp(landmarks):
    fingers=[]

    #thumb
    if landmarks[4][1]<landmarks[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    #for rest of the four fingers
    for id in tipids:
        if landmarks[id][2]<landmarks[id-2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers



while cap.isOpened():

    #reading each frame from cap object
    success,img=cap.read()

    #frame flipped
    img=cv2.flip(img,1)

    #RGB converted for more accuracy
    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    results=hands.process(imgRGB)
    landmarks=[]    #future use

    #if any hand detected
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img,hand,mp_hands.HAND_CONNECTIONS)
            for id,lmk in enumerate(hand.landmark):
                h,w,_=img.shape
                x,y=int(lmk.x*w),int(lmk.y*h)
                landmarks.append([id,x,y])

            xi,yi=landmarks[8][1:]  #tip position of index finger
            xm,ym=landmarks[12][1:] #tip position of middle finger

            # print(landmarks)    #if you need to get full landmarks position
            # print("Index finger at ",xi,yi)  # if you need to get only index finger
            # print("Middle finger at ",xm,ym)  #if you need to get middle finger

            fingers=fingerUp(landmarks)
            print(fingers)  #shows which finger is opened and closed (open-1 , closed-0  [thump,index,middle,ring,small]


    if success:
        cv2.imshow("handTracker",img)

    # Esc to quit the app
    if cv2.waitKey(1)==27:
        break


cv2.destroyAllWindows()


