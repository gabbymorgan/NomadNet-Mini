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

        self.conversations_display = ConversationsDisplay(self.app)
        self.menu_display = MenuDisplay(self.app)
        self.sub_displays = SubDisplays(self.app)
        self.image = None
        

    def start(self):
        self.menu_display.start()
        display = self.e_paper.display
        touch_interface = self.e_paper.touch_interface

        self.image = Image.new('1', (display.height, display.width), 255)
        self.image.rotate(90)
        draw = ImageDraw.Draw(self.image)
        draw.text((10, 10), str(self.app.identity), font=FONT_12, fill=0)
        display.displayPartBaseImage(display.getbuffer(self.image))
        display.init(display.PART_UPDATE)
        time.sleep(10)

class SubDisplays():
    def __init__(self, app):
        self.app = app

    def start():
        return

class MenuDisplay():
    def __init__(self, app):
        self.app = app

    def start(self):
        return
