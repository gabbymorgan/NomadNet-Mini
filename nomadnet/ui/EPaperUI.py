import RNS

from nomadnet.ui.epaperui import *
from nomadnet import NomadNetworkApp

class EPaperUI:
    def __init__(self):
        try:
            self.app = NomadNetworkApp.get_shared_instance()
            self.app.ui = {}
            self.main_display = Main.MainDisplay()
        except Exception as e:
            RNS.log(f"Error in EPaperUI. Exception: {e}", RNS.LOG_ERROR)