# -*- coding:utf8 -*-
# !/usr/bin/python
import cv2
import numpy as np


class Exchanger:
    """Exchange slot is used to exchange ores to money.
    This class include detection and description of Exchange slot.

    Attributes:
      src_img: An image input.
      slot_rect: A list including the four vertices of the slot box.
      position: A list including 3D pose of exchange slot in world coordinate system.
    """

    def __init__(self, img):
        self.src_img = img
        self.slot_rect = []
        self.position = [0, 0, 0, 0, 0, 0]  # x, y, z, pitch, roll, yaw

    def detect_slot(self):
        """Detect exchange slot of self.src_img.

        :return: A list including the four vertices of the slot box.
        """
        pass

    def pose_solution(self):
        """Solve 3D pose in world coordinate system.

        :return: 3D pose [x, y, z, pitch, roll, yaw].
        """
        pass
