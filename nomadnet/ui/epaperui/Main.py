from .Conversations import *
from .Network import *
from .BaseClasses import Component
from .EPaper import *
import threading
from PIL import ImageDraw, ImageFont
import RNS
import sys
import os
fontdir = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'epaperui/assets/fonts')
picdir = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'epaperui/assets')


class MainDisplay(Component):
    def __init__(self, app):
        try:
            super().__init__(app)
            self.ui = EPaperInterface()
            self.height = self.ui.display.height
            self.width = self.ui.display.width
            self.app_is_running = True
            self.should_update_render = False

            self.pages_display = PagesDisplay(self.app, self)
            self.start()

        except Exception as e:
            self.ui.shutdown()
            RNS.log("Error in Main Display. Exception was: " + str(e), RNS.LOG_ERROR)
            print("Error in the fucking Main Display. Exception was: " + str(e))

    def start(self):
        self.pages_display.start()

    def update(self):
        return

class PagesDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.height = round(self.ui.height * .9)
        self.width = self.ui.width
        self.conversations_display = ConversationsDisplay(self.app, self)
        self.network_display = NetworkDisplay(self.app, self)
        self.pages = [self.network_display, self.conversations_display]
        self.selected_page_index = EPaperInterface.PAGE_INDEX_NETWORK

    def start(self):
        selected_page = self.pages[self.selected_page_index]
        selected_page.start()
        return

    def update(self):
        selected_page = self.pages[self.selected_page_index]
        self.ui.reset_canvas()
        draw = ImageDraw.Draw(self.ui.canvas)
        draw.text((0, 0), selected_page.title,
                  font=EPaperInterface.FONT_12)
        self.ui.request_render()
        selected_page.start()
