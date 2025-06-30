import os
import sys
import time
import LXMF
import nomadnet
import RNS
import traceback
import threading
import arrow

from PIL import ImageDraw
from .EPaper import *
from .BaseClasses import Component
from .EPaper import EPaperInterface


class NetworkDisplay(Component):
    def __init__(self, parent):
        super().__init__(parent)
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
                    if self.ui.tap_x > self.ui.width - 40:
                        if (self.ui.tap_y > (self.ui.height - 30)):
                            self.current_peer_index = max(
                                0, self.current_peer_index - 1)
                            self.update()
                        elif (self.ui.tap_y < 40):
                            self.current_peer_index = min(
                                len(self.peers)-1, self.current_peer_index + 1)
                            self.update()
                    else:
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_CONVERSATION
                        self.parent.conversation_display.conversation_peer = self.peers[
                            self.current_peer_index]
                        self.parent.update()
            time.sleep(0.02)

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

            self.ui.reset_canvas()
            background = Image.open(os.path.join(
                    picdir, 'network-display.bmp'))
            self.ui.canvas.paste(background, (0, 0))           
            draw = ImageDraw.Draw(self.ui.canvas)
            draw.text((0, 0), self.title,
                      font=EPaperInterface.FONT_12)
            if self.peers and len(self.peers) > 0:
                current_peer = self.peers[self.current_peer_index]
                timestamp = arrow.get(current_peer[0])
                draw.text(
                    (25, 30), current_peer[2], font=self.ui.FONT_15)
                draw.text((25, 52), current_peer[1].hex(
                ), font=self.ui.FONT_12)
                draw.text((25, 70), timestamp.humanize(), font=self.ui.FONT_12)

            else:
                draw.text((25, 25), "aww no friends!")

            self.ui.request_render()

        except Exception as e:
            RNS.log(
                "Error in update method of NetworkDisplay component. Exception is: " + e, RNS.LOG_ERROR)
