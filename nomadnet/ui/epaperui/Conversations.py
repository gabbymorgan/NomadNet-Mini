import os
import sys
import time
import LXMF
import nomadnet
import RNS
import logging
import traceback
import threading


class ConversationsDisplay():
    def __init__(self, app):
        self.app = app
        self.selected_conversation = None


    def display_list(self):
        self.selected_conversation = None
        self.update_conversation_list()

    def display_conversation(self, source_hash=None):
        self.selected_conversation = source_hash
        self.update_conversation_list()

    def update_conversation_list():
        return

class ConversationsList():
    def __init__(self, parent):
        self.selected_conversation = parent.selected_conversation

class SelectedConversation():
  
    def __init__(self, messages):
        self.messages = messages

    def update_display():
        #render the display using all data attributes on self
        return