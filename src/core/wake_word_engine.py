#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This code implements the wakeword engine which continuosly listens for a
wakeword or hot word.Wake word currently set is _"Hey Gandiva"_.
"""

# Base imports
import alsaaudio
import _thread
import json
from vosk import Model, KaldiRecognizer

# Gandiva imports
from config import constants

#--------------CLASS-SEPARATOR---------------#

class WakeWordEngine():
  """
  ## Wake Word Engine
  Listens for a wakeword or hot word.
  Wake word is "Hey Gandiva".
  """
  def __init__(self):
    # Callbacks
    self.__callback = None

    # Setup alsa audio input
    self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    self.inp.setchannels(1)
    self.inp.setrate(44100)
    self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    self.inp.setperiodsize(1024)
    self.__recording = False

    # Load speech model
    self.__model_location = constants.DATA_PATH + '/SpeechRecognitionModels/' \
      + 'vosk-model-small-en-us-0.15'
    self.__model = None
    # These words roughly form our app's name
    self.__recognizer = None


  def initialize(self):
    """
    Initialize recognizer
    """
    self.__model = Model(self.__model_location)

    self.__recognizer = KaldiRecognizer(self.__model, 44100,
      '["hey gun diva", "[unk]"]')


  def start(self):
    """
    Start listening thread.
    """
    if not self.__recording:
      _thread.start_new_thread(self.__continuous_listening_thread, ())


  def __continuous_listening_thread(self):
    """
    Wakeword listening thread.
    Exits when wakeword detected.
    """
    self.__recording = True
    while self.__recording:
      _, data = self.inp.read()
      if self.__recognizer is not None and self.__recognizer.AcceptWaveform(data):
        result = json.loads(self.__recognizer.Result())
        if result['text'] == 'hey gun diva':
          self.__recording = False
          self.__callback()
          break


  def stop(self) -> None:
    """
    Stops listening thread.
    """
    self.__recording = False


  def connect(self, callback = None):
    """
    Add callback reference to handle wakeword activation event.

    :param _callback: Callback function to handle this event
    """
    self.__callback = callback
