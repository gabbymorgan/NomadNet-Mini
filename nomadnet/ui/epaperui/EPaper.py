from PIL import Image, ImageFont
from .Conversations import *
import threading
from nomadnet.vendor.waveshare import epd2in13_V4
from nomadnet.vendor.waveshare import gt1151
import sys
import os
import logging

fontdir = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'epaperui/assets/fonts')
picdir = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'epaperui/assets')


class EPaperInterface():
    # For context, see documentation for Waveshare 2.13 inch touch e-paper device.
    # https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT_Manual#Raspberry_Pi

    MAX_PARTIAL_REFRESHES = 10  # Protects screen from excessive partial refresh
    MAX_REFRESH_INTERVAL = 24 * 60 * 60  # 24 hours
    TIMEOUT_INTERVAL = 60  # 10 minutes
    FONT_15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
    FONT_12 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)

    def __init__(self):
        try:
            logging.basicConfig(level=logging.DEBUG)
            self.display = epd2in13_V4.EPD()
            self.width = self.display.width
            self.height = self.display.height
            self.touch_interface = gt1151.GT1151()
            self.touch_interface_dev = gt1151.GT_Development()
            self.touch_interface_old = gt1151.GT_Development()
            self.canvas = None
            self.reset_canvas()
            self.touch_flag = True
            self.refresh_flag = True
            self.app_is_running = True
            self.screen_is_active = True
            self.should_render = False
            self.partial_refresh_counter = 0
            self.last_full_refresh = time.time()
            self.last_touch = time.time()

            self.touch_thread = threading.Thread(
                daemon=True, target=self.touch_loop)
            self.refresh_thread = threading.Thread(
                daemon=False, target=self.refresh_loop)


            self.touch_thread.start()
            self.refresh_thread.start()

            self.display.init(self.display.FULL_UPDATE)
            self.touch_interface.GT_Init()
            self.display.Clear(0xFF)

        except Exception as e:
            RNS.log(
                "An error occured in the E-Paper UI. Exception was:" + str(e), RNS.LOG_ERROR)

    def shutdown(self):
        self.touch_flag = False
        self.refresh_flag = False
        self.screen_is_active = False
        self.app_is_running = False
        self.sleep()
        self.display.Dev_exit()
        self.touch_thread.join()
        self.refresh_thread.join()

    def sleep(self):
        self.clear_screen()
        self.display.sleep()

    def awake(self):
        self.display.init(self.display.FULL_UPDATE)
        self.clear_screen()

    def clear_screen(self):
        self.display.Clear(0xFF)

    def touch_loop(self):
        while self.touch_flag:
            if (self.touch_interface.digital_read(self.touch_interface.INT) == 0):
                self.touch_interface_dev.Touch = 1
            else:
                self.touch_interface_dev.Touch = 0

    def refresh_loop(self):
        while self.refresh_flag:
            now = time.time()
            if self.should_render:
                self.should_render = False
                self.render()
            elif now - self.last_touch > self.TIMEOUT_INTERVAL:
                self.sleep()
            elif now - self.last_full_refresh > self.MAX_REFRESH_INTERVAL:
                self.clear_screen()
            time.sleep(1)

    def reset_canvas(self):
        self.canvas = Image.new('1', (self.height, self.width), 255)
        self.canvas.rotate(90)  # landscape mode


    def render(self, isFrame=False):
        if self.partial_refresh_counter >= 10 or isFrame:
            self.display.init(self.display.FULL_UPDATE)
            self.display.displayPartBaseImage(
                self.display.getbuffer(self.canvas))
            self.partial_refresh_counter = 0
        else:
            self.display.displayPartial(self.display.getbuffer(self.canvas))
            self.partial_refresh_counter += 1

    def request_render(self):
        self.should_render = True

