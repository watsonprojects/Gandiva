#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Date and time skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from typing import Dict, List
from gandiva.core.skill_backend import Skill, Intent
import random
from datetime import datetime

class DateTimeSkill(Skill):
  """
  This skill allows the app to respond to the user with the current time or date
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    self.time_intent = Intent(
      "time",
      [
        "what time is it",
        "could you please tell me the time",
        "may i know the time",
        "what's the time",
        "time"
      ],
      "en-us"
    )

    self.time_answers = [
      "The time's ",
      "It is ",
      "It's ",
      "The time is "
    ]

    self.register_intent(self.time_intent_handler, self.time_intent,
      "What time is it?")

    self.date_intent = Intent(
      "date",
      [
        "what date is [today,it]",
        "what's the date today",
        "what is the date today",
        "what is the date",
        "what's the date",
        "what is today's date"
      ],
      "en-us"
    )

    self.date_answers = [
      "Sure! Today's date is ",
      "Sure! Today is  ",
      "The date's ",
      "It is ",
      "It's "
    ]

    self.register_intent(self.date_intent_handler, self.date_intent,
      "What is the date?")

  # Reference: https://www.programiz.com/python-programming/datetime/strftime
  def time_intent_handler(self, subjects:Dict, context:Dict, query: str,
    tags:List, lang:str, datadir:str):
    if "time" in query:
      answer = random.choice(self.time_answers)
      time_now = datetime.now()
      time_string = time_now.strftime("%I:%M %p")
      natural_string = time_now.strftime("%-I %-M %p")
      return { "type": "text", "value": time_string,
        "utterance": answer + natural_string}


  def date_intent_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    if "date" in query:
      answer = random.choice(self.date_answers)
      date_now = datetime.now()
      date_string = date_now.strftime("%x")
      natural_string = date_now.strftime("%A %B %-d %Y")
      return { "type": "text", "value": date_string,
        "utterance": answer + natural_string}

    return None
