from PIL import ImageDraw, Image
from .EPaper import EPaperInterface
from .BaseClasses import Component
import time
import os
import nomadnet
import textwrap
import threading
import RNS
import LXMF
import arrow
import readchar
from pytablericons import TablerIcons, OutlineIcon

picdir = os.path.join(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))), 'epaperui/assets')


class ConversationDisplay(Component):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = "Conversation"
        self.conversation_peer = None
        self.conversation = None
        self.current_message_index = 0
        self.messages = []
        self.touch_thread = threading.Thread(
            daemon=True, target=self.touch_listener)
        self.refresh_thread = threading.Thread(
            daemon=True, target=self.refresh_loop)

    def start(self):
        self.touch_thread.start()
        self.refresh_thread.start()
        self.update()

    def update(self):
        try:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_CONVERSATION and self.conversation_peer:
                existing_conversations = nomadnet.Conversation.conversation_list(
                    self.app)
                source_hash = self.conversation_peer[1].hex()
                self.messages = []
                if source_hash in [c[0] for c in existing_conversations]:
                    self.conversation = nomadnet.Conversation(
                        source_hash, self.app)
                    if self.app.conversation_is_unread(source_hash):
                        self.app.mark_conversation_read(source_hash)
                    for message in self.conversation.messages:
                        message.load()
                        self.messages.append(
                            MessageDisplay(self, message))
                self.messages.sort(
                    key=lambda m: m.message.timestamp, reverse=True)
                self.ui.reset_canvas()
                background = Image.open(os.path.join(
                    picdir, 'conversation-display.bmp'))
                self.ui.canvas.paste(background, (0, 0))
                draw = ImageDraw.Draw(self.ui.canvas)
                draw.text((0, 0), self.title, font=EPaperInterface.FONT_12)
                conversation_peer_name = f"{self.conversation_peer[2].decode(encoding='utf-8', errors='strict')} ({self.conversation_peer[1].hex()[-6:]})"
                alignment_data = self.ui.get_alignment(
                    conversation_peer_name, EPaperInterface.FONT_12)
                draw.text((alignment_data["right_align"], 0), conversation_peer_name,
                          font=EPaperInterface.FONT_12)
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
                    elif self.ui.tap_x > self.ui.width-40 and self.ui.tap_y < 40:
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_COMPOSE
                        self.parent.update()
            time.sleep(0.02)

    def refresh_loop(self):
        while self.ui.app_is_running:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_CONVERSATION and self.conversation_peer:
                if self.app.conversation_is_unread(self.conversation_peer[1].hex()):
                    self.update()
            time.sleep(1)

    def get_state_string(self, message: LXMF.LXMessage):
        if self.app.lxmf_destination.hash == message.lxm.source_hash:
            state = message.get_state()
            state_string = ""
            if state == LXMF.LXMessage.DELIVERED:
                state_string = "delivered"
            elif state == LXMF.LXMessage.FAILED:
                state_string = "failed"
            elif state == LXMF.LXMessage.SENDING:
                state_string = "sending"
            elif state == LXMF.LXMessage.OUTBOUND:
                state_string = "outbound"
            elif message.lxm.method == LXMF.LXMessage.PROPAGATED and state == LXMF.LXMessage.SENT:
                state_string = "on propagation"
            elif message.lxm.method == LXMF.LXMessage.PAPER and state == LXMF.LXMessage.PAPER:
                state_string = "paper"
            elif state == LXMF.LXMessage.SENT:
                state_string = "sent"
            else:
                state_string = "sent"
        else:
            state_string = "received"

        return state_string


class MessageDisplay(Component):
    def __init__(self, parent, message: LXMF.LXMessage):
        super().__init__(parent)
        self.message = message

    def update(self):
        try:
            current_message = self.parent.messages[self.parent.current_message_index]
            if self.message.file_path == current_message.message.file_path:
                draw = ImageDraw.Draw(self.ui.canvas)
                lines = textwrap.wrap(self.message.get_content(), width=32)
                text_y_position = 20
                for line in lines:
                    left, top, right, bottom = EPaperInterface.FONT_15.getbbox(
                        line)
                    text_width = right - left
                    text_height = bottom - top
                    draw.text(
                        ((self.ui.height-text_width)//2, text_y_position), line, font=EPaperInterface.FONT_15, fill=0)
                    text_y_position += text_height
                state = self.parent.get_state_string(self.message)
                timestamp = arrow.get(self.message.timestamp)
                bottom_text = f'{state} {timestamp.humanize()} at {timestamp.to("local").format(fmt="h:mma", locale="en-us")}'
                centered = self.ui.get_alignment(
                    bottom_text, EPaperInterface.FONT_12)["center_align"]
                draw.text((centered, 100), bottom_text,
                          font=EPaperInterface.FONT_12, fill=0)
                self.ui.request_render()

        except Exception as e:
            RNS.log("Error in update method of MessageDisplay. Exception was: " +
                    str(e), RNS.LOG_ERROR)


class ComposeDisplay(Component):
    def __init__(self, parent):
        super().__init__(parent)
        self.char_buffer = ""
        self.keyboard_thread = threading.Thread(
            daemon=True, target=self.keyboard_listener)
        self.touch_thread = threading.Thread(
            daemon=True, target=self.touch_listener)

    def start(self):
        self.keyboard_thread.start()
        self.touch_thread.start()
        self.update()

    def update(self):
        if self.parent.current_page_index != EPaperInterface.PAGE_INDEX_COMPOSE:
            return
        self.ui.reset_canvas()
        background = Image.open(os.path.join(
            picdir, 'compose-display.bmp'))
        self.ui.canvas.paste(background, (0, 0))
        draw = ImageDraw.Draw(self.ui.canvas)
        lines = textwrap.wrap(self.char_buffer, width=32)[-5:]
        text_y_position = 10
        for line in lines:
            left, top, right, bottom = EPaperInterface.FONT_15.getbbox(
                line)
            text_height = bottom - top
            draw.text((10, text_y_position), line,
                      font=EPaperInterface.FONT_15, fill=0)
            text_y_position += text_height
        self.ui.request_render()

    def keyboard_listener(self):
        while self.ui.app_is_running:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_COMPOSE:
                incoming_char = readchar.readkey()
                if incoming_char == readchar.key.BACKSPACE:
                    self.char_buffer = self.char_buffer[0:-1]
                else:
                    self.char_buffer += incoming_char
                if incoming_char:
                    self.update()
            else:
                time.sleep(1)

    def touch_listener(self):
        while self.ui.app_is_running:
            if self.parent.current_page_index == EPaperInterface.PAGE_INDEX_COMPOSE:
                self.ui.detect_screen_interaction()
                if self.ui.screen_is_active and self.ui.did_tap:
                    if self.ui.tap_x > self.ui.width-40 and self.ui.tap_y > self.ui.height-40:
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_CONVERSATION
                        self.current_message_index = 0
                        self.parent.update()
                    elif self.ui.tap_x > self.ui.width-40 and self.ui.tap_y < 40:
                        if self.parent.conversation_display.conversation:
                            self.parent.conversation_display.conversation.send(
                                self.char_buffer)
                        else:
                            peer_hash = self.parent.conversation_display.conversation_peer[1].hex()
                            new_conversation = nomadnet.Conversation(peer_hash, nomadnet.NomadNetworkApp.get_shared_instance(), initiator=True)
                            new_conversation.send(self.char_buffer)
                        self.parent.current_page_index = EPaperInterface.PAGE_INDEX_CONVERSATION
                        self.char_buffer = ""
                        self.parent.update()
            time.sleep(0.02)
