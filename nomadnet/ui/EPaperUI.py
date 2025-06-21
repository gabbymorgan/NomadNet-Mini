import sys
import os
import nomadnet
import RNS

from nomadnet.ui.epaperui import *
from nomadnet import NomadNetworkApp

class EPaperUI:
    def __init__(self):
        self.app = NomadNetworkApp.get_shared_instance()
        self.app.ui = self
        self.loop = None
        self.main_display = Main.MainDisplay(self, self.app)
        self.main_display.start()
        

