from flask import Flask,render_template,Response
import cv2
import numpy as np
import mediapipe as mp



app = Flask(__name__)



cap=cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,680)
cap.set(10,150)


def virtual():
    canvas = np.zeros((720, 1280, 3), np.uint8)
    canvas[:, :, :] = 255
    # Black Canvas
    canvasBlack = np.zeros((720, 1280, 3), np.uint8)

    # Mediapipe hand object
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()  # hands=mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5)

    # Mediapipes Drawing tool for connecting hand landmarks
    mp_draw = mp.solutions.drawing_utils

    # header bar image
    overlay = cv2.imread("static/images/BarUp.png")[0:80, 0:1280]

    # SideBar image
    sidebar = cv2.imread("static/images/BarSide.png")[80:720, 1200:1280]

    # tools
    drawColor = (0, 0, 255)

    # for displaying on screen
    selectedColor = 'Blue'
    selectedTool = 'Draw'

    tool = "Draw"  # important for selection

    xp, yp = 0, 0  # previous position of index finger

    # variable for drawing circle
    countCircle = 1

    # variable for drawing rectangle
    countRectangle = 1

    # Function for finding how much fingers are up
    tipIds = [8, 12, 16, 20]  # finger tip ids except for thump tip (4)

    def fingerUp(landmark):
        fingerList = []
        # thump up/down finding is different if thumptip(4) is left to id 3 then up else down ie, x(id4)<x(id3)
        if landmark[4][1] < landmark[3][1]:
            fingerList.append(1)  # 0-id 1-x 2-y in landmark
        else:
            fingerList.append(0)

        # For the rest of fingers if y(id-tip)<y(id-middlepart) then up else down (id-2 bcz middle part of finger)
        for id in tipIds:
            if landmark[id][2] < landmark[id - 2][2]:
                fingerList.append(1)
            else:
                fingerList.append(0)

        return fingerList

    while True:
        
        success,img=cap.read()

        #flipping to make correct aligned(1=horizontally)
        img=cv2.flip(img,1)


        if not success:
            break
        else:

            # 2. Landmark and position finding
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # bcz mediapipe prefer RGB as it is trained in RGB
            results = hands.process(imgRGB)  # Hand Detected

            # IT IS IMPORTANT THAT IT MUST BE PLACED INSIDE LOOP
            landMark = []  # Landmark list for storing position of each finger                   ERROR 1 CAUSED

            # if hand is detected
            if results.multi_hand_landmarks:
                lndmrk = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(img, lndmrk, mp_hands.HAND_CONNECTIONS)  # drawing connection not necessary

                for id, lm in enumerate(lndmrk.landmark):
                    height, width, _ = img.shape
                    # this is done because lm.x gives ratio of x position but we need pixel value so multiply by width , same for height
                    x, y = int(lm.x * width), int(lm.y * height)
                    # appending each landmarks id and position as a list to landMark
                    landMark.append([id, x, y])

                xi, yi = landMark[8][1:]  # index fingers position
                xm, ym = landMark[12][1:]  # middle fingers position
                # print(xm,ym)

                # 3.opened fingers
                fingerList = fingerUp(landMark)

                """We are writing circle and rectangle finish beacuse when we draw circle by using index finger and when middle finger
                up then we must stop the drawing of circle and paste it there for that 
                when middle up the selection mode on --> so we can finsh circle inside selection 
                countCircle will count whether a circle finished drawing or not

                note : only when we draw something on canvasBlack then only permanent so when middle finger up only we are drawing it on canvasBlack

                //Same for rectangle  
                """
                # 4. Selection Mode=================================================================================
                if fingerList[1] and fingerList[2]:

                    # circle finishing
                    if countCircle == 0:
                        cv2.circle(img, (xstart_circle, ystart_circle), int(((xstart_circle - xlast_circle) ** 2 + (
                                    ystart_circle - ylast_circle) ** 2) ** 0.5), drawColor, 10)
                        cv2.circle(canvas, (xstart_circle, ystart_circle), int(((xstart_circle - xlast_circle) ** 2 + (
                                    ystart_circle - ylast_circle) ** 2) ** 0.5), drawColor, 10)
                        cv2.circle(canvasBlack, (xstart_circle, ystart_circle), int(((
                                                                                                 xstart_circle - xlast_circle) ** 2 + (
                                                                                                 ystart_circle - ylast_circle) ** 2) ** 0.5),
                                   drawColor, 10)
                        countCircle = 1

                    # rectangle finishing
                    if countRectangle == 0:
                        cv2.rectangle(img, (xstart_rect, ystart_rect), (xlast_rect, ylast_rect), drawColor, 10)
                        cv2.rectangle(canvas, (xstart_rect, ystart_rect), (xlast_rect, ylast_rect), drawColor, 10)
                        cv2.rectangle(canvasBlack, (xstart_rect, ystart_rect), (xlast_rect, ylast_rect), drawColor, 10)
                        countRectangle = 1

                    # to make discontinuity after selection
                    xp, yp = 0, 0

                    cv2.rectangle(img, (xi - 10, yi - 15), (xm + 10, ym + 20), drawColor, -1)

                    # check if finger on header portion   check later y 125 not 80
                    if yi < 85:
                        # check if fingers are in which x position

                        # Red Color
                        if 342 < xm < 480:
                            drawColor = (0, 0, 255)

                            selectedColor = "Red"

                        # Blue Color
                        elif 576 < xm < 720:
                            drawColor = (255, 100, 0)
                            selectedColor = "Blue"

                        # Green Color
                        elif 810 < xm < 960:
                            drawColor = (0, 255, 0)
                            selectedColor = "Green"


                        # Eraser
                        elif 1020 < xi < 1200:
                            drawColor = (0, 0, 0)
                            selectedColor = "none"
                            selectedTool = 'Eraser'
                            tool = "Eraser"

                    # side tool selection
                    if xm > 1220:
                        if 81 < ym < 167:
                            # print("Clear all")
                            canvasBlack = np.zeros((720, 1280, 3), np.uint8)
                            canvas[:, :, :] = 255
                        elif 192 < ym < 294:
                            # print("Draw tool")
                            tool = "Draw"
                        elif 320 < ym < 408:
                            # print("Circle tool")
                            tool = "Circle"
                        elif 440 < ym < 550:
                            # print("Rectangle")
                            tool = "Rectangle"

                # 5. Drawing Mode==================================================================================
                if fingerList[1] and fingerList[2] == 0:

                    # print("Drawing Mode")

                    cv2.circle(img, (xi, yi), 15, drawColor, -1)

                    if tool == "Eraser":
                        # when frame start dont make a line from 0,0 so draw a line from xi,yi to xi,yi ie a point
                        if xp == 0 and yp == 0:
                            xp, yp = xi, yi

                        # it is to automatically make drawing back to normal size
                        if drawColor == (0, 0, 0):
                            cv2.line(img, (xp, yp), (xi, yi), drawColor, 70)
                            cv2.line(canvas, (xp, yp), (xi, yi), (255, 255, 255), 70)
                            cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 70)
                        else:
                            cv2.line(img, (xp, yp), (xi, yi), drawColor, 10)
                            cv2.line(canvas, (xp, yp), (xi, yi), drawColor, 10)
                            cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 10)
                        # update xp and yp
                        xp, yp = xi, yi

                    # Drawing
                    if tool == "Draw":
                        # when frame start dont make a line from 0,0 so draw a line from xi,yi to xi,yi ie a point
                        if xp == 0 and yp == 0:
                            xp, yp = xi, yi

                        # it is to automatically make eraser back to normal size
                        if drawColor != (0, 0, 0):
                            cv2.line(img, (xp, yp), (xi, yi), drawColor, 10)
                            cv2.line(canvas, (xp, yp), (xi, yi), drawColor, 10)
                            cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 10)
                        else:
                            cv2.line(img, (xp, yp), (xi, yi), drawColor, 70)
                            cv2.line(canvas, (xp, yp), (xi, yi), (255, 255, 255), 70)
                            cv2.line(canvasBlack, (xp, yp), (xi, yi), drawColor, 70)
                        # update xp and yp
                        xp, yp = xi, yi

                    elif tool == "Circle":
                        if countCircle == 1:
                            xstart_circle, ystart_circle = xi, yi
                            countCircle = 0
                        cv2.circle(img, (xstart_circle, ystart_circle),
                                   int(((xstart_circle - xi) ** 2 + (ystart_circle - yi) ** 2) ** 0.5), drawColor, 10)
                        xlast_circle, ylast_circle = xi, yi
                    elif tool == "Rectangle":
                        if countRectangle == 1:
                            xstart_rect, ystart_rect = xi, yi
                            countRectangle = 0
                        cv2.rectangle(img, (xstart_rect, ystart_rect), (xi, yi), drawColor, 10)
                        xlast_rect, ylast_rect = xi, yi

            # 6 . Adding canvas and real fram





            # 6 . Adding canvas and real fram

            imgGray = cv2.cvtColor(canvasBlack, cv2.COLOR_BGR2GRAY)
            _, imgBin = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
            imgBin = cv2.cvtColor(imgBin, cv2.COLOR_GRAY2BGR)
            img = cv2.bitwise_and(img, imgBin)
            img = cv2.bitwise_or(img, canvasBlack)

            img[0:80, 0:1280] = overlay
            img[80:720, 1200:1280] = sidebar
            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/board")
def board():
    return render_template("video.html")


@app.route("/video")
def video():
    return Response(virtual(),mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__== "__main__":
    app.run(debug=True)
