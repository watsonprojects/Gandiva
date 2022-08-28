#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This file has the skill backend, skill class and intent class.
Skill backend takes care of registering intents that are supplied by skills and
their intent handlers. Intent handlers are callbacks which can be later used to
perform some action based on the user's "intent" as determined from user's
question. The `Skill` class is inherited by the skills, which gives them access
to the `register_intent()` function, which is then called by the skill to
register itself in the skill database of Gandiva. `Intent` refers structure
representing user's intention as derived from the natural language input given
by the user.
"""

# Base imports
from typing import List
import re
import sqlite3
import os
from gi.repository import GLib
from config import constants
import sys
import shutil
import importlib
import inspect
import itertools

from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

# Gandiva imports
from system_portal import SystemPortal

#--------------CLASS-SEPARATOR---------------#

class Intent():
  """
  Intent represents what the user wants to convey
  using the query
  """

  def __init__(self, classification:str, patterns:List[str], lang:str):
    self.classification = classification
    self.patterns = patterns
    self.lang = lang



#--------------CLASS-SEPARATOR---------------#

class SkillBackend():
  """
  ## Skill Backend
  Skill backend takes care of registering intents that
  are supplied by skills and their intent handlers.
  Intent handlers are callbacks which can be later used
  to perform some action based on the user's "intent".
  """

  # List of skills
  skills_list = []

  # Example list for showing them for suggestions
  example_list = []

  # List of intent handlers or callbacks supplied by the skills
  callback_list = []

  # Dictionary of context variables which are later used to assume subjects
  # from pronouns
  context_dict = {}

  plugin_directory = ""

  db_cursor = None

  VALID_INTERNAL_INTENT_HANDLERS = {
    "direct_launch_handler" : "AppSearch",
    "keyword_app_search_handler" : "AppSearch",
    "category_search_handler" : "AppSearch",
    "games_search_handler" : "AppSearch",
    "accessories_search_handler" : "AppSearch",
    "keyword_search_handler": "FileSystemSearch",
    "library_handler": "FileSystemSearch"
  }

  def __init__(self, force_install_skills=False):
    self.__db_location = GLib.get_user_cache_dir() + "/" \
      + constants.APPLICATION_ID
    if not os.path.exists(self.__db_location):
      os.mkdir(self.__db_location)
    self.__db_location += "/databases"
    if not os.path.exists(self.__db_location):
      os.mkdir(self.__db_location)

    self.__db_location += "/skills.db"

    self.__portal_error_callback = None

    self.portal = SystemPortal()
    self.portal.connect_error_callback(self.portal_error_handler)

    SkillBackend.plugin_directory = os.path.join(GLib.get_user_data_dir(),
      constants.APPLICATION_ID, "skill_plugins")
    if not os.path.exists(SkillBackend.plugin_directory):
      print(f"Skill's not installed. Installing them to \
        {SkillBackend.plugin_directory}")
      if not os.path.exists(os.path.join(GLib.get_user_data_dir(),
        constants.APPLICATION_ID)):
        os.mkdir(os.path.join(GLib.get_user_data_dir(),
          constants.APPLICATION_ID))
      shutil.copytree(os.path.join(constants.DATA_PATH, "SkillPlugins"),
        SkillBackend.plugin_directory)
    elif force_install_skills:
      print("Reinstalling skills…")
      if os.path.exists(os.path.join(GLib.get_user_data_dir(),
        constants.APPLICATION_ID, SkillBackend.plugin_directory)):
        shutil.rmtree(SkillBackend.plugin_directory)

      shutil.copytree(os.path.join(constants.DATA_PATH, "SkillPlugins"),
        SkillBackend.plugin_directory, dirs_exist_ok=True)

    print("Plugin directory: ", SkillBackend.plugin_directory)


  def connect_portal_error_callback(self, callback):
    self.__portal_error_callback = callback

  def portal_error_handler(self, error_type):
    if self.__portal_error_callback is not None:
      self.__portal_error_callback(error_type)


  def scan_skills(self):
    """
    Discover skills from the user data folder.
    Skills are contained in their own folders inside a `__init__.py` file.

    The class name should be the same as the folder name with a "Skill" prefix
    So if there's a skill `FooBar`, then the folder is named `FooBar`
    the class is named `FooBarSkill`
    """
    if os.path.exists(self.__db_location):
      os.remove(self.__db_location)

    self.__skill_connection = sqlite3.connect(self.__db_location)

    self.__skill_connection.execute("""
      CREATE TABLE IF NOT EXISTS skills (
        id INTEGER NOT NULL PRIMARY KEY,
        syntax TEXT,
        sentence TEXT,
        lang TEXT,
        name TEXT,
        classification TEXT,
        fallback TINYINT,
        callback_id INTEGER
      );
    """)

    self.__skill_connection.execute("CREATE INDEX IF NOT EXISTS syntax_index \
      ON skills (syntax)")

    SkillBackend.db_cursor = self.__skill_connection.cursor()

    sys.path.append(SkillBackend.plugin_directory)

    classes = []
    for dir_entry in os.scandir(SkillBackend.plugin_directory):
      if dir_entry.is_dir():
        classes += [dir_entry.name]

    if self.__skill_connection:
      self.__skill_connection.close()

    for class_name in classes:
      module = importlib.import_module(class_name)
      skill_class = getattr(module, class_name + "Skill")
      if inspect.getmro(skill_class)[1].__module__ + "." \
        + inspect.getmro(skill_class)[1].__name__ \
        == "gandiva.core.skill_backend.Skill":
        SkillBackend.skills_list += [skill_class(self)]


  def __permute_pattern(self, patterns:List[str]):
    """
    Find all possible combinations from the given sentence in intent.
    """
    sentence_groups = []
    variable_groups = []
    for pattern in patterns:
      tokens = pattern.split(" ")
      pattern_list = []
      token_index = 0
      variable_indices = []
      for token in tokens:
        # If the token is an array of possible words
        if re.search(r"^\[.*\]$", token) is not None:
          sub_tokens = token.replace("[", "").replace("]", "").split(",")
          pattern_list += [sub_tokens]
        # If the token is a variable
        elif re.search(r"^{.*}$", token) is not None:
          sub_tokens = token.replace("{", "").replace("}", "").split(",")
          # First item is always the token name
          variable = sub_tokens[0]
          # the other ones represent the possible tags
          variable_indices += [(variable, token_index)]
          tags = sub_tokens[1:]
          if len(tags) == 0:
            print("[SkillBackend] Intent Error: Speech tags not associated \
              with variable <" + variable + ">")
            break
          possible_words = []
          # Temporarily substitute the variables to facilitate pos tagging
          for tag in tags:
            if tag == "JJ": # Adjective
              possible_words += ["nice"]
            elif tag == "RB": # Adverb
              possible_words += ["nicely"]
            elif tag == "VB": # Adverb
              possible_words += ["do"]
            else: # Probably noun
              possible_words += ["Amanda"]
          pattern_list += [possible_words]
        else:
          pattern_list += [[token]]
        token_index += 1

      # Reference: https://www.quora.com/How-do-I-generate-all-the-unique-combinations-of-a-2D-array-in-Python
      sentence_groups += [
        [" ".join(token) for token in itertools.product(*pattern_list)]
      ]
      variable_groups += [variable_indices]

    syntax_list = []
    converted_sentences = []
    for i in range(len(sentence_groups)):
      for j in range(len(sentence_groups[i])):
        tokenized = word_tokenize(sentence_groups[i][j])
        intent_tags = pos_tag(tokenized)
        tag_list = []
        for tag in intent_tags:
          tag_list += [tag[1]]
        syntax_list += [" ".join(tag_list)]
        for variable_tuple in variable_groups[i]:
          tokenized[variable_tuple[1]] = "{" + variable_tuple[0] + "}"
        converted_sentences += [" ".join(tokenized)]

    return syntax_list, converted_sentences


  def register_intent(self, intent_handler_callback, intent:Intent, name:str,
    example:str, fallback:bool):
    """
    Save the intent details and saved callback index to DB.
    """

    if not fallback:
      print("[SkillBackend] Registering intent for", name, "skill…")
      SkillBackend.callback_list += [intent_handler_callback]
      callback_index = len(SkillBackend.callback_list) - 1

      syntax_list, sentences = self.__permute_pattern(intent.patterns)

      db_location = GLib.get_user_cache_dir() + "/" + constants.APPLICATION_ID \
        + "/databases/skills.db"
      skill_conn = sqlite3.connect(db_location)
      db_cursor = skill_conn.cursor()

      i = 0
      for syntax in syntax_list:
        db_cursor.execute("""
          INSERT INTO skills (
            syntax,
            sentence,
            lang,
            name,
            classification,
            fallback,
            callback_id
          ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
          syntax,
          sentences[i],
          intent.lang,
          name,
          intent.classification,
          0,
          callback_index
        ))
        i += 1

      skill_conn.commit()
      skill_conn.close()
    else:
      # Fallback skills don't have intents. They just use the entire query
      print("[SkillBackend] Registering fallback intent for", name, "skill…")
      SkillBackend.callback_list += [intent_handler_callback]
      callback_index = len(SkillBackend.callback_list) - 1
      db_location = GLib.get_user_cache_dir() + "/" + constants.APPLICATION_ID \
        + "/databases/skills.db"
      skill_conn = sqlite3.connect(db_location)
      db_cursor = skill_conn.cursor()
      db_cursor.execute("""
        INSERT INTO skills (
          syntax,
          sentence,
          lang,
          name,
          classification,
          fallback,
          callback_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
      """, (
        "",
        "",
        "",
        name,
        "fallback",
        1,
        callback_index
      ))

      skill_conn.commit()
      skill_conn.close()

    # Store the example queries supplied by the skill
    if example != "":
      SkillBackend.example_list += [example]


  def verify_internal_intent_handler(self,
    function_name: str, module_name: str) -> bool:
    if function_name in SkillBackend.VALID_INTERNAL_INTENT_HANDLERS:
      return SkillBackend.VALID_INTERNAL_INTENT_HANDLERS[function_name] \
        == module_name

    return False



#--------------CLASS-SEPARATOR---------------#

class Skill():
  """
  ## Skill Base Class
  A skill represents an ability that is added to the app.
  Every skill comes with the following:
  - A set of intents (sentences that rough represents the user's query)
  - A couple of intent handler functions that return some answer and/or
    perform some action
  """

  def __init__(self, skill_backend):
    self.__skill_backend = skill_backend


  def register_intent(self, handler_callback, intent:Intent,
    example_query:str="", fallback:bool=False):
    """
    Add this skill to the AI skillset.

    :param handler_callback: Callback function used to handle intent
    :param intent: An intent (see Intent) that the skill can handle
    :param example_query: An example query that the user can send to trigger
    this skill
    :param fallback: Whether or not to register as a fallback which runs only
    when all other skills have failed.
    If `True`, pass `None` for intent paramter.
    """
    self.__skill_backend.register_intent(handler_callback, intent,
      self.__class__.__name__, example_query, fallback)

    # self.__skill_backend.register_settings()
