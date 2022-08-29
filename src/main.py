#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
This code file contains the main Application loop logic
"""

# Base imports
import faulthandler
import os
import sys

# Gtk imports
import gi
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
#pylint: enable=wrong-import-position
from gi.repository import Gtk, Gio, Gdk, Adw, GLib

# Gandiva imports
from shell.main_window import MainWindow
from core.core_loop import CoreLoop
from utils.utilities import BubbleStyle
from config import constants, settings

#--------------CLASS-SEPARATOR---------------#

class GandivaApp(Adw.Application):
  """
  ## Gandiva Application
  The main application class where the AI core and UI are implemented.
  The application is divided symantically into two parts:
  - The AI core
  - The GUI

  The two parts talk to each other exchanging information between two threads:
  - Gtk main loop
  - Core loop
  """

  def __init__(self, *args, **kwargs):
    GLib.threads_init()

    faulthandler.enable()

    super().__init__(*args, **kwargs)

    # Set applications properties
    self.props.application_id = "com.github.watsonprojects.gandiva"

    # Initialize objects
    self.main_window = None
    self.core_loop = None


  def do_startup(self):
    """
    Overrides the do_startup function of Adw.Application
    """
    Gtk.Application.do_startup(self)

    # Setup quiting app using Escape, Ctrl+Q
    quit_action = Gio.SimpleAction.new("quit", None)
    quit_action.connect("activate", self.on_quit_action)
    self.add_action(quit_action)
    self.set_accels_for_action("app.quit", ["<Ctrl>Q", "Escape"])

    # Set CSS provider
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(os.path.join(constants.DATA_PATH,
                                "application.css"))
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), css_provider, 800)


  def do_activate(self):
    """
    Overrides the do_activate function of Adw.Application
    """
    new_window_made = False
    # Allow only one window
    if self.main_window is None:
      self.main_window = MainWindow(application=self)
      # Add the current window to the application for tracking
      self.add_window(self.main_window)
      new_window_made = True

    first_launch = settings.get_first_run()
    # Allow only one core loop
    if self.core_loop is None:
      self.core_loop = CoreLoop()
      # Connect all the callbacks
      self.core_loop.connect("recognition-begin", self.ui_start_listening_mode)
      self.core_loop.connect("recognition-end", self.ui_stop_listening_mode)
      self.core_loop.connect("audio-input", self.audio_event_handler)
      self.core_loop.connect("audio-output", self.audio_out_event_handler)
      self.core_loop.connect("file-query", self.file_query_result_handler)
      self.core_loop.connect("app-query", self.app_query_result_handler)
      self.core_loop.connect("data-output", self.send_speech_bubble)
      self.core_loop.connect("speech-start", self.start_talking)
      self.core_loop.connect("speech-stop", self.stop_talking)
      self.core_loop.connect("think", self.start_thinking)
      self.core_loop.connect("suggestions-available", self.create_suggestions)
      self.core_loop.connect("need-indexing", self.show_index_toast)

      self.add_action(self.core_loop.index_action)

      self.core_loop.start(not first_launch)

    if new_window_made:
      # Connect all the callbacks
      self.main_window.connect_event("face-button-event",
                                     self.face_button_event_handler)
      self.main_window.connect_event("chat-entry-changed",
                                     self.chat_rt_query_handler)
      self.main_window.connect_event("suggestion-activated",
                                     self.suggestion_activate_handler)
      self.main_window.connect_event("chat-entry-activated",
                                     self.core_loop.query_utterance)
      self.main_window.connect_event("utterance",
                                     self.core_loop.send_utterance)
      self.main_window.connect_event(
        "voice-activation-mode-changed",
        self.core_loop.set_wakeword_engine_active)
      self.main_window.connect_event(
        "setup-complete",
        self.core_loop.initialize
      )

    self.running = True
    self.__show_ui()

    if first_launch:
      self.main_window.show_initial_setup()
      print ("First run")
    else:
      print ("Not first run")


  def __show_ui(self):
    """
    Show the window and it"s contents
    """
    self.main_window.present()


  # Event handlers
  # ---------------------------------------------------------------------------
  def on_quit_action(self, action, param):
    """
    Delete the window on app quit
    """
    if self.main_window is not None:
      self.main_window.destroy()


  def ui_start_listening_mode(self):
    self.__show_ui()
    self.main_window.start_face_animation()


  def ui_stop_listening_mode(self):
    self.main_window.stop_face_animation()


  def face_button_event_handler(self):
    self.core_loop.main_button_event()


  def chat_rt_query_handler(self, value):
    self.core_loop.realtime_query(value)


  def audio_event_handler(self, value):
    self.main_window.animate_face_rec(value)


  def audio_out_event_handler(self, value):
    self.main_window.send_talking_feedback(value)


  def file_query_result_handler(self, result):
    self.main_window.show_file_query_results(result)


  def app_query_result_handler(self, result):
    self.main_window.show_app_query_results(result)


  def suggestion_activate_handler(self, data_type, data):
    self.core_loop.activate_suggestion(data_type, data)


  def send_speech_bubble(self, data, data_type: str, from_user: bool,
                         bubble_style:BubbleStyle=None,
                         bubble_sub_class="generic"):
    self.main_window.send_speech_bubble(data, data_type, from_user,
                                        bubble_style, bubble_sub_class)


  def start_talking(self):
    self.main_window.start_talking()


  def start_thinking(self):
    self.main_window.start_thinking()


  def stop_talking(self):
    self.main_window.stop_talking()


  def create_suggestions(self, suggestions):
    self.main_window.create_suggestions(suggestions)


  def show_index_toast(self):
    if self.main_window is not None:
      self.main_window.show_toast(
        "Indexing is required for file search to work",
        "Index", "fs.index")


def main(version, app_id, datadir):
  # Initialize global configuration and constants
  constants.init(app_id=app_id, datadir=datadir, version=version)

  # Initialize global settings
  settings.init(app_id=app_id)
  app = GandivaApp()
  return app.run(sys.argv)
