import time
import nomadnet
import textwrap
import threading
import RNS

from .BaseClasses import Component
from .EPaper import EPaperInterface
from PIL import ImageDraw


class ConversationsDisplay(Component):
    def __init__(self, app, parent):
        super().__init__(app, parent)
        self.title = "Conversations"
        self.conversation_peer = None
        self.conversation = None
        self.messages = []
        self.current_message_index = None
        self.touch_flag = False
        self.touch_thread = threading.Thread(
            daemon=False, target=self.touch_listener)

    def start(self):
        try:
            if self.parent.selected_page_index == EPaperInterface.PAGE_INDEX_CONVERSATION and self.conversation_peer:
                existing_conversations = nomadnet.Conversation.conversation_list(
                    self.app)
                source_hash = self.conversation_peer[1].hex()
                if source_hash in [c[0] for c in existing_conversations]:
                    self.conversation = nomadnet.Conversation(
                        source_hash, self.app)
                    for message in self.conversation.messages:
                        message.load()
                        self.messages.append(
                            MessageDisplay(self.app, self, message))
                    self.current_message_index = 0
                    self.messages[0].update()
                self.touch_flag = True
                self.touch_thread.start()
                self.update()

        except Exception as e:
            RNS.log("Error Conversation Display. Exception was: " +
                    str(e), RNS.LOG_ERROR)

    def update(self):
        if self.messages:
            self.messages[self.current_message_index].update()

    def touch_listener(self):
        while self.ui.app_is_running and self.touch_flag:
            if self.parent.selected_page_index != EPaperInterface.PAGE_INDEX_CONVERSATION:
                continue
            touch_x = self.ui.touch_interface_dev.X[0]
            touch_y = self.ui.touch_interface_dev.Y[0]
            touch_s = self.ui.touch_interface_dev.X[0]
            prev_touch_x = self.ui.touch_interface_old.X[0]
            prev_touch_y = self.ui.touch_interface_old.Y[0]
            prev_touch_s = self.ui.touch_interface_old.S[0]
            touch_is_new = (touch_x != prev_touch_x) and touch_s > 0
            if self.ui.screen_is_active and touch_is_new:
                if touch_x > self.ui.width-20:
                    self.current_message_index = min(
                        self.current_message_index+1, len(self.messages)-1)
                    self.update()
                elif touch_x < 20:
                    self.current_message_index = max(
                        self.current_message_index-1, 0)
                    self.update()


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
                self.ui.reset_canvas()
                draw = ImageDraw.Draw(self.ui.canvas)
                timestamp_string = time.strftime('%Y-%m-%d %H:%M:%S',
                                                 time.localtime(
                                                     self.timestamp))
                left, top, right, bottom = EPaperInterface.FONT_15.getbbox(
                    timestamp_string)
                date_width = right - left
                draw.text((self.ui.height-date_width, 0), time.strftime('%Y-%m-%d %H:%M:%S',
                                                              time.localtime(self.timestamp)), font=EPaperInterface.FONT_12, fill=0)
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
            RNS.log("Error in Message Display. Exception was: " +
                    str(e), RNS.LOG_ERROR)
