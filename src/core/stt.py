#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This file implements the speech-to-text system using _vosk_.
"""

# Base imports
import alsaaudio
import numpy
import _thread
import json
from vosk import Model, KaldiRecognizer

# Gandiva imports
from config import constants


# Based on solution from
# https://stackoverflow.com/questions/6867675/audio-recording-in-python

#--------------CLASS-SEPARATOR---------------#

class SpeechTotext():
  """
  ## Speech-to-Text
  Interprets speech to text using VOSK
  with a given speech model.
  """

  def __init__(self):
    # Init callbacks
    self.__audio_input_callback = None
    self.__recognition_complete_callback = None

    # recording thread inputs
    self.__recording = False

    # if not os.path.exists(self.recoding_path):
    #   os.mkdir(self.recoding_path)

    self.__model_location = constants.DATA_PATH + "/SpeechRecognitionModels/" \
        + "vosk-model-small-en-us-0.15"

    self.__model = None
    self.__recognizer = None


  def initialize(self):
    """
    Initialize Recognizer
    """
    self.__model = Model(self.__model_location)
    self.__recognizer = KaldiRecognizer(self.__model, 44100)


  def __record(self):
    """
    Recording thread function
    """
    self.__recording = True
    # Initialize alsa instance
    sound_input = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    sound_input.setchannels(1)
    sound_input.setrate(44100)
    sound_input.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    sound_input.setperiodsize(1024)
    while self.__recording:
      _, data = sound_input.read()
      a = numpy.fromstring(data, dtype="int16")
      if self.__audio_input_callback is not None:
        self.__audio_input_callback(numpy.abs(a).mean())
      # w.writeframes(data)
      if self.__recognizer.AcceptWaveform(data):
        result = json.loads(self.__recognizer.Result())
        self.__recognition_complete(result["text"])
        self.__recording = False
        break
    sound_input.close()


  def start_listening(self):
    """
    Start listening thread
    """
    if not self.__recording and self.__recognizer is not None:
      _thread.start_new_thread(self.__record, ())


  def stop_listening(self):
    """
    Stop listening thread
    """
    self.__recording = False


  def connect(self, event_type="audio", callback=None):
    """
    Add callback reference to particular events.

    Supported Event Type Options:
    - `audio`
    - `recognition-complete`

    :param event_type: Type of event. Can be one of supported event type options
    :type event_type: str
    :param callback: Callback function to handle this event
    """
    if event_type == "audio":
      self.__audio_input_callback = callback
    elif event_type == "recognition-complete":
      self.__recognition_complete_callback = callback


  # Event handlers
  # ----------------------------------------------------------------------------
  def __recognition_complete(self, text: str):
    self.__recognition_complete_callback(text)
