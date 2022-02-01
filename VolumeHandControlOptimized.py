import cv2
import time
import numpy as np
import HandTracking as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 0
volPer = 0
area = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) !=0:
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100
        print(area)
        if 200 <area<1500:
            #Find Distance between indexfinger and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            #Convert Volume
            volBar = np.interp(length, [30, 190], [400, 150])
            volPer = np.interp(length, [30, 190], [0, 100])

            # Reduce resolution to make it smoother
            smoothness = 10
            volPer = smoothness * round(volPer/smoothness)

            #Check finger up
            fingers = detector.fingerUp()
            #print(fingers)
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (255, 0, 255), cv2.FILLED)


    cv2.rectangle(img, (50, 150), (85,400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (530, 35), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

    #Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 35), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
    cv2.imshow("Image", img)
    cv2.waitKey(1)