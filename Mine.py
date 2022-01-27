import cv2
import numpy
from enum import Enum


class MINETYPE(Enum):
    WHITE = 0
    YELLOW = 1


class mine():
    position = [0, 0, 0, 0, 0, 0]      #x,y,z,pith,roll,yaw
    sign = [0, 0, 0, 0]
    def detect_mine(self, src, type,fps):
        cv2.putText(src, fps, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow("frame", src)
        pass
    def dis_midline(self,src):
        pass
    def fin_sign(self,src):
        pass
    def find_code(self,src):
        pass
    def get_position(self,src):
        pass
    def get_type(self):
        pass
    def detect_dot(self):
        pass
    def remove_spot(self):
        pass
