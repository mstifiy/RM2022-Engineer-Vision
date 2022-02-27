# -*- coding:utf8 -*-
# !/usr/bin/python
import cv2
import numpy as np

DEBUG_PRETREATMENT = False
SHOW_RESULT = True


class Indicator:
    """Ore release indicator light of large resource island.
    The indicator has three states: go out, blink and light up.
    we number the light bars 0 ~ 4. Facing large resource island,
    it is 0/1/2/3/4 from left to right.
    This class include detection and description of indicator light.

    Attributes:
      src_img: An image input.
      light_RC: A list including all light bar boxes detected.
      target_light_recs: A list including the four vertices of the target light box.
    """

    def __init__(self):
        self.img_width = 0
        self.img_height = 0
        self.dst_img = None
        self.src_img = None
        self.roi_img = None
        self.last_light_RC = []
        self.light_RC = []
        self.target_light_recs = []

    def detect_light(self):
        """Detect indicator lights of self.src_img.

        :return: all light bar boxes detected.
        """
        # pre-treatment
        grayImg = cv2.cvtColor(self.roi_img, cv2.COLOR_BGR2GRAY)
        _, binBrightImg = cv2.threshold(grayImg, 230, 255, cv2.THRESH_BINARY)
        # element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        # binBrightImg = cv2.dilate(binBrightImg, element)
        if DEBUG_PRETREATMENT:
            cv2.imshow("brightness_binary", binBrightImg)  # DEBUG_PRETREATMENT
        # find and filter light bars
        self.light_RC.clear()
        lightContours, _ = cv2.findContours(binBrightImg.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in lightContours:
            lightContourArea = cv2.contourArea(contour)
            # print(lightContourArea)
            if len(contour) <= 10 or 500 < lightContourArea or lightContourArea < 100:  # 去除面积过小和过大的区域
                continue
            lightRec = _, (a, b), angle = cv2.fitEllipse(contour)
            solidity = lightContourArea / (a * b)
            w_h_ratio = b / a
            # print(solidity, w_h_ratio, angle)
            if w_h_ratio < 3 or solidity < 0.5:
                continue
            # 颜色筛选
            lightMask = np.zeros((self.src_img.shape[0], self.src_img.shape[1], 1), dtype = np.uint8)
            box = cv2.boxPoints(lightRec)
            box = np.int0(box)
            cv2.fillConvexPoly(lightMask, box, (255, 255, 255))
            # lightMask = cv2.dilate(lightMask, element)
            lightImg = cv2.bitwise_and(self.src_img, self.src_img, mask = lightMask)
            meanVal = cv2.mean(lightImg, lightMask)
            if max(meanVal[0], meanVal[1], meanVal[2]) - min(meanVal[0], meanVal[1], meanVal[2]) < 25:
                self.light_RC.append((lightRec, contour))
        if 5 < len(self.light_RC):
            return None
        self.light_RC.sort(key = lambda t: t[0][0][0])  # 对灯条按照从左到右排序
        if SHOW_RESULT:
            self.showRecs([i[0] for i in self.light_RC])
        return self.light_RC

    def get_target_light(self):
        """Get target light bar position.

        :return: the four vertices of the target light box.
        """
        self.target_light_recs.clear()
        target1 = self.light_RC.copy()
        target2 = self.last_light_RC.copy()
        if not self.last_light_RC:  # 第一帧
            self.last_light_RC = self.light_RC.copy()
            return None
        if len(self.last_light_RC) == len(self.light_RC):  # 指示灯无变化
            self.last_light_RC = self.light_RC.copy()
            return None
        else:  # 指示灯可能闪烁
            for rec in self.light_RC:
                for l_rec in self.last_light_RC:
                    if cv2.pointPolygonTest(l_rec[1], rec[0][0], True) > 0:
                        target1.remove(rec)
                        target2.remove(l_rec)
                        break
            self.target_light_recs += target1 + target2
            self.last_light_RC = self.light_RC.copy()
        self.target_light_recs = [i[0] for i in self.target_light_recs]
        self.para_position()
        if SHOW_RESULT:
            self.showRecs(self.target_light_recs, "target_light")
        return self.target_light_recs

    def para_position(self):  # 对位
        tlr = self.target_light_recs.copy()[0]
        target_center = (int(tlr[0][0]), int(tlr[0][1]))
        cv2.circle(self.dst_img, target_center, 5, (255, 0, 0), -1)
        cv2.line(self.dst_img, (self.dst_img.shape[1] // 2, 0), (self.dst_img.shape[1] // 2, self.dst_img.shape[0]),
                 (255, 255, 255), 2)
        cv2.line(self.dst_img, target_center, (self.dst_img.shape[1] // 2, target_center[1]), (255, 255, 0), 2)
        distance = target_center[0] - self.dst_img.shape[1] // 2
        cv2.putText(self.dst_img, str(distance), (self.dst_img.shape[1] // 2 + 5, target_center[1] - 10),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))

    def loadImg(self, img):
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        self.src_img = img.copy()
        self.dst_img = img.copy()
        self.roi_img = img[0:int(self.img_height / 1.3), :]

    def showRecs(self, recs, LType = "normal_light"):
        color = (0, 255, 0)
        thickness = 2
        if LType == "target_light":
            color = (0, 0, 255)
            thickness = 3
        for rec in recs:
            box = cv2.boxPoints(rec)
            box = np.int0(box)
            cv2.drawContours(self.dst_img, [box], 0, color, thickness)
        cv2.imshow("result", self.dst_img)


if __name__ == "__main__":
    """indicator light test"""
    cap = cv2.VideoCapture("Indicator.mp4")
    # 实例化indicator
    indicator = Indicator()

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        cv2.imshow('frame', frame)
        # 检测指示灯灯条
        indicator.loadImg(frame)
        indicator.detect_light()
        indicator.get_target_light()
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
