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

class MainDisplay():
    def __init__(self, ui, app):
        print(fontdir)
        try:
            self.ui = ui
            self.app = app

            self.flag_t = 1
            self.e_paper_display = epd2in13_V3.EPD()
            self.touch_interface = gt1151.GT1151()
            self.touch_interface_dev = gt1151.GT_Development()
            self.touch_interface_old = gt1151.GT_Development()
            self.thread = threading.Thread(target = self.pthread_irq)
            self.font_12 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)

            self.conversations_display = ConversationsDisplay(self.app)
            self.menu_display = MenuDisplay(self.app)
            self.sub_displays = SubDisplays(self.app)

            self.image = None
            
        except Exception as e:
            print(e)

    def start(self):
        self.menu_display.start()
        try:            
            epd = self.e_paper_display
            gt = self.touch_interface

            epd.init(epd.FULL_UPDATE)
            gt.GT_Init()
            epd.Clear(0xFF)

            self.thread.daemon = True
            self.thread.start()

            self.image = Image.new('1', (epd.height, epd.width), 255)
            self.image.rotate(90)
            draw = ImageDraw.Draw(self.image)
            draw.text((10, 10), str(self.app.identity), font=self.font_12, fill=0)
            epd.displayPartBaseImage(epd.getbuffer(self.image))
            epd.init(epd.PART_UPDATE)
            time.sleep(10)

            quit()

        except Exception as e:
            print(e)
            quit()

    def quit(self):
        logterm_pid = None
        self.flag_t = 0
        self.e_paper_display.sleep()
        time.sleep(2)
        self.thread.join()
        self.e_paper_display.Dev_exit()

        if True or RNS.vendor.platformutils.is_android():
            if self.sub_displays.log_display != None and self.sub_displays.log_display.log_term != None:
                if self.sub_displays.log_display.log_term.log_term != None:
                    logterm_pid = self.sub_displays.log_display.log_term.log_term.pid
                    if logterm_pid != None:
                        import os, signal
                        os.kill(logterm_pid, signal.SIGKILL)

    def pthread_irq(self) :
        print("pthread running")
        while self.flag_t == 1 :
            if(self.touch_interface.digital_read(self.touch_interface.INT) == 0) :
                self.touch_interface_dev.Touch = 1
            else :
                self.touch_interface_dev.Touch = 0
        print("thread:exit")
