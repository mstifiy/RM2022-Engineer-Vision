import copy

import cv2
import numpy as np
import math
import Globla
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
        ROI_mask = copy.deepcopy(np.zeros((src.shape[0], src.shape[1], 3), np.float32))
        binary = np.zeros((src.shape[0], src.shape[1], 3), np.float32)
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
            dst = cv2.bitwise_and(src, src, mask=mask)
            #flag = self.find_sign(binary, src)
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
            for i in range(0, len(contours)):
                contour_area = cv2.contourArea(contours[i])
                if contour_area > stone_area:
                    stone_area = contour_area
                    index = i
            if stone_area > 1000:
                self.stone_rect = cv2.boundingRect(contours[index])
                dst = copy.deepcopy(cv2.bitwise_and(src, src, mask=mask))
                dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
                ret, binary = cv2.threshold(dst, 40, 255, cv2.THRESH_BINARY)
                flag = self.find_sign(mask, src)
                cv2.imshow("dst", dst)
                x, y, w, h = self.stone_rect
                ROI_mask = binary[y:y+h, x:x+w]
                #ROI_mask = copy.deepcopy(binary[y:y+h, x:x+w])
                cv2.drawContours(src, contours, index, (255, 0, 0), -1)
                # ROI_stone = binary(self.stone_rect)
                # cv2.bitwise_xor(ROI_stone,ROI_mask,ROI_stone)

                #flag = self.find_sign(mask, src)

            #cv2.drawContours(src, contours, -1, (0, 0, 255), 2)
            if Globla.GET_DIS_ON:
                self.dis_midline(src, contours)
            cv2.imshow("ROI", ROI_mask)
        #cv2.imshow("mask", mask)
        cv2.putText(src, fps, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow("frame", src)
        pass

    def dis_midline(self,src, contours):
        for i in contours:
            rect = cv2.minAreaRect(i)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            dx = box[1][0] - box[0][0]
            dy = box[1][1] - box[0][1]
            if dx != 0:
                angle = math.atan(dy / dx)
            else:
                angle = 0
            if angle >= -0.52359877559829887307710723054658 and angle <= 0.52359877559829887307710723054658:
                cv2.drawContours(src, [box], 0, (0, 255, 0), 2)
                left = src.shape[1]
                mid = np.int0(src.shape[1] / 2)
                #cv2.line(src, (mid, 0), (mid , src.shape[0]), (128, 37, 180))      #中线
                right = 0
                for j in box:
                    if j[0] > right:
                        right = j[0]
                    if j[0] < left:
                        left = j[0]
                dmid = (left + right) / 2
                dmid = np.int0(dmid)
                cv2.line(src, (dmid, 0), (dmid, src.shape[1]), (90, 60, 68), 2)
                return (mid - (dmid))



    def find_sign(self,ROI_stone,src):
        print("find_sign is run")
        sign_l = 0
        sign_r = 0
        sign_fulldark = 0
        contours, hierarchy = cv2.findContours(ROI_stone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in contours:
            if cv2.contourArea(i) < 1000:
                print("pass")
                continue
            rects = cv2.boundingRect(i)
            [x, y, w, h] = rects
            print(rects)
            if ((h / w) < 0.8) | ((h / w) > 1.2):
                continue
            s = self.detect_dot(copy.deepcopy(ROI_stone[y:y+h, x:x+w]))
            print("s="+str(s))
            self.sign_l = (0, 0, 0, 0)
            self.sign_r = (0, 0, 0, 0)
            if s == 0:
                x = rects.tl().x + self.stone_rect.tl().x
                y = rects.tl().y + self.stone_rect.tl().y
                w = rects.br().x+self.stone_rect.tl().x - x
                h = rects.br().y+self.stone_rect.tl().y - y
                self.sign_l = (x, y, w, h)
                sign_l += 1
                cv2.rectangle(src, rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl(), (0, 0, 255), 2)
            elif s == 1:
                x = rects.tl().x + self.stone_rect.tl().x
                y = rects.tl().y + self.stone_rect.tl().y
                w = rects.br().x + self.stone_rect.tl().x - x
                h = rects.br().y + self.stone_rect.tl().y - y
                self.sign_r = (x, y, w, h)
                sign_r += 1
                cv2.rectangle(src, rects.tl() + self.stone_rect.tl(), rects.br() + self.stone_rect.tl(), (0, 0, 255), 2)
            elif s == 2:
                x = rects.tl().x + self.stone_rect.tl().x
                y = rects.tl().y + self.stone_rect.tl().y
                w = rects.br().x + self.stone_rect.tl().x - x
                h = rects.br().y + self.stone_rect.tl().y - y
                self.sign_fulldark = (x, y, w, h)
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
        slbrx = self.sign_l[0]+self.sign_l[2]
        sltlx = self.sign_l[0]
        srbrx = self.sign_r[0]+self.sign_r[2]
        srtlx = self.sign_r[0]
        if ((slbrx + sltlx) / 2) < ((srbrx + srtlx) / 2):
                self.center_x = ((slbrx + sltlx) / 2 + (srbrx + srtlx) / 2) / 2
                print("found!")
                cv2.line(src, cv2.Point,(0,255,255),2)
    def find_code(self,src):
        pass
    def get_position(self,src):
        pass
    def detect_dot(self, ROI):
        otherarea = 0
        sign_area = 0
        #print("0:"+str(ROI.shape[0]) + " 1:" + str(ROI.shape[1]))
        for i in range(0, ROI.shape[0]):
            for j in range(0, ROI.shape[1]):
                if ROI[i, j] == 0:
                    otherarea += 1
                else:
                    sign_area += 1
        rate = sign_area / ROI.shape[1] / ROI.shape[0]
        if (rate > 0.4) & (rate < 0.65):
            left_area = 0
            right_area = 0
            darkl_area = 0
            darkr_area = 0
            for i in range(0, ROI.shape[0]):
                for j in range(0, ROI.shape[1]):
                    if ROI[i, j] == 0:
                        left_area += 1
                    elif i > ROI.shape[0] /2 & j > ROI.shape[1] / 2:
                        if ROI[i, j] == 0:
                            right_area += 1
                    if i < ROI.shape[0] / 3 | j < ROI.shape[1] / 3:
                        if ROI[i, j] == 255:
                            darkl_area += 1
                    if i < ROI.shape[0] / 3 | j > ROI.shape[1] *2 / 3:
                        if ROI[i, j] == 255:
                            darkr_area += 1
            if (left_area * 4 / ROI.shape[1] / ROI.shape[0] > 0.9) & (darkr_area / (ROI.shape[1] * ROI.shape[0] * 5 / 9) > 0.7):
                return 1
            elif (right_area * 4 / ROI.shape[1] / ROI.shape[0] > 0.9) & (darkl_area / (ROI.shape[1] * ROI.shape[0] * 5 / 9) > 0.7):
                return 0
        elif sign_area / ROI.shape[1] / ROI.shape[0] > 1:
            return 2
        return 4
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