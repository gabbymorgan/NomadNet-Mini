import os
import sys
import time
import LXMF
import nomadnet
import RNS
import traceback
import threading

from PIL import Image, ImageDraw
from .EPaper import *
from .BaseClasses import Component


class NetworkDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.title = "Directory"
        self.current_announce_index = 0
        self.announces = self.app.directory.announce_stream
        self.swipe_thread = threading.Thread(
            daemon=True, target=self.swipe_listener)

        print(self.announces)

    def swipe_listener(self):
        gt = self.ui.touch_interface
        GT_Dev = self.ui.touch_interface_dev
        GT_Old = self.ui.touch_interface_old

        while self.ui.screen_is_active:
            selected_page = self.parent.pages[self.parent.selected_page_index]
            while selected_page.title == self.title:
                gt.GT_Scan(GT_Dev, GT_Old)
                if (GT_Old.X[0] == GT_Dev.X[0] and GT_Old.Y[0] == GT_Dev.Y[0] and GT_Old.S[0] == GT_Dev.S[0]):
                    continue
                elif (GT_Dev.Y[0] < (self.ui.height - 40)):
                    new_current_announce_index = min(
                        len(self.announces)-1, self.current_announce_index + 1)
                elif (GT_Dev.Y[0] > 40):
                    new_current_announce_index = max(
                        0, self.current_announce_index - 1)
                if new_current_announce_index != self.current_announce_index:
                    self.current_announce_index = new_current_announce_index
                    self.update()
                self.ui.last_touched = time.time()

    def start(self):
        self.swipe_thread.start()
        self.update()

    def update(self):
        self.ui.reset_canvas()
        draw = ImageDraw.Draw(self.ui.canvas)
        draw.text(
            (0, 20), self.announces[self.current_announce_index][2], font=self.ui.FONT_15)
        draw.text((0, 40), self.announces[self.current_announce_index][1].hex(
        ), font=self.ui.FONT_12)
        draw.text((0, 60), time.strftime('%Y-%m-%d %H:%M:%S',
                  time.localtime(self.announces[self.current_announce_index][0])), font=self.ui.FONT_12)
        draw.text(
            (0, 80), self.announces[self.current_announce_index][3], font=self.ui.FONT_12)
        self.parent.update()
