#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This file implements the main AI loop, which consists of listening for input,
processing it (act on it), when input is available, sending some response
back to the user and going back to listening and so on…
"""

#pylint: disable=unused-argument
#pylint: disable=consider-using-f-string

# Base imports
import _thread
import time
import subprocess
import random
from gi.repository import GLib, Gio

# Gandiva imports
from wake_word_engine import WakeWordEngine
from stt import SpeechTotext
from tts import TextToSpeech
from file_system_search import FileSystemSearch
from app_search import AppSearch
from inference_engine import InferenceEngine
from config import settings
from utils import utilities
from utils.utilities import BubbleStyle

#--------------CLASS-SEPARATOR---------------#

class CoreLoop():
  """
  ## AI Core loop
  This implements the main AI loop, which consists of the following steps:
  - Listen for input
  - When input is available, consume it (act on it)
  - Send some response back to the user
  - Go back to listening and so on…
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Callbacks
    self.__recognition_begin_callback = None
    self.__recognition_end_callback = None
    self.__audio_callback = None
    self.__audio_output_callback = None
    self.__file_found_callback = None
    self.__data_output_callback = None
    self.__speech_output_start_callback = None
    self.__speech_output_stop_callback = None
    self.__thinking_callback = None
    self.__suggestions_available_callback = None
    self.__notify_index_callback = None

    # Filesystem search
    self.__fs_search = FileSystemSearch()

    # App search
    self.__app_search = AppSearch()

    # Inference Engine or the brain of the app
    # Infers the answer or action based on skills
    # (elementary abilities added to the app)
    self.__inference_engine = InferenceEngine()
    self.__inference_engine.connect_portal_error_callback(
        self.handle_portal_error)

    # VOSK Speech recognition system
    self.stt = SpeechTotext()
    self.stt.connect("audio", self.handle_audio_input)
    self.stt.connect("recognition-complete", self.query_utterance)

    # Wakeword or "hot word" engine
    self.wake_word_engine = WakeWordEngine()
    self.wake_word_engine.connect(self.start_listening)
    if settings.get_voice_activation_mode() and not settings.get_first_run():
      self.wake_word_engine.start()

    # Speech drive
    self.tts = TextToSpeech()
    self.tts.connect("audio", self.handle_audio_output)

    # Thread inputs
    self.__alive = True
    self.__live_query = ""
    self.__query = ""
    self.__utterance = ""
    self.__system_update = False
    self.__system_index = False
    self.__system_update_skills = False
    self.__initialize_core_loop = False

    self._state = "idle"

    # Setup index action
    self.index_action = Gio.SimpleAction.new("fs.index", None)
    self.index_action.connect("activate", self.queue_index)


  def start(self, update:bool):
    # Start the main loop thread
    _thread.start_new_thread(self.__main_loop, (update,))


  def __main_loop(self, update:bool):
    """
    The main loop thread
    """
    self.__system_update = False
    if update:
      self.initialize()

    # Start main loop
    while self.__alive:
      # Handle system queries
      if self.__initialize_core_loop:
        self.__initialize_core_loop = False
        time.sleep(1)
        if self.__thinking_callback is not None:
          self.__thinking_callback()

        self.stt.initialize()
        self.wake_word_engine.initialize()
        self.__app_search.discover()
        example_queries = self.__inference_engine.update()
        if len(example_queries) > 0 \
          and self.__suggestions_available_callback is not None:
          self.__suggestions_available_callback(example_queries)
        # Let user know that the AI has analysed all the skills and is ready
        self.__send_response("Hello! How may I help you?", "text", False)
        self.start_audio_output()
        self.tts.speak("Hello! I am Gandiva! How may I help you?")
        self.stop_audio_output()

      elif self.__system_update:
        self.__system_update = False
        self.__send_response("Updating AI engine", "text", False)
        self.start_audio_output()
        self.tts.speak("Updating AI engine")
        self.stop_audio_output()
        if self.__thinking_callback is not None:
          self.__thinking_callback()
        print("[CoreLoop] Updating Inference Engine…")
        example_queries = self.__inference_engine.update()
        if len(example_queries) > 0 \
          and self.__suggestions_available_callback is not None:
          self.__suggestions_available_callback(example_queries)
        print("[CoreLoop] Indexing files…")
        self.__fs_search.index_files(True)
        self.__send_response("AI engine updated", "text", False)
        self.start_audio_output()
        self.tts.speak("AI engine updated")
        self.stop_audio_output()

      elif self.__system_index:
        self.__send_response("Indexing file system search", "text", False)
        self.start_audio_output()
        self.tts.speak("indexing file system search")
        self.stop_audio_output()
        if self.__thinking_callback is not None:
          self.__thinking_callback()
        time.sleep(1)
        self.__system_index = False
        self.__fs_search.index_files(True)
        self.__send_response("Indexing complete!", "text", False)
        self.start_audio_output()
        self.tts.speak("indexing complete")
        self.stop_audio_output()

      elif self.__system_update_skills:
        self.__system_update_skills = False
        self.__send_response("Relearning skills", "text", False)
        self.start_audio_output()
        self.tts.speak("Relearning skills")
        self.stop_audio_output()
        if self.__thinking_callback is not None:
          self.__thinking_callback()
        time.sleep(1)
        example_queries = self.__inference_engine.update_skills()
        if len(example_queries) > 0 \
          and self.__suggestions_available_callback is not None:
          self.__suggestions_available_callback(example_queries)
        self.__send_response("I am ready!", "text", False)
        self.start_audio_output()
        self.tts.speak("Skill set updated. I am ready")
        self.stop_audio_output()

      elif len(self.__live_query) > 0:
        app_results = self.__app_search.search(self.__live_query, False, True)
        if self.__app_found_callback is not None:
          app_found_lamda = lambda : self.__app_found_callback(app_results)
          GLib.idle_add(app_found_lamda)
        file_results, searched = self.__fs_search.search_file(self.__live_query)
        if not searched:
          self.__notify_index_callback()
        if self.__file_found_callback is not None:
          file_found_lamda = lambda : self.__file_found_callback(file_results)
          GLib.idle_add(file_found_lamda)
        self.__live_query = ""

      # Handle user queries
      elif len(self.__query) > 0:
        # Infer answer or action from the query
        if self.__thinking_callback is not None:
          self.__thinking_callback()
        self.wake_word_engine.stop()
        results = self.__inference_engine.infer(self.__query)
        self.__query = ""
        for result in results:
          if result["type"] == "internal-action":
            time.sleep(0.5)
            if result["action"] == "app-launch":
              app_result = self.__app_search.search(result["value"],
                True, False)
              try:
                if app_result.launch():
                  utterance = ("Opening " if random.random() > 0.5 \
                    else "Here's ") + app_result.get_name()
                  widget = utilities.get_app_bubble(app_result)
                  self.__send_response(widget, "widget", False)
                else:
                  utterance = "It seems the app failed to start up."
                  self.__send_response(utterance, "text", False)
              except Exception as e:
                utterance = "That's odd, looks like I can't launch this app"
                self.__send_response(utterance, "text", False)
                print(e)

              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "app-search-keyword":
              app_results = self.__app_search.search(result["value"],
                False, False)
              if app_results is not None and len(app_results) > 0:
                if len(app_results) == 10:
                  utterance = "Here's the top ten results"
                else:
                  utterance = "Here's the search results"
                self.__send_response(app_results, "list", False,
                  None, "search-apps-generic")
              else:
                utterance = "I did not find any such app"
                self.__send_response(utterance, "text", False)

              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "app-search-category":
              app_results = self.__app_search.search(result["value"], False,
                False, True)
              if app_results is not None and len(app_results) > 0:
                utterance = "Here's the apps in '%s' category" \
                  % result["value"]
                self.__send_response(app_results, "list", False,
                  None, "search-apps-generic")
              else:
                utterance = "I did not find any apps in the '%s' category" \
                  % result["value"]
                self.__send_response(utterance, "text", False)

              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "app-search-games":
              app_results = self.__app_search.search("Game", False, False, True)
              if app_results is not None and len(app_results) > 0:
                utterance = "Here's the games. It's play-time I guess?"
                self.__send_response(app_results, "list", False,
                  None, "search-apps-games")
              else:
                utterance = "I did not find any games installed"
                self.__send_response(utterance, "text", False)

              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "app-search-accessories":
              app_results = self.__app_search.search("Accessories",
                False, False, True)
              if app_results is None or len(app_results) == 0:
                app_results = self.__app_search.search("Utility",
                  False, False, True)

              if app_results is not None and len(app_results) > 0:
                utterance = "Here's the accessories"
                self.__send_response(app_results, "list", False,
                  None, "search-apps-accessories")
              else:
                utterance = "I did not find any accessory apps"
                self.__send_response(utterance, "text", False)

              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "file-search-keyword":
              file_results, searched = self.__fs_search.search_file(
                result["value"], True)
              if not searched:
                self.__notify_index_callback()
                utterance = "I am afraid, I'll need to index the files before \
                  searching. You can command me to do so by \
                  typing 'system run index'"
              elif file_results is None or len(file_results) == 0:
                utterance = "No files or folders were found with those keywords"
              else:
                utterance = "I have found %d item%s" % (len(file_results),
                  "" if len(file_results) == 1 else "s")
                self.__send_response(file_results, "list", False, None,
                  "search-files-generic")

              self.__send_response(utterance, "text", False)
              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
            elif result["action"] == "file-open-library":
              utterance = "Opening %s library" % result["value"].lower()
              self.__send_response(utterance, "text", False)
              library_uri = GLib.get_home_dir()
              if result["value"].startswith("DOCUMENT"):
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_DOCUMENTS)
              elif result["value"] == "DESKTOP":
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_DESKTOP)
              elif result["value"].startswith("DOWNLOAD"):
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_DOWNLOAD)
              elif result["value"] in [
                  "PICTURE", "PICTURES", "PHOTO", "PHOTOS", "IMAGE", "IMAGES"
                ]:
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_PICTURES)
              elif result["value"] in ["MUSIC", "AUDIO"]:
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_MUSIC)
              elif result["value"].startswith("VIDEO"):
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_VIDEOS)
              elif result["value"] == "TEMPLATES":
                library_uri = GLib.get_user_special_dir(
                  GLib.UserDirectory.DIRECTORY_TEMPLATES)

              subprocess.call(("xdg-open", library_uri))
              self.start_audio_output()
              self.tts.speak(utterance)
              self.stop_audio_output()
          else:
            self.__send_response(result["value"], result["type"], False,
              result["style"] if "style" in result else None)
            if result["type"] == "text" and "utterance" not in result.keys():
              self.start_audio_output()
              self.tts.speak(result["value"])
              self.stop_audio_output()
            elif "utterance" in result.keys():
              self.start_audio_output()
              self.tts.speak(result["utterance"])
              self.stop_audio_output()
            time.sleep(0.2)
        if settings.get_voice_activation_mode():
          self.wake_word_engine.start()
      elif len(self.__utterance) > 0:
        self.tts.speak(self.__utterance)
        self.__utterance = ""
      time.sleep(0.5)


  def initialize(self):
    """
    Initialize the core loop
    """
    print("[CoreLoop] Initializing…")
    self.__initialize_core_loop = True


  def __send_response(self, data, data_type:str, direction:bool,
      bubble_style:BubbleStyle=None, bubble_sub_class="generic"):
    """
    Sets the response variables and sends when Gtk thread is idle
    """
    response_lamda = lambda : self.__data_output_callback(data, data_type,
      direction, bubble_style, bubble_sub_class)
    GLib.idle_add(response_lamda)


  def start_listening(self):
    """
    Start actively listening for voice inputs
    """

    print("Hello! What can I do for you?")
    if self.__recognition_begin_callback is not None:
      self.__recognition_begin_callback()
    self.wake_word_engine.stop()
    self._state = "listening"
    self.stt.start_listening()
    return True


  def stop_listening(self):
    """
    Stop the listening thread
    """
    self._state = "thinking"
    self.stt.stop_listening()


  def start_audio_output(self):
    if self.__speech_output_start_callback is not None:
      self._state = "speaking"
      self.__speech_output_start_callback()


  def stop_audio_output(self):
    if self.__speech_output_stop_callback is not None:
      self._state = "idle"
      self.__speech_output_stop_callback()


  def set_wakeword_engine_active(self, active:bool):
    if active:
      self.wake_word_engine.start()
    else:
      self.wake_word_engine.stop()


  def main_button_event(self):
    if self._state == "idle":
      self.start_listening()
    elif self._state == "listening":
      self.stop_listening()
      if self.__recognition_end_callback is not None:
        self.__recognition_end_callback()
    elif self._state == "speaking":
      self.tts.stop()
      self.stop_audio_output()


  # Event handlers
  # ----------------------------------------------------------------------------
  def handle_audio_input(self, value):
    if self.__audio_callback is not None:
      self.__audio_callback(value)


  def handle_audio_output(self, buffer):
    if self.__audio_output_callback is not None:
      self.__audio_output_callback(buffer)


  def handle_portal_error(self, message):
    self.__send_response(message, "text", False)


  def connect(self, event_type, callback):
    """
    Add callback reference to particular events.

    Supported Event Type Options:
    - `recognition-begin`
    - `recognition-end`
    - `audio-input`
    - `audio-output`
    - `file-query`
    - `data-output`
    - `speech-start`
    - `speech-stop`
    - `think`
    - `suggestions-available`
    - `need-indexing`

    :param event_type: Type of event. Can be one of supported event type options
    :type event_type: str
    :param callback: Callback function to handle this event
    """
    if event_type == "recognition-begin":
      self.__recognition_begin_callback = callback
    elif event_type == "recognition-end":
      self.__recognition_end_callback = callback
    elif event_type == "audio-input":
      self.__audio_callback = callback
    elif event_type == "audio-output":
      self.__audio_output_callback = callback
    elif event_type == "file-query":
      self.__file_found_callback = callback
    elif event_type == "app-query":
      self.__app_found_callback = callback
    elif event_type == "data-output":
      self.__data_output_callback = callback
    elif event_type == "speech-start":
      self.__speech_output_start_callback = callback
    elif event_type == "speech-stop":
      self.__speech_output_stop_callback = callback
    elif event_type == "think":
      self.__thinking_callback = callback
    elif event_type == "suggestions-available":
      self.__suggestions_available_callback = callback
    elif event_type == "need-indexing":
      self.__notify_index_callback = callback


  def realtime_query(self, query: str):
    self.__live_query = query


  def send_utterance(self, utterance: str):
    self.tts.stop()
    self.__utterance = utterance
    pass


  def query_utterance(self, query: str):
    proper_query = ""
    for q in query:
      if q.isalnum() or q == " " or q == "'":
        proper_query += q
    proper_query = proper_query.strip()

    if self.__recognition_end_callback is not None:
      self.__recognition_end_callback()

    if proper_query == "":
      self.__send_response("Sorry, I didn't quiet understand!", "text", False)
      if settings.get_voice_activation_mode():
        self.wake_word_engine.start()
      return

    if proper_query.lower() == "system run update":
      self.queue_update()
    elif proper_query.lower() == "system run index":
      self.__system_index = True
    elif proper_query.lower() == "system run relearn":
      self.queue_relearn()
    else:
      self.__query = proper_query
    self.__send_response(query.rstrip().capitalize(), "text", True)


  def queue_index(self, action, params):
    self.__system_index = True


  def queue_update(self):
    self.__system_update = True


  def queue_relearn(self):
    self.__system_update_skills = True


  def activate_suggestion(self, data_type, data):
    if data_type == "text":
      self.__send_response(data, "text", True)
      self.__query = data
    if data_type == "file":
      is_directory = data[1] == "inode/directory"
      subprocess.call(("xdg-open", data[2] + data[0]))
      self.__send_response("Open " + ("folder " if is_directory else "file ") \
        + data[0], "text", True)
      self.__send_response("Opening " + data[0], "text", False)
    elif data_type == "app":
      self.__send_response("Launch " + data.get_name(), "text", True)
      try:
        data.launch()
        widget = utilities.get_app_bubble(data)
        self.__send_response(("Opening " if random.random() > 0.5 \
          else "Here's ") + data.get_name(), "text", False)
        self.__send_response(widget, "widget", False)
      except Exception as e:
        self.__send_response("That's odd, looks like I can't launch this app",
          "text", False)
        print(e)
