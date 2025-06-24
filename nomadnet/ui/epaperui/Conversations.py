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
        self.conversations_list = ConversationsListDisplay(self.app, self)
        self.selected_conversation = SelectedConversationDisplay(self.app, self)
        self.sub_displays = [self.conversations_list, self.selected_conversation]
        self.current_display = None

    def start(self):
        return

    def render(self):
        return

class ConversationsListDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)

    def render():
        return

class SelectedConversationDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)

    def render():
        #render the display using all data attributes on self
        return