import time

import cv2
import Mine
import Globla

def detectmine():
    cap = cv2.VideoCapture('untitled.41.avi')
    fps = 0
    type = 1
    while (True):
        ret, frame = cap.read()
        Globla.mutex.acquire()
        t = float(cv2.getTickCount())
        c = Mine.mine()
        c.detect_mine(frame, type, str(fps))
        t = (cv2.getTickCount() - t) / cv2.getTickFrequency()
        fps = (1.0 / t)
        Globla.mutex.release()
        ch = cv2.waitKey(1) & 0xff
        if ch == ord('q'):
            Globla.run = 0
            break
        elif ch == ord('1'):
            type = 0
        elif ch == ord('2'):
            type =1
        elif ch == ord('3'):
            Globla.GET_DIS_ON = not Globla.GET_DIS_ON
