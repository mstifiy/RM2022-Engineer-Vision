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
    def detect_mine(self, src, ROI,original_rect , contour, ifgetdis):
        antiROI = copy.deepcopy(cv2.bitwise_not(ROI))
        self.find_sign(antiROI,src,original_rect)
        if ifgetdis:
            middis = self.dis_midline(src, contour)
            if middis != None:
                print(middis)
        cv2.imshow("ROI", ROI)
        cv2.imshow("antiROI", antiROI)

    def dis_midline(self, src, contour):
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        dx = box[1][0] - box[0][0]
        dy = box[1][1] - box[0][1]
        mid = np.int0(src.shape[1] / 2)
        cv2.line(src, (mid, 0), (mid, src.shape[0]), (255, 0, 255), 1)  # 中线
        if dx != 0:
            angle = math.atan(dy / dx)
        else:
            angle = 0
        if angle >= -0.52359877559829887307710723054658 and angle <= 0.52359877559829887307710723054658:
            cv2.drawContours(src, [box], 0, (0, 255, 0), 2)
            left = src.shape[1]
            right = 0
            for j in box:
                if j[0] > right:
                    right = j[0]
                if j[0] < left:
                    left = j[0]
            dmid = (left + right) / 2
            dmid = np.int0(dmid)
            cv2.line(src, (dmid, 0), (dmid, src.shape[1]), (30, 144, 255), 1)
            return (mid - (dmid))



    def find_sign(self,ROI_stone,src,orect):
        shape = ROI_stone.shape
        sidenum = 1
        xyratio = shape[1]/shape[0]
        if (xyratio < 1.5 and xyratio > 1.05) or (xyratio > 0.65 and xyratio< 0.95):
            sidenum = 2
        elif xyratio >= 0.95 and xyratio <= 1.05:
            sidenum = 1
        contours, hierarchy = cv2.findContours(ROI_stone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        tl = []
        tr = []
        bl = []
        br = []
        b = []
        for i in contours:
            recta = cv2.boundingRect(i)
            rect = cv2.minAreaRect(i)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            dx = orect[0]
            dy = orect[1]
            if_have_corner = havecorner(recta, shape)
            if if_have_corner:
                point1 = np.array(box, dtype="float32")
                point2 = np.array([[0, 24], [0, 0], [24, 0], [24, 24]], dtype="float32")
                M = cv2.getPerspectiveTransform(point1, point2)
                dot_ROI = cv2.warpPerspective(ROI_stone, M, (24, 24))
                type = self.detect_dot(dot_ROI)
                for j in box:
                    j[0] += dx
                    j[1] += dy
                cv2.drawContours(src, [box], 0, (128, 100, 5), 2)
                cv2.putText(src, type, box[0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cx, cy, w, h = recta
                x = np.int0((w / 2) + cx + dx)
                y = np.int0((h / 2) + cy + dy)
                if type == 'tl':
                    tl.append((x, y))
                elif type == 'tr':
                    tr.append((x, y))
                elif type == 'bl':
                    bl.append((x, y))
                elif type == 'br':
                    br.append((x, y))
                elif type == 'B':
                    b.append((x, y))
            lines = []
            darklines = []
            for m in tl:
                for j in tr:
                    lines.append(line(m, j))
                for j in bl:
                    lines.append(line(m, j))
            for m in tr:
                for j in br:
                    lines.append(line(m, j))
            for m in bl:
                for j in br:
                    lines.append(line(m, j))
            for m in b:
                for j in tl + tr + bl + br:
                    darklines.append(line(m, j))
            leaves = []                                  #可能存在的叶子集合
            for m in range(len(darklines)-1):
                for j in range(m+1, len(darklines)):
                    if_same_point = False
                    same_point = [0, 0]
                    leaf = [[0, 0], [0, 0]]
                    for p1 in range(2):
                        for p2 in range(2):
                            if darklines[m].pt[p1] == darklines[j].pt[p2]:
                                same_point = darklines[m].pt[p1]
                                if_same_point = True
                                leaf = [darklines[m].pt[1 - p1], darklines[j].pt[1 - p2]]
                    if if_same_point:
                        angle = lineagle(darklines[m], darklines[j])
                        if angle > 1.45 and angle < 1.7:
                            l = darklines[m].lenth() / darklines[j].lenth()
                            if l > 0.8 and l < 1.2 :
                                lf = dark_corner(same_point, leaf[0], leaf[1])
                                leaves.append(lf)
            if len(leaves) > 1:
                for m in range(len(leaves) - 1):                    #排查标签
                    for j in range(m + 1, len(leaves)):
                        if len(leaves) > 1:
                            if if_same_leaves(leaves[m], leaves[j]):
                                leaves[m]._draw(src)
                                leaves[j]._draw(src)


                                continue
                            elif leaves[m].average_length() > leaves[j].average_length():
                                pass
                                # leaves.remove(leaves[j])
                            elif leaves[m].average_length() < leaves[j].average_length():
                                pass
                                # leaves.remove(leaves[m])
            elif len(leaves) == 1:
                leaves[0]._draw(src)
                if leaves[0].leaves[0][0] < leaves[0].center[0] and leaves[0].line[0].angle() < 0.52359877559829887307710723054658 and leaves[0].line[0].angle() > -0.52359877559829887307710723054658:
                    if leaves[0].leaves[1][1] > leaves[0].center[1] and (leaves[0].line[1].angle() > 1.0471975511965977461542144610932 or leaves[0].line[1].angle() < -1.0471975511965977461542144610932):
                        print("right")
                    elif leaves[0].leaves[1][1] < leaves[0].center[1] and (leaves[0].line[1].angle() > 1.0471975511965977461542144610932 or leaves[0].line[1].angle() < -1.0471975511965977461542144610932):
                        print("under")
                elif leaves[0].leaves[0][0] > leaves[0].center[0] and leaves[0].line[0].angle() < 0.52359877559829887307710723054658 and leaves[0].line[0].angle() > -0.52359877559829887307710723054658:
                    if leaves[0].leaves[1][1] > leaves[0].center[1] and (leaves[0].line[1].angle() > 1.0471975511965977461542144610932 or leaves[0].line[1].angle() < -1.0471975511965977461542144610932):
                        print("upper")
                    elif leaves[0].leaves[1][1] < leaves[0].center[1] and (leaves[0].line[1].angle() > 1.0471975511965977461542144610932 or leaves[0].line[1].angle() < -1.0471975511965977461542144610932):
                        print("left")


            
    def find_code(self,src):
        pass
    def get_position(self,src):
        pass
    def detect_dot(self, ROI):
        area = 0
        tl = 0
        tr = 0
        bl = 0
        br = 0
        for i in range(0, 24):
            for j in range(0, 24):
                if ROI[i, j] == 255:
                    area += 1
                    if i <= 12:
                        if j <= 12:
                            tl += 1
                        else:
                            tr += 1
                    else:
                        if j <= 12:
                            bl += 1
                        else:
                            br += 1
        if tl / 144 < 0.03:
            return 'bl'
        elif tr / 144 < 0.03:
            return 'tl'
        elif bl / 144 < 0.03:
            return 'br'
        elif br / 144 < 0.03:
            return 'tr'
        arearatio = area / 576
        if arearatio >= 0.9 and arearatio <= 1.03:
            return 'B'
        else:
            return 'R'
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

def havecorner(rect, shape):
    x, y, w, h = rect
    if w / h < 0.85 and w / h > 1.15:
        return 0
    if w < 15 or h < 15:
        return 0
    if x == 0:
        if y == 0:
            return 0
        elif y + h == shape[0]:
            return 0
    elif x + w == shape[1]:
        if y == 0:
            return 0
        elif y + h == shape[0]:
            return 0
    return 1

class line:
    def __init__(self, pt1, pt2):
        self.pt = [pt1, pt2]
    def draw(self, src):
        cv2.line(src, self.pt[0], self.pt[1], (0, 102, 255), 2)
    def lenth(self):
        a = ((self.pt[0][0] - self.pt[1][0]) ** 2) + ((self.pt[0][1] - self.pt[1][1]) ** 2)
        a = np.float32(a ** 0.5)
        return a
    def angle(self):
        x = self.pt[0][0] - self.pt[1][0]
        y = self.pt[0][1] - self.pt[1][1]
        if x == 0:
            return 1.5707963267948966192313216916398
        return abs(math.atan(y / x))

class dark_corner:
    def __init__(self, center, pt1, pt2):
        self.center = center
        self.leaves = [pt1, pt2]
        self.line = [line(center, pt1), line(center, pt2)]
    def average_length(self):
        a = self.line[1].lenth()
        b = self.line[0].lenth()
        s = np.int0((a + b) / 2)
        return s
    def _draw(self, src):
        self.line[0].draw(src)
        self.line[1].draw(src)

def lineagle(lineA, lineB):
    angle = abs(lineA.angle() - lineB.angle())
    return angle

def if_same_leaves(coner1, corner2):
    if coner1.leaves[0] == corner2.leaves[0] and coner1.leaves[1] == corner2.leaves[1]:
        return True
    elif coner1.leaves[0] == corner2.leaves[1] and coner1.leaves[1] == corner2.leaves[0]:
        return True
    else:
        return False