#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
This code implements the chat interface
using which the user can interact with the AI
"""

# Base imports
import gi
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
#pylint: enable=wrong-import-position
from gi.repository import Gtk, Adw, GObject, GLib

# Gandiva imports
from suggestion_button import SuggestionButton
from chat_bubble import ChatBubble, ChatBubbleSearch
from utils.utilities import BubbleStyle

#--------------CLASS-SEPARATOR---------------#

class ChatView(Gtk.Box):
  """
  This provides a chat interface similar to
  instant messaging apps.
  """

  MAX_BUBBLES = 24

  # GLib signals
  __gsignals__ = {
    'toggle-face': (GObject.SIGNAL_RUN_FIRST, bool,
            (bool,))
  }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Callbacks
    self.__realtime_text_input_callback = None
    self.__suggestion_activate_callback = None
    self.__input_activate_callback = None
    self.__start_listening_callback = None

    # Chat UI params
    self.__number_of_bubbles = 0


  def make_ui(self):
    """
    Prepare UI.
    """
    self.face_revealed = True
    self.set_hexpand(True)
    self.set_orientation(Gtk.Orientation.VERTICAL)

    # Make the custom title bar of the window
    self.headerbar = Adw.HeaderBar()
    self.headerbar.get_style_context().add_class('flat')
    self.append(self.headerbar)
    self.set_size_request(280, 160)

    self.show_face_button = Gtk.ToggleButton()
    self.show_face_button.set_active(True)
    self.show_face_button.set_icon_name('view-dual-symbolic')
    self.show_face_button.connect('clicked', self.toggle_revealer)
    self.headerbar.pack_start(self.show_face_button)

    self.scrolled_window = Gtk.ScrolledWindow()
    self.scrolled_window.set_size_request(200, 200)
    self.scrolled_window.get_style_context().add_class('chat-window')
    self.scrolled_window.set_vexpand(True)
    self.append(self.scrolled_window)

    self.chat_box = Gtk.Box()
    self.chat_box.set_orientation(Gtk.Orientation.VERTICAL)
    self.chat_box.set_valign(Gtk.Align.END)
    self.scrolled_window.set_child(self.chat_box)

    self.suggestion_box = Gtk.ScrolledWindow()
    self.suggestion_box.set_size_request(100, 52)
    self.append(self.suggestion_box)

    self.suggestion_stack = Gtk.Stack()
    self.suggestion_stack.set_transition_type(
        Gtk.StackTransitionType.SLIDE_UP_DOWN)
    self.suggestion_box.set_child(self.suggestion_stack)

    self.generic_suggestion_box = Gtk.Box()
    self.generic_suggestion_box.set_margin_start(8)
    self.generic_suggestion_box.set_margin_end(8)
    self.generic_suggestion_box.set_spacing(6)
    self.suggestion_stack.add_named(self.generic_suggestion_box,
        'generic-suggestions')

    self.file_and_app_suggestion_box = Gtk.Box()
    self.file_and_app_suggestion_box.set_spacing(6)
    self.file_and_app_suggestion_box.set_margin_start(8)
    self.file_and_app_suggestion_box.set_margin_end(8)
    self.suggestion_stack.add_named(self.file_and_app_suggestion_box,
        'file-app-suggestions')
    self.app_suggestion_box = Gtk.Box()
    self.app_suggestion_box.set_spacing(6)
    self.file_and_app_suggestion_box.append(self.app_suggestion_box)
    self.file_suggestion_box = Gtk.Box()
    self.file_suggestion_box.set_spacing(6)
    self.text_suggestion_buttons = []
    self.__file_suggestion_buttons = []
    self.__app_suggestion_buttons = []
    self.file_and_app_suggestion_box.append(self.file_suggestion_box)

    self.chat_entry = Gtk.Entry()
    self.chat_entry.set_margin_start(8)
    self.chat_entry.set_margin_end(8)
    self.chat_entry.set_margin_bottom(8)
    self.chat_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
        'audio-input-microphone-symbolic')
    self.chat_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
        'mail-send-symbolic')
    self.chat_entry.connect('changed', self.__handle_input_realtime)
    self.chat_entry.connect('activate', self.__handle_input_activated)
    self.chat_entry.connect('icon_release', self.__handle_input_icon_clicked)
    self.append(self.chat_entry)

    GLib.timeout_add(1000, self.grab_entry_focus)


  def grab_entry_focus(self):
    if not self.chat_entry.is_focus():
      self.chat_entry.grab_focus_without_selecting()

    return True


  def show_mic_icon(self, show: bool):
    self.chat_entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, show)


  def toggle_revealer(self, event):
    self.set_face_revealed(self.emit('toggle-face', self.face_revealed))


  def set_face_revealed(self, revealed: bool):
    self.face_revealed = revealed
    self.show_face_button.set_active(revealed)
    self.show_mic_icon(not revealed)


  def __handle_input_realtime(self, obj):
    if self.__realtime_text_input_callback is not None:
      self.__realtime_text_input_callback(self.chat_entry.get_text())
    if len(self.chat_entry.get_text()) == 0:
      self.suggestion_stack.set_visible_child_name('generic-suggestions')


  def __handle_input_activated(self, obj):
    if self.__input_activate_callback is not None:
      self.__input_activate_callback(self.chat_entry.get_text())

    self.chat_entry.set_text('')


  def __handle_input_icon_clicked(self, obj, icon_pos):
    if icon_pos == Gtk.EntryIconPosition.SECONDARY:
      self.__handle_input_activated(None)
    elif self.__start_listening_callback is not None:
      self.__start_listening_callback()


  def __scroll_to_bottom(self):
    adj = self.scrolled_window.get_vadjustment()
    adj.set_value(adj.get_upper() - adj.get_page_size() + 20)
    pass


  def connect_event(self, event_type: str, callback):
    if event_type == 'chat-entry-change':
      self.__realtime_text_input_callback = callback
    elif event_type == 'suggestion-activated':
      self.__suggestion_activate_callback = callback
    elif event_type == 'chat-entry-activated':
      self.__input_activate_callback = callback
    elif event_type == 'mic-button-clicked':
      self.__start_listening_callback = callback


  def show_file_search_suggestions(self, results):
    for b in self.__file_suggestion_buttons:
      self.file_suggestion_box.remove(b)

    self.__file_suggestion_buttons.clear()

    for r in results:
      suggest_button = SuggestionButton()
      suggest_button.set_button_details('file', data=r)
      self.__file_suggestion_buttons += [ suggest_button ]
      self.file_suggestion_box.append(suggest_button)
      suggest_button.connect_event('clicked',
        self.__suggestion_activate_handler)

    if len(results) > 0:
      self.suggestion_stack.set_visible_child_name('file-app-suggestions')

  def show_app_search_suggestions(self, results):
    for b in self.__app_suggestion_buttons:
      self.app_suggestion_box.remove(b)

    self.__app_suggestion_buttons.clear()

    for r in results:
      suggest_button = SuggestionButton()
      suggest_button.set_button_details('app', data=r)
      self.__app_suggestion_buttons += [ suggest_button ]
      self.app_suggestion_box.append(suggest_button)
      suggest_button.connect_event('clicked',
        self.__suggestion_activate_handler)

    if len(results) > 0:
      self.suggestion_stack.set_visible_child_name('file-app-suggestions')


  def __suggestion_activate_handler(self, data_type, data):
    if self.__suggestion_activate_callback is not None:
      self.__suggestion_activate_callback(data_type, data)


  def send_speech_bubble(self, data, data_type='text', from_user=True,
    bubble_style:BubbleStyle = None, bubble_sub_class='generic'):
    if self.__number_of_bubbles >= ChatView.MAX_BUBBLES:
      self.chat_box.remove(self.chat_box.get_first_child())
    self.__number_of_bubbles += 1
    if bubble_sub_class.startswith('search'):
      bubble = ChatBubbleSearch()
      bubble.set_category(bubble_sub_class[7:])
    else:
      bubble = ChatBubble()
      if bubble_style is None:
        if from_user:
          bubble_style = BubbleStyle('#555761', '#ECECEC', '', '#AEAEAE')
        else:
          bubble_style = BubbleStyle('#0D52BF', '#E1EDFB', '', '#729AC4')

    bubble.set_content(data, bubble_style, from_user)

    self.chat_box.append(bubble)
    bubble.animate_bubble()
    GLib.timeout_add(100, self.__scroll_to_bottom)


  def create_suggestions(self, suggestions):
    if len(self.text_suggestion_buttons) > 0:
      for button in self.text_suggestion_buttons:
        self.generic_suggestion_box.remove(button)

    self.text_suggestion_buttons.clear()

    for suggestion in suggestions:
      suggest_button = SuggestionButton()
      suggest_button.set_button_details('text', suggestion)
      suggest_button.connect_event('clicked',
        self.__suggestion_activate_handler)
      self.text_suggestion_buttons += [suggest_button]
      self.generic_suggestion_box.append(suggest_button)
