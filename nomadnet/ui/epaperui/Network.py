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
        self.prev_peer_index = 0
        self.network_touch_thread = threading.Thread(
            daemon=True, target=self.network_touch_listener)

    def network_touch_listener(self):
        while self.ui.app_is_running:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_NETWORK:
                self.ui.detect_screen_interaction()
                if self.ui.screen_is_active and self.ui.did_tap:
                    if (self.ui.tap_y > (self.ui.height - 20)):
                        self.current_peer_index = max(
                            0, self.current_peer_index - 1)
                        self.update()
                    elif (self.ui.tap_y < 20):
                        self.current_peer_index = min(
                            len(self.peers)-1, self.current_peer_index + 1)
                        self.update()
                    else:
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_CONVERSATION
                        self.parent.conversation_display.conversation_peer = self.peers[
                            self.current_peer_index]
                        self.parent.update()

    def start(self):
        self.network_touch_thread.start()
        self.update()

    def update(self):
        try:
            if self.parent.current_page_index != EPaperInterface.PAGE_INDEX_NETWORK:
                return
            max_height = self.ui.height
            max_width = self.ui.width
            mid_height = self.ui.width//2
            mid_width = self.ui.width//2

            if self.current_peer_index != self.prev_peer_index:
                self.parent.update()
            self.prev_peer_index = self.current_peer_index

            draw = ImageDraw.Draw(self.ui.canvas)
            draw.text((0, 0), self.title,
                      font=EPaperInterface.FONT_12)
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

        except Exception as e:
            RNS.log(
                "Error in update method of NetworkDisplay component. Exception is: " + e, RNS.LOG_ERROR)
