# -*- coding:utf8 -*-
# !/usr/bin/python
import cv2
import numpy as np


class Indicator:
    """Ore release indicator light of large resource island.
    The indicator has three states: go out, blink and light up.
    we number the light bars 0 ~ 4. Facing large resource island,
    it is 0/1/2/3/4 from left to right.
    This class include detection and description of indicator light.

    Attributes:
      src_img: An image input.
      light_boxes: A list including all light bar boxes detected.
      target_light_rect: A list including the four vertices of the target light box.
    """

    def __init__(self, img):
        self.src_img = img
        self.light_boxes = []
        self.target_light_rect = []

    def detect_light(self):
        """Detect indicator lights of self.src_img.

        :return: all light bar boxes detected.
        """

        pass

    def get_target_light(self):
        """Get target light bar position.

        :return: the four vertices of the target light box.
        """
        pass
