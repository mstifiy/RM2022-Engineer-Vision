import cv2
import copy
import Mine
import Globla
import numpy as np

def pretreatment(src, type):
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    if type == 0:
        lower = np.array([0, 0, 221])
        upper = np.array([128, 30, 255])
        mask = cv2.inRange(hsv, lower, upper)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pret = []
        for i in contours:
            contour_area = cv2.contourArea(i)
            if contour_area > 1000 and contour_area < 100000:
                stone_rect = cv2.boundingRect(i)
                dst = copy.deepcopy(cv2.bitwise_and(src, src, mask=mask))
                dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
                ret, binary = cv2.threshold(dst, 40, 255, cv2.THRESH_BINARY)
                x, y, w, h = stone_rect
                if w / h < 1.65 and w / h > 0.55:
                    ROI_mask = binary[y:y + h, x:x + w]
                    pret.append((ROI_mask, stone_rect, i))
        return pret

    elif type == 1:
        lower = np.array([26, 43, 46])
        upper = np.array([34, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pret = []
        for i in contours:
            contour_area = cv2.contourArea(i)
            if contour_area > 1000:
                stone_rect = cv2.boundingRect(i)
                dst = copy.deepcopy(cv2.bitwise_and(src, src, mask=mask))
                dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
                ret, binary = cv2.threshold(dst, 40, 255, cv2.THRESH_BINARY)
                x, y, w, h = stone_rect
                if w / h < 1.7 and w / h > 0.55:
                    ROI_mask = binary[y:y + h, x:x + w]
                    pret.append((ROI_mask, stone_rect, i))
        return pret


def detectmine():
    cap = cv2.VideoCapture('untitled.41.avi')
    type = 1
    choice = 0
    while (True):
        ret, frame = cap.read()
        Globla.mutex.acquire()
        t = float(cv2.getTickCount())
        c = pretreatment(frame, type)
        mineset = 0
        for i in c:
            d = Mine.mine()
            mineset += 1
            if mineset == choice:
                d.detect_mine(frame, i[0], i[1], i[2], 1)
            d.detect_mine(frame, i[0], i[1], i[2], 0)
        t = (cv2.getTickCount() - t) / cv2.getTickFrequency()
        fps = (1.0 / t)
        fps = np.int0(fps)
        cv2.putText(frame, str(fps), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow("src", frame)
        Globla.mutex.release()
        ch = cv2.waitKey(1) & 0xff
        if ch == ord('0') or ch == ord('1') or ch == ord('2') or ch == ord('3') or ch == ord('4') or ch == ord('5'):
            choice = int(ch) - 48
        elif ch == 27:
            Globla.run = 0
            break
        elif type == 1 and ch == ord('q'):
            type = 0
            print("finding white now")
        elif type == 0 and ch == ord('e'):
            type = 1
            print("finding yellow now")

