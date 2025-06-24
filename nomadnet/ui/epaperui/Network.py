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
        self.touch_thread = threading.Thread(
            daemon=False, target=self.touch_listener)

    def touch_listener(self):
        while self.ui.app_is_running:
            touch_y = self.ui.touch_interface_dev.Y[0]
            prev_touch_y = self.ui.touch_interface_old.Y[0]
            selected_page = self.parent.pages[self.parent.selected_page_index]
            if self.ui.screen_is_active and selected_page.title == self.title:
                if touch_y == prev_touch_y:
                    continue
                elif (touch_y < (self.ui.height - 20)):
                    new_current_announce_index = min(
                        len(self.announces)-1, self.current_announce_index + 1)
                elif (touch_y > 20):
                    new_current_announce_index = max(
                        0, self.current_announce_index - 1)
                print(new_current_announce_index)
                if new_current_announce_index != self.current_announce_index:
                    self.current_announce_index = new_current_announce_index
                    self.update()

    def start(self):
        self.touch_thread.start()
        self.update()

    def update(self):
        max_height = self.ui.height
        max_width = self.ui.width
        mid_height = self.ui.width//2
        mid_width = self.ui.width//2

        self.ui.reset_canvas()
        draw = ImageDraw.Draw(self.ui.canvas)
        draw.line((15,mid_width-15,0,mid_width), fill=0, width=2)
        draw.line((0,mid_width,15,mid_width+15), fill=0, width=2)
        draw.line((max_height-15,mid_width-15, max_height,mid_width), fill=0, width=2)
        draw.line((max_height, mid_width, max_height-15 ,mid_width+15), fill=0, width=2)
        draw.text(
            (25, 25), self.announces[self.current_announce_index][2], font=self.ui.FONT_15)
        draw.text((25, 50), self.announces[self.current_announce_index][1].hex(
        ), font=self.ui.FONT_12)
        draw.text((25, 70), time.strftime('%Y-%m-%d %H:%M:%S',
                  time.localtime(self.announces[self.current_announce_index][0])), font=self.ui.FONT_12)
        draw.text(
            (25, 90), self.announces[self.current_announce_index][3], font=self.ui.FONT_12)
        draw.text((self.ui.height//2, self.ui.width-20),
                  str(self.current_announce_index + 1), font=self.ui.FONT_12)
        self.parent.update()
