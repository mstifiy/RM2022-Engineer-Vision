import copy

import cv2
import numpy as np
from enum import Enum


class MINETYPE(Enum):
    WHITE = 0
    YELLOW = 1


class mine():
    position = [0, 0, 0, 0, 0, 0]      #x,y,z,pith,roll,yaw
    sign = [0, 0, 0, 0]
    lower = np.array([0, 0, 0])
    upper = np.array([180, 255, 255])
    def detect_mine(self, src, type,fps):
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        ROI_mask = np.zeros((src.shape[0], src.shape[1], 3), np.float32)
        if (type == 0):                         #银矿石
            lower = np.array([0, 0, 221]) #0 0 221
            upper = np.array([128, 30, 255]) #128 30 255
            mask = cv2.inRange(hsv, lower, upper)
            self.remove_spot(mask, mask)
            # for r in range(0, src.shape[0]):
            #     for c in range(0, src.shape[1]):
            #         if mask[r, c] == 255:
            #             dst[r, c] = src[r, c]
            #             print("src:"+str(src[r,c])+" dst:"+str(dst[r,c]))
            # dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
            #binary = cv2.threshold(mask, 40, 255, cv2.THRESH_BINARY)
            #self.remove_spot(binary,dst)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            stone_area = 0
            index = 0
            for i in contours:
                contour_area = cv2.contourArea(i)
                if contour_area > stone_area:
                    stone_area = contour_area
                    index = i
            if stone_area > 1000:
                self.stone_rect = cv2.boundingRect(index)
                ROI_mask = cv2.bitwise_and(src, src, mask=mask)
                cv2.drawContours(src,contours,index,-1,(0,0,255))
            cv2.imshow("ROI", ROI_mask)
        elif (type == 1):                       #金矿石
            lower = np.array([26, 43, 46])
            upper = np.array([34, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            self.remove_spot(mask, mask)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            stone_area = 0
            index = 0
            for i in contours:
                contour_area = cv2.contourArea(i)
                if contour_area > stone_area:
                    stone_area = contour_area
                    index = i
            if stone_area > 1000:
                self.stone_rect = cv2.boundingRect(index)
                ROI_mask = cv2.bitwise_and(src, src, mask=mask)
            cv2.drawContours(src, contours, -1, (0, 0, 255))
            cv2.imshow("ROI", ROI_mask)
        cv2.imshow("mask", mask)
        cv2.putText(src, fps, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow("frame", src)
        pass
    def dis_midline(self,src):
        pass
    def find_sign(self,ROI_stone,src):
        sign_l = 0
        sign_r = 0
        sign_fulldark = 0
        contours,hierarchy=cv2.findContours(ROI_stone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in contours:
            if cv2.contourArea(i) < 1000:
                continue
            rects = cv2.boundingRect(i)
            if ((rects.height / rects.width) < 0.8) | ((rects.height / rects.width) > 1.2):
                continue
            s = self.detect_dot(ROI_stone(rects))
            if s == 0:
                self.sign_l = cv2.Rect(rects.tl() + self.stone_rect.tl(), rects.br()+self.stone_rect.tl())
                sign_l +=1
                cv2.rectangle(src, rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl(), (0, 0, 255), 2)
            elif s == 1:
                self.sign_r = cv2.Rect(rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl())
                sign_r += 1
                cv2.rectangle(src, rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl(), (0, 0, 255), 2)
            elif s == 2:
                self.sign_fulldark = cv2.Rect(rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl())
                sign_fulldark += 1
                cv2.rectangle(src, rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl(), (0, 0, 255), 2)
            if sign_fulldark > 0:
                sum_sign = sign_l + sign_r + sign_fulldark
                if (sum_sign == 3) & (sign_fulldark == 2):
                    print("case 1 ")
                elif (sum_sign == 2) & (sign_fulldark == 1):
                    if sign_l == 1:
                        print("90 clockwise")
                        self.sign_r = self.sign_fulldark
                        sign_r = 1
                    else:
                        print("180 clockwise")
                        self.sign_l = self.sign_fulldark
                        sign_l = 1
            if ((self.sign_l.br().x + self.sign_l.tl().x) / 2) < ((self.sign_r.br().x + self.sign_r.tl().x) / 2):
                self.center_x = ((self.sign_l.br().x + self.sign_l.tl().x) / 2 + (self.sign_r.br().x + self.sign_r.tl().x) / 2) / 2
                cv2.line(src, cv2.Point)
    def find_code(self,src):
        pass
    def get_position(self,src):
        pass
    def detect_dot(self, ROI):
        otherarea = 0
        sign_area = 0
        for i in range(0,ROI.rows):
            for j in range(0,ROI.cows):
                if ROI[i,j] ==0:
                    otherarea+=1
                else:
                    sign_area+=1
        rate = sign_area / ROI.cols / ROI.rows
        if (rate > 0.4) & (rate < 0.65):
            left_area = 0
            right_area = 0
            darkl_area = 0
            darkr_area = 0
            for i in range(0, ROI.rows):
                for j in range(0, ROI.cows):
                    if ROI[i,j] == 0:
                        left_area+=1
                    elif i > ROI.rows/2 & j > ROI.cols / 2:
                        if ROI[i,j] == 0:
                            right_area+=1
                    if i < ROI.rows / 3 | j < ROI.cols / 3:
                        if ROI[i,j] ==255:
                            darkl_area+=1
                    if i < ROI.rows / 3 | j > ROI.cols *2 / 3:
                        if ROI[i,j] == 255:
                            darkr_area+=1
    def remove_spot(self,src, dst):
        pass
        # dst = src.clone()
        # pdata = src.data
        # qdata = dst.data
        # pdata = pdata + 5 * src.cols + 6
        # qdata = qdata + 5 * dst.cols + 6
        #
        # for i in range(5,src.rows-5):
        #     for j in range(5,src.cols-5):
        #         index_white = ( * (pdata-1)+ * (pdata+1)+ * (pdata+1+src.cols)+ * (pdata-1+src.cols)+ * (pdata-1-src.cols)+ * (pdata+1-src.cols)
        #         + * (pdata+src.cols)+ * (pdata-src.cols)) / 255
        #         if index_white > 5:
        #             * qdata = 255
        #         elif index_white < 2:
        #             * qdata =  0
        #         pdata++
        #         qdata++
        #     pdata = pdata+11
        #     qdata = qdata+11