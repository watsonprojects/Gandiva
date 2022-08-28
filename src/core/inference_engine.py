#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This is the *brain* of the app. This is where we take the query from the user,
match it against a couple of skills in the database, run a function that was
defined by the skill to handle the query and
send back the result to the core loop.
"""

#pylint: disable=consider-using-f-string

# Base imports
import random
import nltk
import re
import os
import sqlite3
from nltk import data
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from typing import List, Dict
from gi.repository import GLib

# Gandiva imports
from config import constants
from system_portal import SystemPortal
from skill_backend import SkillBackend

#--------------CLASS-SEPARATOR---------------#

class InferenceEngine():
  """
  ## Inference Engine
  This is the *brain* of the app.
  This is where we take the query from the user,
  match it against a couple of skills in the database,
  run a function that was defined by the skill to
  handle the query.
  """

  def __init__(self):
    # Callbacks
    self.__portal_error_callback = None

    # NLTK data path setup
    if not os.path.exists(GLib.get_user_data_dir()):
      os.mkdir(GLib.get_user_data_dir())
    if not os.path.exists(os.path.join(GLib.get_user_data_dir(),
      constants.APPLICATION_ID)):
      os.mkdir(os.path.join(GLib.get_user_data_dir(), constants.APPLICATION_ID))
    if not os.path.exists(os.path.join(GLib.get_user_data_dir(),
      constants.APPLICATION_ID, "data")):
      os.mkdir(os.path.join(GLib.get_user_data_dir(),
        constants.APPLICATION_ID, "data"))
    if not os.path.exists(os.path.join(GLib.get_user_data_dir(),
      constants.APPLICATION_ID, "data", "nltk")):
      os.mkdir(os.path.join(GLib.get_user_data_dir(),
        constants.APPLICATION_ID, "data", "nltk"))

    self.__nltk_data_path = os.path.join(GLib.get_user_data_dir(),
      constants.APPLICATION_ID, "data", "nltk")
    data.path = [self.__nltk_data_path]
    print(self.__nltk_data_path)

    # Initialize the skill system
    self.__skill_backend = SkillBackend()
    self.__skill_backend.connect_portal_error_callback(
      self.portal_error_handler)

    # DB path setup
    self.__db_location = GLib.get_user_cache_dir() + "/" \
      + constants.APPLICATION_ID + "/databases/skills.db"


  def connect_portal_error_callback(self, callback):
    self.__portal_error_callback = callback


  def portal_error_handler(self, error_type):
    if self.__portal_error_callback is not None:
      message = "Error"
      if error_type == SystemPortal.ERROR_NO_INTERNET:
        message = "Look's like I cannot access the internet!"
      elif error_type == SystemPortal.ERROR_NO_GEO_LOCATION:
        message = "I am unable to assertain out location"
      elif error_type == SystemPortal.ERROR_NO_XDG_OPEN:
        message = "I was unable to open the resource"

      self.__portal_error_callback(message)


  def update(self):
    """
    Update the Inference Engine.
    """
    self.download()
    # Scan for skills
    self.__skill_backend.scan_skills()

    return random.sample(self.__skill_backend.example_list,
      min(5, len(self.__skill_backend.example_list)))

  def download(self):
    """
    Download the NLTK packages
    """
    nltk.download("punkt", download_dir=self.__nltk_data_path)
    nltk.download("averaged_perceptron_tagger",
      download_dir=self.__nltk_data_path)

  def update_skills(self):
    """
    Reinstall skills (Restart the app if things don't work)
    """
    if self.__skill_backend:
      del self.__skill_backend

    self.__skill_backend = SkillBackend(True)
    self.__skill_backend.scan_skills()

    return random.sample(self.__skill_backend.example_list,
      min(5, len(self.__skill_backend.example_list)))


  def __shortlist(self, cursor:sqlite3.Cursor,
    tokens:List[str], intent_tag_list:List):
    """
    Get a small list of skills that best handle the given query.
    """
    largest_matching_results = []
    variable_list = []

    # Perform a blanket scan by gradually increasing the length of sentence
    # structure considered for matching. This gives a big list of all skills
    # whose "intent"s match the given query roughly
    for i in range(len(intent_tag_list)):
      short_syntax = " ".join(intent_tag_list[:i]) + "%"
      cursor.execute("""
        SELECT * FROM skills
         WHERE syntax LIKE ?
      """, (short_syntax,))
      db_results = cursor.fetchall()
      if len(db_results) != 0:
        largest_matching_results = db_results
      else:
        # At this point we have exceeded the max length that could be matched
        break

    n = len(tokens)

    scores = {}

    # Match the inidivdual words to and give the skills a score based on the
    # most number of matches
    for result in largest_matching_results:
      variable_dict = {}
      result_tags = result[1].split(" ")
      result_tokens = result[2].split(" ")
      if result[0] not in scores:
        scores[result[0]] = 0

      n_result = len(result_tokens)
      for i in range(n_result if n > n_result else n):
        # Check if the words match (ignore if it's a variable enclosed within
        # flower brackets)
        if re.search("^{.*}$", result_tokens[i]) is None \
          and tokens[i] == result_tokens[i]:
          scores[result[0]] += 2
        # Check is the skill is expecting a variable word
        elif re.search("^{.*}$", result_tokens[i]) is not None:
          variable_dict[result_tokens[i].replace("{", "").replace("}", "")] \
            = tokens[i]
        else:
          scores[result[0]] -= 1

        # Bonus points for matching the pos tag as well
        if intent_tag_list[i] == result_tags[i]:
          scores[result[0]] += 1
      variable_list += [variable_dict]

    # most_match = 0
    most_matched_index = -1
    second_most_matched_index = -1
    third_most_matched_index = -1
    i = 0

    short_listed_keys = sorted(scores, key=scores.get, reverse=True)[:3]

    # TODO: Improve code here to use an array of indices or dynamicaly
    # generating the result array instead of using fixed indices

    # Get the skill with the highest score
    for result in largest_matching_results:
      # The score must be at least the same number of words in the query
      # for it to be considered valid
      if scores[result[0]] > n and result[0] in short_listed_keys:
        if short_listed_keys.index(result[0]) == 0:
          most_matched_index = i
        elif short_listed_keys.index(result[0]) == 1:
          second_most_matched_index = i
        elif short_listed_keys.index(result[0]) == 2:
          third_most_matched_index = i
      i += 1

    if most_matched_index < 0:
      return [], []
    elif second_most_matched_index < 0:
      return [
        largest_matching_results[most_matched_index]
      ], [
        variable_list[most_matched_index]
      ]
    elif third_most_matched_index < 0:
      return [
        largest_matching_results[most_matched_index],
        largest_matching_results[second_most_matched_index]
      ], [
        variable_list[most_matched_index],
        variable_list[second_most_matched_index]
      ]
    else:
      return [
        largest_matching_results[most_matched_index],
        largest_matching_results[second_most_matched_index],
        largest_matching_results[third_most_matched_index]
      ], [
        variable_list[most_matched_index],
        variable_list[second_most_matched_index],
        variable_list[third_most_matched_index]
      ]


  def infer(self, query:str):
    """
    Find out what the user wants.

    :param query: User text input/query
    :type query: str
    """
    # Tag the sentence
    tokenized = word_tokenize(query.lower())
    intent_tags = pos_tag(tokenized)
    intent_syntax_query_list = []
    for tag in intent_tags:
      intent_syntax_query_list += [tag[1]]

    # Connect to skill database
    skill_conn = sqlite3.connect(self.__db_location)
    db_cursor = skill_conn.cursor()

    # Get list os skills that can handle the query and the list of variables
    short_listed_results, variables = self.__shortlist(db_cursor, tokenized,
      intent_syntax_query_list)

    skill_results = []

    i = 0
    for result in short_listed_results:
      # syntax = result[1]
      lang = result[3]
      skill_name = result[4]
      callback_id = result[7]
      subjects = variables[i]
      context = self.__get_context(skill_name)

      # Call the skill intent handler function and get answers
      intent_handler = SkillBackend.callback_list[callback_id]
      skill_result = intent_handler(subjects, context, query.lower(),
        intent_tags, lang, os.path.join(self.__skill_backend.plugin_directory,
        intent_handler.__module__))

      if skill_result is not None:
        print(
          f"[Inference Engine] Answered by {intent_handler.__module__} skill")
        if skill_result["type"] == "internal-action" and \
          not self.__skill_backend.verify_internal_intent_handler(
            intent_handler.__name__, intent_handler.__module__):
          db_cursor.close()
          skill_conn.close()
          return [{"type": "text", "value": \
            "This is urgent, the skill %s is trying to access restricted areas \
              of my system" % intent_handler.__module__}]
        skill_results += [skill_result]
        break

      i += 1

    # If the query hasn't been answered or handled by any skill,
    # Use the the fallback intent handlers and pass the whole query
    # without any interpretation. The fallback handler must interpret
    # such queries on their own.
    if len(skill_results) == 0:
      db_cursor.execute("""
        SELECT * FROM skills
        WHERE fallback = 1
      """)

      fallback_skills = db_cursor.fetchall()

      if len(fallback_skills) > 0:
        for fallback_skill in fallback_skills:
          skill_name = fallback_skill[4]
          callback_id = fallback_skill[7]
          intent_handler = SkillBackend.callback_list[callback_id]
          skill_result = intent_handler(query, tokenized, os.path.join(
            self.__skill_backend.plugin_directory, intent_handler.__module__))
          if skill_result is not None:
            if skill_result["type"] == "internal-action" and \
              not self.__skill_backend.verify_internal_intent_handler(
                intent_handler.__name__, intent_handler.__module__):
              db_cursor.close()
              skill_conn.close()
              return [{"type": "text", "value": "This is urgent, the skill %s \
                is trying to access restricted areas of my system" \
                  % intent_handler.__module__}]
            print("[Inference Engine] Answered by %s fallback skill" \
              % intent_handler.__module__)
            skill_results += [skill_result]
            break


    db_cursor.close()
    skill_conn.close()

    # If there's no answers even from fallback intent handlers,
    # let the user know that there's no known answers we way to
    # handle the query
    if len(skill_results) == 0:
      return [{"type": "text", "value": "I am sorry, I don't know"}]


    return skill_results


  def __get_context(self, skill_name:str) -> Dict:
    """
    Get the context dictionary associated with a given skill.
    Context can be used by certain queries involving pronouns
    to implicitly assume the subject.

    :param skill_name: Name of skill
    :type skill_name: str
    """
    return {key.replace(skill_name + "+", ""): value for (key, value) \
      in SkillBackend.context_dict.items() if key.startswith(skill_name)}
