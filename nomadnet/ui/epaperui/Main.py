import RNS
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'epaperui/assets/fonts')
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'epaperui/assets')    
from nomadnet.vendor.waveshare import gt1151
from nomadnet.vendor.waveshare import epd2in13_V3

from PIL import Image,ImageDraw,ImageFont
import threading

from .Conversations import *

FONT_12 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)


class EPaperInterface():
    # For context, see documentation for Waveshare 2.13 inch touch e-paper device. 
    # https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT_Manual#Raspberry_Pi

    MAX_PARTIAL_REFRESHES = 10 # Protects screen from excessive partial refresh
    MAX_REFRESH_INTERVAL = 24 * 60 * 60 * 1000 # 24 hours
    TIMEOUT_INTERVAL = 10 * 60 * 1000 # 10 minutes

    def __init__(self):
        try:
            self.should_evaluate_touch = True
            self.screen_is_active = True
            self.display = epd2in13_V3.EPD()
            self.image = Image.new('1', (self.display.height, self.display.width), 255)
            self.touch_interface = gt1151.GT1151()
            self.touch_interface_dev = gt1151.GT_Development()
            self.touch_interface_old = gt1151.GT_Development()
            self.touch_thread = threading.Thread(target = self.touch_response_loop)
            self.refresh_thread = threading.Thread(target = self.refresh_loop)
            self.partial_refresh_counter = 0
            self.last_full_refresh = time.time()
            self.last_touch = time.time()
            
            self.touch_thread.daemon = True
            self.touch_thread.start()
            self.refresh_thread.daemon = True
            self.refresh_thread.start()

            self.display.init(self.display.FULL_UPDATE)
            self.touch_interface.GT_Init()
            self.display.Clear(0xFF)

            
        except Exception as e:
            RNS.log("An error occured in the E-Paper UI. Exception was:" + str(e), RNS.LOG_ERROR)
            self.quit()

    def quit(self):
        self.should_evaluate_touch = False
        self.screen_is_active = False
        self.sleep()
        time.sleep(2)
        self.touch_thread.join()
        self.refresh_thread.join()
        self.display.Dev_exit()
        quit()

    def sleep(self):
        self.clear_screen()
        self.display.sleep()
    
    def awake(self):
        self.display.init(self.display.FULL_UPDATE)
        self.clear_screen()

    def clear_screen(self):
        self.display.Clear(0xFF)


    def touch_response_loop(self) :
        while self.should_evaluate_touch:
            if(self.touch_interface.digital_read(self.touch_interface.INT) == 0):
                self.touch_interface_dev.Touch = 1
            else :
                self.touch_interface_dev.Touch = 0

    def refresh_loop(self):
        while self.screen_is_active:
            now = time.time()
            if now - self.last_touch > self.TIMEOUT_INTERVAL:
                self.sleep()
            elif now - self.last_full_refresh > self.MAX_REFRESH_INTERVAL:
                self.clear_screen()
            time.sleep(5)

class MainDisplay():
    def __init__(self, ui, app):
        self.ui = ui
        self.app = app
        self.e_paper = EPaperInterface()

        self.app_is_running = True
        self.conversations_display = ConversationsDisplay(self.app)
        self.pages = [self.conversations_display]
        self.menu_display = Menu(self.app)
        self.page_display = Pages(self.app, self.pages)
        self.image = None
        

    def start(self):
        try:
            self.menu_display.start()
            self.render()
            while self.app_is_running:
                time.sleep(5)
            self.e_paper.quit()
        except Exception as e:
            RNS.log("An error occured in the Main Display. Exception was:" + str(e), RNS.LOG_ERROR)
            self.e_paper.quit()

    def render(self):
        display = self.e_paper.display
        image = self.image

        image = Image.new('1', (display.height, display.width), 255)
        image.rotate(90)
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), str(self.app.identity), font=FONT_12, fill=0)
        display.displayPartBaseImage(display.getbuffer(image))
        display.init(display.PART_UPDATE)
        self.page_display.render()


class Pages():
    def __init__(self, app, pages):
        self.app = app

        self.pages = pages
        self.selected_page = 0


    def start(self):
        return

    def swipe_handler(self):
        # interpret swipe gesture from touch_interface
        # if diff x difference is greater than y differeence, interperet as a horizontal swipe
        # move up self.pages on right swipe and down on left swipe

        return
    
    def render(self):
        return


class Menu():
    def __init__(self, app):
        self.app = app

    def start(self):
        return
    
    def render(self):
        return
