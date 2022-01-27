import cv2
import Mine
import Globla


def Detect():
    cap = cv2.VideoCapture(0)
    fps = 0
    while (True):
        ret, frame = cap.read()
        t = float(cv2.getTickCount())
        c = Mine.mine()
        c.detect_mine(frame, 0, str(fps))
        t = (cv2.getTickCount() - t) / cv2.getTickFrequency()
        fps = (1.0 / t)
        if cv2.waitKey(10) & 0xff == ord('q'):
            Globla.run = 0
            break