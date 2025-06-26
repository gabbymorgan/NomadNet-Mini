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

    def start(self):
        self.pages_display.start()

    def update(self):
        return

class PagesDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.height = round(self.ui.height * .9)
        self.width = self.ui.width
        self.conversation_display = ConversationDisplay(self.app, self)
        self.network_display = NetworkDisplay(self.app, self)
        self.pages = [self.network_display, self.conversation_display]
        self.current_page_index = EPaperInterface.PAGE_INDEX_NETWORK
        self.prev_page_index = EPaperInterface.PAGE_INDEX_NETWORK

    def start(self):
        for page in self.pages:
            page.start()
        self.update()


    def update(self):
        current_page = self.pages[self.current_page_index]
        if self.current_page_index != self.prev_page_index:
            self.ui.reset_canvas()
            current_page.update()
        self.prev_page_index = self.current_page_index
