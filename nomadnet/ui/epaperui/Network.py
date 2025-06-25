import os
import sys
import time
import LXMF
import nomadnet
import RNS
import traceback
import threading

from PIL import ImageDraw
from .EPaper import *
from .BaseClasses import Component
from .EPaper import EPaperInterface


class NetworkDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.title = "Directory"
        self.peers = [
            x for x in self.app.directory.announce_stream if x[3] == "peer"]
        self.current_peer_index = 0
        self.touch_flag = False
        self.touch_thread = threading.Thread(
            daemon=False, target=self.touch_listener)

    def touch_listener(self):
        while self.ui.app_is_running and self.touch_flag:
            if self.parent.selected_page_index != EPaperInterface.PAGE_INDEX_NETWORK:
                continue
            touch_x = self.ui.touch_interface_dev.X[0]
            touch_y = self.ui.touch_interface_dev.Y[0]
            touch_s = self.ui.touch_interface_dev.X[0]
            prev_touch_x = self.ui.touch_interface_old.X[0]
            prev_touch_y = self.ui.touch_interface_old.Y[0]
            prev_touch_s = self.ui.touch_interface_old.S[0]
            touch_is_new = touch_y != prev_touch_y and touch_s > 0

            if self.ui.screen_is_active and touch_is_new:
                if (touch_y > (self.ui.height - 20)):
                    new_current_peer_index = max(
                        0, self.current_peer_index - 1)
                elif (touch_y < 20):
                    new_current_peer_index = min(
                        len(self.peers)-1, self.current_peer_index + 1)
                else:
                    self.parent.selected_page_index = EPaperInterface.PAGE_INDEX_CONVERSATION
                    self.parent.conversations_display.conversation_peer = self.peers[
                        self.current_peer_index]
                    self.touch_flag = False
                    self.parent.conversations_display.start()
                    continue
                if new_current_peer_index != self.current_peer_index:
                    self.current_peer_index = new_current_peer_index
                    self.update()

    def start(self):
        self.touch_flag = True
        self.touch_thread.start()
        self.update()

    def update(self):
        max_height = self.ui.height
        max_width = self.ui.width
        mid_height = self.ui.width//2
        mid_width = self.ui.width//2

        self.ui.reset_canvas()
        draw = ImageDraw.Draw(self.ui.canvas)
        draw.line((15, mid_width-15, 0, mid_width), fill=0, width=2)
        draw.line((0, mid_width, 15, mid_width+15), fill=0, width=2)
        draw.line((max_height-15, mid_width-15,
                  max_height, mid_width), fill=0, width=2)
        draw.line((max_height, mid_width, max_height -
                  15, mid_width+15), fill=0, width=2)

        if self.peers and len(self.peers) > 0:
            draw.text(
                (25, 25), self.peers[self.current_peer_index][2], font=self.ui.FONT_15)
            draw.text((25, 50), self.peers[self.current_peer_index][1].hex(
            ), font=self.ui.FONT_12)
            draw.text((25, 70), time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(self.peers[self.current_peer_index][0])), font=self.ui.FONT_12)
            draw.text(
                (25, 90), self.peers[self.current_peer_index][3], font=self.ui.FONT_12)
            draw.text((self.ui.height//2, self.ui.width-20),
                      str(self.current_peer_index + 1), font=self.ui.FONT_12)

        else:
            draw.text((25, 25), "aww no friends!")
        
        self.ui.request_render()