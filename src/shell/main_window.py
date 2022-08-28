#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
This code file contains the Main UI logic
The class MainWindow forms the well, main window of
the app. Everything else renders within it.
"""

# Gtk imports
import gi
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0') # Make sure Gtk 4 are imported
gi.require_version('Adw', '1') # Make sure Adwaita 1 are imported
#pylint: enable=wrong-import-position
from gi.repository import Gtk, Adw, GLib

# Gandiva imports
from chat_view import ChatView
from face_view import FaceView
from initial_setup import InitialSetup
from toast_widget import ToastWidget
from utils.utilities import BubbleStyle

from config import settings

#--------------CLASS-SEPARATOR---------------#

class MainWindow(Adw.ApplicationWindow):
  """
  ## Main Window
  This forms the main window of the app.
  The user can use this to interact with the AI via a GUI.
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Set Window properties
    self.set_size_request(400, 380)
    self.set_default_size(600, 380)
    self.get_style_context().add_class('rounded')
    self.set_title('Gandiva')
    self.set_hide_on_close(settings.get_voice_activation_mode())
    self.get_root().connect_after('notify', self.on_window_notify)

    # Window contents
    # This is needed in case we need to show toast notifications within the
    # app window
    self.overlay = Gtk.Overlay()
    self.toast = None

    # This forms the main switchable panel
    self.main_stack = Gtk.Stack()

    self.overlay.set_child(self.main_stack)

    # This divides the UI in two halves which either show or hide the child
    # in response to window resize events
    self.face_revealer = Adw.Flap()
    self.face_revealer.set_reveal_flap(reveal_flap=True)
    self.face_revealer.set_swipe_to_close(True)
    self.face_revealer.set_swipe_to_open(True)
    self.face_revealer.connect_after('notify', self.on_flap_notify)
    self.main_stack.add_named(self.face_revealer, 'main-view')

    # This is the "face" of the app. It provides a memetic UI
    # to gauge the AI system. This panel is placed on the left
    self.face = FaceView()
    self.face.make_ui()
    self.face.connect('toggle_face_view', self.on_toggle_face)
    self.face.connect_event('main-button-clicked',
                            self.face_main_button_click_handler)
    self.face.connect_event('voice-activation-mode-changed',
                            self.voice_activation_mode_changed)
    self.face_revealer.set_flap(flap=self.face)

    # This provides a simple chat / messaging UI similar to messaging apps
    # Users use this to "send messages" to the AI as if it were a person
    # This panel is placed on the right
    self.chat_box = ChatView()
    self.chat_box.make_ui()
    self.chat_box.show_mic_icon(False)
    self.chat_box.connect('toggle-face', self.on_toggle_face)
    self.chat_box.connect_event('chat-entry-change',
                                self.chat_entry_rt_change_handler)
    self.chat_box.connect_event('suggestion-activated',
                                self.chat_suggestion_activate_handler)
    self.chat_box.connect_event('chat-entry-activated',
                                self.send_text_utterance)
    self.chat_box.connect_event('mic-button-clicked',
                                self.face_main_button_click_handler)
    self.face_revealer.set_content(content=self.chat_box)

    # Visually separates the two halves
    self.separator = Gtk.Separator()
    self.separator.set_orientation(Gtk.Orientation.VERTICAL)
    self.face_revealer.set_separator(self.separator)

    # Sets the content of the window
    self.set_content(self.overlay)

    # Initialize all the ui event callbacks
    self.__face_event_callback = None
    self.__chat_rt_callback = None
    self.__suggestion_activate_callback = None
    self.__chat_activate_callback = None
    self.__utterance_callback = None
    self.__voice_mode_callback = None
    self.__setup_complete_callback = None


  def on_flap_notify(self, widget, param):
    """
    Handle flap events
    """
    if param.name == 'reveal-flap':
      self.chat_box.set_face_revealed(not self.face_revealer.get_folded())
      self.face.set_hexpand(not self.face_revealer.get_folded())
      self.face.show_extra_controls(self.face_revealer.get_folded())
      if self.face_revealer.get_folded():
        self.face.get_style_context().add_class('face-folded')
      else:
        self.face.get_style_context().remove_class('face-folded')


  def on_window_notify(self, widget, param):
    """
    Handle window events
    """
    if param.name in ['maximized', 'unmaximized', 'default-width']:
      self.chat_box.set_face_revealed(not self.face_revealer.get_folded())
      self.face.set_hexpand(not self.face_revealer.get_folded())
      self.face.show_extra_controls(self.face_revealer.get_folded())
      if self.face_revealer.get_folded():
        self.face.get_style_context().add_class('face-folded')
      else:
        self.face.get_style_context().remove_class('face-folded')


  def show_initial_setup(self):
    self.set_hide_on_close(False)
    self.initial_setup = InitialSetup()
    self.initial_setup.connect('send_utterance', self.send_utterance)
    self.main_stack.add_named(self.initial_setup, 'initial-setup')
    self.main_stack.set_transition_type(Gtk.StackTransitionType.NONE)
    self.main_stack.set_visible_child_name('initial-setup')
    self.main_stack.set_transition_type(Gtk.StackTransitionType.UNDER_LEFT)
    self.initial_setup.connect('complete', self.setup_complete)


  def setup_complete(self, obj):
    self.main_stack.set_visible_child_name('main-view')
    settings.set_first_run(False)
    self.set_hide_on_close(True)

    if self.__setup_complete_callback is not None:
      GLib.idle_add(self.__setup_complete_callback)


  # UI Event handlers
  def on_toggle_face(self, event, show: bool) -> bool:
    self.face_revealer.set_reveal_flap(not show)
    return not show


  def voice_activation_mode_changed(self, active):
    self.set_hide_on_close(active)
    if self.__voice_mode_callback is not None:
      self.__voice_mode_callback(active)


  def connect_event(self, event_type: str, callback):
    """
    Add callback reference to particular events.

    Supported Event Type Options:
    - `face_button_event`
    - `chat-entry-changed`
    - `suggestion-activated`
    - `chat-entry-activated`
    - `utterance`
    - `voice-activation-mode-changed`
    - `setup-complete`

    :param event_type: Type of event. Can be one of supported event type options
    :type event_type: str
    :param callback: Callback function to handle this event
    """
    if event_type == 'face-button-event':
      self.__face_event_callback = callback
    elif event_type == 'chat-entry-changed':
      self.__chat_rt_callback = callback
    elif event_type == 'suggestion-activated':
      self.__suggestion_activate_callback = callback
    elif event_type == 'chat-entry-activated':
      self.__chat_activate_callback = callback
    elif event_type == 'utterance':
      self.__utterance_callback = callback
    elif event_type == 'voice-activation-mode-changed':
      self.__voice_mode_callback = callback
    elif event_type == 'setup-complete':
      self.__setup_complete_callback = callback


  def send_utterance(self, obj, utterance):
    if self.__utterance_callback is not None:
      self.__utterance_callback(utterance)

    return False


  def face_main_button_click_handler(self):
    if self.__face_event_callback is not None:
      self.__face_event_callback()


  def chat_entry_rt_change_handler(self, value):
    if self.__chat_rt_callback is not None:
      self.__chat_rt_callback(value)


  def chat_suggestion_activate_handler(self, data_type, data):
    if self.__suggestion_activate_callback is not None:
      self.__suggestion_activate_callback(data_type, data)


  def animate_face_rec(self, value):
    self.face.light_ring_animate_recognition(value)


  def start_face_animation(self):
    self.face.light_ring_animation_begin()


  def stop_face_animation(self):
    self.face.light_ring_animation_end()


  def show_file_query_results(self, results):
    self.chat_box.show_file_search_suggestions(results)


  def show_app_query_results(self, results):
    self.chat_box.show_app_search_suggestions(results)


  def send_talking_feedback(self, buffer):
    self.face.set_talking_audio(buffer)


  def start_talking(self):
    self.face.stop_thinking()
    self.face.light_ring_animation_begin()
    self.face.start_talking()


  def stop_talking(self):
    self.face.stop_talking()
    self.face.light_ring_animation_end()


  def start_thinking(self):
    self.face.start_thinking()


  def send_speech_bubble(self, data, data_type: str, from_user=True,
                         bubble_style:BubbleStyle=None,
                         bubble_sub_class='generic'):
    self.chat_box.send_speech_bubble(data, data_type, from_user,
                                     bubble_style, bubble_sub_class)


  def send_text_utterance(self, text: str):
    if self.__chat_activate_callback is not None:
      self.__chat_activate_callback(text)


  def create_suggestions(self, suggestions):
    self.chat_box.create_suggestions(suggestions)


  def show_toast(self, message:str, action_name='', action=''):
    if self.toast is not None:
      self.overlay.remove_overlay(self.toast)
    self.toast = ToastWidget()
    self.toast.set_data(message, self.get_application(), action_name, action)
    self.overlay.add_overlay(self.toast)
    self.overlay.set_measure_overlay(self.toast, False)
