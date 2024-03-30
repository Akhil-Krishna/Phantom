"""
handTracker.py is a python program that uses mediapipe library to track hands and its positions
it also provides a function to track which all fingers are closed and opened

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

    if success:
        cv2.imshow("handTracker",img)

    # Esc to quit the app
    if cv2.waitKey(1)==27:
        break


cv2.destroyAllWindows()


