#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This code implements an app search and quick launch functionality. Apps are
loaded into memory as a list of `DesktopApplication` objects,
which has most of the useful information about the app which can be used to
launching them or trigerring actions.
"""

# Base imports
from functools import cmp_to_key
from gi.repository import Gio
import enchant

# Gandiva imports
from utils import utilities
from utils.utilities import DesktopApplication

#--------------CLASS-SEPARATOR---------------#


class AppSearch():
  """
  ## App Search
  Search apps installed in the system
  """

  def discover(self):
    """
    Load a list of all apps in the system
    """
    apps = Gio.AppInfo.get_all()

    self.__apps = []
    for app in apps:
      self.__apps += [DesktopApplication(app)]

    print(f"Found {len(self.__apps)} apps in the system.")

  def search(self, query_text: str, top_one: bool,
    top_three: bool, search_by_category=False):
    """
    Search an app or a list of apps by name
    """
    if query_text == "":
      return []

    query_text = utilities.strip_string(query_text)

    app_distance_maps = {}
    min_match = 9999
    min_match_index = -1
    i = 0
    for app in self.__apps:
      if not search_by_category:
        name = utilities.strip_string(app.get_name())
        distance = enchant.utils.levenshtein(
          name.upper(), query_text.upper())

        if distance == 0 and top_one:
          return app

        if top_three or top_one:
          if distance < 4 or name.upper() in query_text.upper():
            if distance < 4:
              distance -= len(query_text)
            if name.upper().startswith(query_text.upper()):
              distance -= len(query_text) * 2
            if name.upper() in query_text.upper():
              distance -= len(query_text)
            app_distance_maps[distance] = app
            if distance < min_match:
              min_match = distance
              min_match_index = i
          elif app.match_keyword(query_text):
            distance -= len(query_text) * 2

            app_distance_maps[distance] = app
            if distance < min_match:
              min_match = distance
              min_match_index = i
        else:
          if distance < 4:
            distance -= len(query_text)
          if name.upper().startswith(query_text.upper()):
            distance -= len(query_text) * 2
          if name.upper() in query_text.upper():
            distance -= len(query_text)
          if app.match_keyword(query_text):
            distance -= len(query_text) * 2

          app_distance_maps[distance] = app
          if distance < min_match:
            min_match = distance
            min_match_index = i

      else:
        if app.match_category(query_text):
          app_distance_maps[i] = app

      i += 1

    if top_one:
      return self.__apps[min_match_index]

    if search_by_category:
      return sorted(list(app_distance_maps.values()),
        key=cmp_to_key(self.desktop_app_comparator))

    sorted_maps = sorted(app_distance_maps.items())[
      :3 if top_three else 10]

    sorted_list = []
    for tup in sorted_maps:
      sorted_list += [tup[1]]

    return sorted_list

  def desktop_app_comparator(self, app1: DesktopApplication,
    app2: DesktopApplication):
    name1 = app1.get_name()
    name2 = app2.get_name()

    if name1 < name2:
      return -1
    elif name1 > name2:
      return 1
    else:
      return 0
