import os
import sys
import time
import LXMF
import nomadnet
import RNS
import traceback
import threading

from .BaseClasses import Component

class ConversationsDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.title = "Conversations"
        self.list_display = ConversationsListDisplay(self.app, self)
        self.conversation_display = SelectedConversationDisplay(self.app, self)
        self.sub_displays = [self.list_display, self.conversation_display]
        self.current_display_index = 0

    def start(self):
        current_display = self.sub_displays[self.current_display_index]
        current_display.start()
        return

class ConversationsListDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)

class SelectedConversationDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
