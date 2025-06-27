import time
import nomadnet
import textwrap
import threading
import RNS
import arrow

from .BaseClasses import Component
from .EPaper import EPaperInterface
from PIL import ImageDraw


class ConversationDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.title = "Conversation"
        self.conversation_peer = None
        self.conversation = None
        self.current_message_index = 0
        self.messages = []
        self.touch_thread = threading.Thread(
            daemon=True, target=self.touch_listener)

    def start(self):
        self.touch_thread.start()
        self.update()

    def update(self):
        try:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_CONVERSATION and self.conversation_peer:
                self.ui.detect_screen_interaction()
                existing_conversations = nomadnet.Conversation.conversation_list(
                    self.app)
                source_hash = self.conversation_peer[1].hex()
                self.messages = []
                if source_hash in [c[0] for c in existing_conversations]:
                    self.conversation = nomadnet.Conversation(
                        source_hash, self.app)
                    for message in self.conversation.messages:
                        message.load()
                        self.messages.append(
                            MessageDisplay(self.app, self, message))
                self.messages.sort(key=lambda m: m.timestamp, reverse=True)
                self.ui.reset_canvas()
                draw = ImageDraw.Draw(self.ui.canvas)
                draw.text((0, 0), f"{self.conversation_peer[2].decode(encoding='utf-8', errors='strict')} ({self.conversation_peer[1].hex()[-6:]})",
                          font=EPaperInterface.FONT_12)
                draw.text((0, 100), "back",
                          font=EPaperInterface.FONT_15, fill=0)
                if len(self.messages) > 0:
                    self.messages[self.current_message_index].update()
                else:
                    draw.text((50, 50), "No messages?",
                              font=EPaperInterface.FONT_15, fill=0)
                self.ui.request_render()

        except Exception as e:
            RNS.log("Error in update method of ConversationDisplay. Exception was: " +
                    str(e), RNS.LOG_ERROR)

    def touch_listener(self):
        while self.ui.app_is_running:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_CONVERSATION:
                self.ui.detect_screen_interaction()
                if self.ui.screen_is_active and self.ui.did_swipe:
                    if self.ui.swipe_direction == EPaperInterface.SWIPE_RIGHT:
                        self.current_message_index = min(
                            self.current_message_index+1, len(self.messages)-1)
                        self.update()
                    elif self.ui.swipe_direction == EPaperInterface.SWIPE_LEFT:
                        self.current_message_index = max(
                            self.current_message_index-1, 0)
                        self.update()
                elif self.ui.screen_is_active and self.ui.did_tap:
                    if self.ui.tap_x > self.ui.width-40 and self.ui.tap_y > self.ui.height-40:
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_NETWORK
                        self.current_message_index = 0
                        self.parent.update()


class MessageDisplay(Component):
    def __init__(self, app, parent, message):
        super().__init__(app, parent)
        self.timestamp = message.timestamp
        self.content = message.get_content()
        self.file_path = message.file_path

    def update(self):
        try:
            current_message = self.parent.messages[self.parent.current_message_index]
            if self.file_path == current_message.file_path:
                draw = ImageDraw.Draw(self.ui.canvas)
                timestamp = arrow.get(self.timestamp)
                datetime_string = f'{timestamp.humanize()} at {timestamp.format(fmt="h:mma", locale="en-us")}'
                left, top, right, bottom = EPaperInterface.FONT_15.getbbox(datetime_string)
                date_width = right - left
                draw.text((date_width, 0), datetime_string, font=EPaperInterface.FONT_12, fill=0)
                lines = textwrap.wrap(self.content, width=32)
                text_y_position = 20
                for line in lines:
                    left, top, right, bottom = EPaperInterface.FONT_15.getbbox(
                        line)
                    text_width = right - left
                    text_height = bottom - top
                    draw.text(
                        ((self.ui.height-text_width)//2, text_y_position), line, font=EPaperInterface.FONT_15, fill=0)
                    text_y_position += text_height
                self.ui.request_render()

        except Exception as e:
            RNS.log("Error in update method of MessageDisplay. Exception was: " +
                    str(e), RNS.LOG_ERROR)
