#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
DuckDuckGo skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from typing import Dict, List
from gandiva.core.skill_backend import Skill, Intent

import gi
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
#pylint: enable=wrong-import-position

from gi.repository import Gtk, Pango, GdkPixbuf

class DuckDuckGoSkill(Skill):
  """
  This skill allows Gandiva to answer certain trivia questions from the user.
  It also acts as a fallback skill which is used when all other likely intents
  handlers have failed. It utilizes the DuckDuckGo answering API.
  """
  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    # Always use portal to connect to internet
    self.portal = skill_backend.portal

    self.topic_intent = Intent(
      'generic',
      [
        '[what,who] [is,was,are,were] [a,an,the] {subject,JJ,NN,NNS}',
        '[what,who] [is,was,are,were] {subject,JJ,NN,NNS}',
        'tell me about {subject,JJ,NN,NNS}'
      ],
      'en-us'
    )

    self.register_intent(self.search_topic_intent_handler, self.topic_intent,
      'Tell me about Jupiter')

    self.register_intent(self.fallback_intent_handler, None,
      'Valley Forge National Park', True)

    self.URL = 'https://api.duckduckgo.com'


  def __send_query(self, query: str):
    PARAMS = {
      'q': query,
      'format': 'json',
      'pretty': 0,
      'no_html': 1,
      'skip_disambig': 1
    }
    raw_result = self.portal.http_get(self.URL, PARAMS)

    if raw_result is not None:
      result = raw_result.json()
      main_answer = ''

      if result['Definition'] != '':
        main_answer = result['Definition']
      elif result['Abstract'] != '':
        main_answer = result['Abstract']

      return main_answer, result['Image']
    else:
      return None, None


  def search_topic_intent_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    query = ''
    if 'subject' in subjects:
      query = subjects['subject']
    else:
      return None

    main_answer, image_url = self.__send_query(query)
    if main_answer is None or len(main_answer) == 0:
      return None

    main_box = Gtk.Box()
    main_box.set_orientation(Gtk.Orientation.VERTICAL)

    answer_label = Gtk.Label()
    answer_label.set_margin_top(12)
    answer_label.set_margin_bottom(12)
    answer_label.set_margin_start(6)
    answer_label.set_margin_end(6)
    answer_label.set_max_width_chars(28)
    answer_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    answer_label.set_wrap(True)
    answer_label.set_justify(Gtk.Justification.LEFT)
    answer_label.set_text(main_answer)
    main_box.append(answer_label)

    if image_url is not None:
      response = self.portal.http_get('https://duckduckgo.com' + image_url, {})
      if response is not None and not response.content.startswith(b'GIF'):
        loader = GdkPixbuf.PixbufLoader()
        loader.write(response.content)
        loader.close()

        image_pixbuf = loader.get_pixbuf()
        separator = Gtk.Separator()
        main_box.append(separator)

        image = Gtk.Image.new_from_pixbuf(image_pixbuf)
        image.set_size_request(200, 200)
        main_box.append(image)

    return { 'type': 'widget', 'value': main_box, 'utterance': main_answer }



  def fallback_intent_handler(self, query: str, tags:List, datadir:str):
    main_answer, image_url = self.__send_query(query)
    if main_answer is None or len(main_answer) == 0:
      return None

    main_box = Gtk.Box()
    main_box.set_orientation(Gtk.Orientation.VERTICAL)

    answer_label = Gtk.Label()
    answer_label.set_margin_top(12)
    answer_label.set_margin_bottom(12)
    answer_label.set_margin_start(6)
    answer_label.set_margin_end(6)
    answer_label.set_max_width_chars(28)
    answer_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    answer_label.set_wrap(True)
    answer_label.set_justify(Gtk.Justification.LEFT)
    answer_label.set_text(main_answer)
    main_box.append(answer_label)

    if image_url is not None:
      response = self.portal.http_get('https://duckduckgo.com' + image_url, {})
      if response is not None and not response.content.startswith(b'GIF'):
        loader = GdkPixbuf.PixbufLoader()
        loader.write(response.content)
        loader.close()

        image_pixbuf = loader.get_pixbuf()
        separator = Gtk.Separator()
        main_box.append(separator)

        image = Gtk.Image.new_from_pixbuf(image_pixbuf)
        image.set_size_request(200, 200)
        main_box.append(image)

    return { 'type': 'widget', 'value': main_box, 'utterance': main_answer }
