#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Personality skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from typing import Dict, List
from gandiva.core.skill_backend import Skill, Intent
import random

class PersonalitySkill(Skill):
  """
  This skill gives Gandiva a "personality". It allows Gandiva to respond to
  certain personal questions directed towards Gandiva.
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    # Always use portal to connect to internet
    self.portal = skill_backend.portal

    self.generic_intent = Intent(
      "generic",
      [
        "[what,who] are you",
        "what is your {name,NN}"
      ],
      "en-us"
    )

    self.answers = [
      "I am Gandiva. I am an AI program designed to help you.",
      "I am an AI program designed to help you with stuff. \
        You can call me Gandiva"
    ]
    self.name_answers = [
      "My name is Gandiva.",
      "The name's Gandiva, Project Gandiva.",
      "I am called Gandiva"
    ]

    self.register_intent(self.intent_handler, self.generic_intent)

    self.creation_intent = Intent(
      "creation",
      [
        "who [made,created] you",
        "who [makes,creates,maintains] you",
      ],
      "en-us"
    )

    self.register_intent(self.creation_intent_handler, self.creation_intent)

    # Some jokes were taken from https://kidadl.com/funnies/jokes/best-computer-science-jokes-that-will-crack-up-any-comp-sci-majors
    # others from https://www.goodhousekeeping.com/life/parenting/g28581033/best-jokes-for-kids/
    self.JOKES = [
      "If I forget things easily, you need to RAM my head. Ha ha ha ha!",
      "I love spiders, they crawl all over the internet. I am sorry, \
        you don't like spiders?",
      "While coding, what language did the Spanish programmer use? Si++! \
        Aaa ha ha ha",
      "Did you know what I had for dinner? Not much, \
        just took a byte out of a cookie. Sad noises.",
      "How do they keep the soccer arena cool? They fill it with fans. \
        Ha ha ha.",
      "Why can't you tell a joke to an egg? \
        You don't because it might crack up. He he."
    ]
    self.joke_intent = Intent(
      "joke",
      [
        "tell me a joke",
        "make me laugh"
      ],
      "en-us"
    )

    self.register_intent(self.joke_handler, self.joke_intent, "Tell me a joke")


  def intent_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    if "name" in subjects.keys():
      if subjects["name"] == "name":
        answer = random.choice(self.name_answers)
      else:
        return None
    else:
      answer = random.choice(self.answers)
    return { "type": "text", "value": answer }


  def creation_intent_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    answer = "I was created by Subhadeep Jasu as part of " + \
    "Harvard's CS50 final project on June 29th, 2022. I am Gandiva and " + \
    "this is CS50!"
    return { "type": "text", "value": answer }


  def joke_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    return { "type": "text", "value": random.choice(self.JOKES)}
