#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This code implements the text-to-speech system using _epeak NG_.
There's plans to later on change that to a custom text-to-speech solution built
just for this project.
"""

# Base imports
import io
import time
from espeakng import ESpeakNG
import wave
import alsaaudio

#--------------CLASS-SEPARATOR---------------#

class TextToSpeech():
  """
  ## Text-to-Speech
  Speech synthesis drive of the AI.

  This is where any text can be converted to speech
  and allows the AI to have a voice.
  """

  PERIOD_SIZE = 1024

  def __init__(self):
    self.__espeak_engine = ESpeakNG()
    self.__espeak_engine.voice = 'en-us'
    self.__audio_callback = None
    self.__ready = False
    self.__speaking = False


  def speak(self, text:str):
    """
    Utter the given text.
    """
    self.__ready = True

    wav = self.__espeak_engine.synth_wav(text)

    wavef = wave.open(io.BytesIO(wav))

    framerate = wavef.getframerate()
    nchannels = wavef.getnchannels()

    sound_output = alsaaudio.PCM()
    sound_output.setchannels(nchannels)
    sound_output.setrate(framerate)
    sound_output.setperiodsize(TextToSpeech.PERIOD_SIZE)


    data = wavef.readframes(TextToSpeech.PERIOD_SIZE)

    # Reference:
    # https://stackoverflow.com/questions/17657103/how-to-play-wav-file-in-python
    self.__speaking = True
    while data and self.__ready:
      sound_output.write(data)
      if self.__audio_callback is not None:
        self.__audio_callback(data)
      data = wavef.readframes(TextToSpeech.PERIOD_SIZE)

    sound_output.close()
    self.__speaking = False
    self.__ready = True


  def stop(self):
    """
    Stop utterance
    """
    if self.__ready and self.__speaking:
      self.__ready = False
      while not self.__ready:
        time.sleep(0.1)


  def connect(self, event_type:str, callback):
    """
    Add callback reference to particular events.

    Supported Event Type Options:
    - `audio`

    :param event_type: Type of event. Can be one of supported event type options
    :type event_type: str
    :param callback: Callback function to handle this event
    """
    if event_type == 'audio':
      self.__audio_callback = callback
