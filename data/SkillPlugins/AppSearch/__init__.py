#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
App Search skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from gandiva.core.skill_backend import Skill, Intent

class AppSearchSkill(Skill):
  """
  This is an internal skill which is used to identify user
  intents to open an app or search for apps based on a
  given criteria.
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    self.direct_launch_intent = Intent(
      'direct_launch',
      [
        '[launch,open] {name,NN,JJ} {subname,NN,JJ}',
        '[launch,open] {name,NN,JJ}',
        '[launch,open] the app called {name,NN,JJ} {subname,NN,JJ}'
        '[launch,open] the app called {name,NN,JJ}'
        '[launch,open] the {name,NN,JJ} {subname,NN,JJ} app'
        '[launch,open] the {name,NN,JJ} app'
      ],
      'en-us'
    )

    self.register_intent(self.direct_launch_handler,
      self.direct_launch_intent, 'Open Firefox')

    self.keyword_search_intent = Intent(
      'keyword_search',
      [
        '[find,search,show] all apps by [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] all apps [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] apps by [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] apps [name,keyword] {keyword,NN,JJ}',
      ],
      'en-us'
    )

    self.register_intent(self.keyword_app_search_handler,
      self.keyword_search_intent, 'Search apps by keyword game')

    self.category_search_intent = Intent(
      'category_app_search',
      [
        '[find,search,show] all the {category,NN,JJ} apps',
        '[find,search,show] all my {category,NN,JJ} apps',
        '[find,search,show] the {category,NN,JJ} apps',
        'search for {category,NN,JJ} apps',
      ],
      'en-us'
    )

    self.register_intent(self.category_search_handler,
      self.category_search_intent, 'Show all my music apps')

    self.search_games_intent = Intent(
      'category_app_search',
      [
        '[find,search,show] all the games',
        '[find,search,show] all my games',
        '[find,search,show] the games',
        'search for games',
        'i want to play games',
        'i wanna play games'
      ],
      'en-us'
    )

    self.register_intent(self.games_search_handler,
      self.search_games_intent, 'Search for games')

    self.search_accessories_intent = Intent(
      'category_app_search',
      [
        '[find,search,show] all the [accessories,utilities]',
        '[find,search,show] all my [accessories,utilities]',
        '[find,search,show] the [accessories,utilities]',
        'search for [accessories,utilities]',
      ],
      'en-us'
    )

    self.register_intent(self.accessories_search_handler,
      self.search_accessories_intent, 'Find the accessories')


  def direct_launch_handler(self, subjects, context, query, tags,
    lang:str, datadir:str):
    app_name = ''
    if 'name' in subjects.keys():
      app_name += subjects['name']

    if 'subname' in subjects.keys():
      app_name += ' ' + subjects['subname']

    if len(app_name) > 0:
      return { 'type': 'internal-action', 'action': 'app-launch',
        'value': app_name }

    return None


  def keyword_app_search_handler(self, subjects, context, query, tags,
    lang:str, datadir:str):
    if 'keyword' in subjects.keys():
      return { 'type': 'internal-action', 'action': 'app-search-keyword',
        'value': subjects['keyword'] }

    return None


  def category_search_handler(self, subjects, context, query, tags,
    lang:str, datadir:str):
    if 'apps' not in query:
      return None

    if 'category' in subjects.keys():
      category = subjects['category']

      return { 'type': 'internal-action', 'action': 'app-search-category',
        'value': category.capitalize() }

    return None


  def games_search_handler(self, subjects, context, query, tags,
    lang:str, datadir:str):
    if 'games' not in query:
      return None

    return { 'type': 'internal-action', 'action': 'app-search-games',
      'value': 'Games'}


  def accessories_search_handler(self, subjects, query, context, tags,
    lang:str, datadir:str):
    return { 'type': 'internal-action', 'action': 'app-search-accessories',
      'value': 'Accessories'}
