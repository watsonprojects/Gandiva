#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Wikipedia skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from typing import Dict, List
from gandiva.core.skill_backend import Skill, Intent
from gandiva.utils.utilities import BubbleStyle
import re
import html
from urllib import parse

import gi
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
#pylint: enable=wrong-import-position

from gi.repository import Gtk, Pango, GdkPixbuf, Adw

class WikipediaSkill(Skill):
  """
  This skill allows Gandiva to fetch information from Wikipedia when
  specifically asked to do so. The reponse speech bubble will often have
  multiple possible Wikipedia page references with a link to open the
  corresponding page in the default browser.
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    # Always use portal to connect to internet
    self.portal = skill_backend.portal

    self.bubble_style = BubbleStyle('#000000', '#FFFFFF', '', '#636466')

    self.html_tag_regex = re.compile('<.*?>')

    self.generic_intent = Intent(
      'generic',
      [
        'search wikipedia for {subject,JJ,NN}',
        'search for {subject,JJ,NN} on wikipedia',
        'search wikipedia for [a,an,the] {subject,JJ,NN}',
        'search for [a,an,the] {subject,JJ,NN} on wikipedia',
      ],
      'en-us'
    )

    self.register_intent(self.intent_handler, self.generic_intent,
      'Search Wikipedia for Saturn')

    # Wikipedia 'W' logo is a registered trademark of Wikimedia
    # https://commons.wikimedia.org/wiki/File:Wikipedia%27s_W.svg
    logo_svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
      <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
      <svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://web.resource.org/cc/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="128px" height="128px" viewBox="0 0 128 128" version="1.1">
        <metadata>
          <rdf:RDF>
            <dc:Image>
              <dc:format>image/svg+xml</dc:format>
              <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
              <dc:title>
                <rdf:Bag>
                  <rdf:li lang="en">Wikipedia's W</rdf:li>
                  <rdf:li lang="es">W de Wikipédia</rdf:li>
                </rdf:Bag>
              </dc:title>
              <dc:description>
                <rdf:Bag>
                  <rdf:li lang="en">The official Wikipedia favicon</rdf:li>
                  <rdf:li lang="es">El favicono oficial de Wikipédia</rdf:li>
                </rdf:Bag>
              </dc:description>
              <dc:creator>
                <rdf:Bag>
                  <rdf:li lang="en">
                    <dc:title>Jonathan Hoefler</dc:title>
                    <dc:description>The "W" originates from the Hoefler Text typeface by Jonathan Hoefler.</dc:description>
                  </rdf:li>
                  <rdf:li lang="en">
                    <dc:title>STyx</dc:title>
                    <dc:description>SVG document originally created by Wikimedia user STyx and uploaded on 25 June 2007</dc:description>
                    <dc:date>2007-06-26</dc:date>
                  </rdf:li>
                </rdf:Bag>
              </dc:creator>
              <dc:subject>
                <rdf:Bag>
                  <rdf:li>Wikipedia</rdf:li>
                  <rdf:li>favicon</rdf:li>
                </rdf:Bag>
              </dc:subject>
              <dc:rights>
                <rdf:Bag>
                  <dc:description>This work is ineligible for copyright and therefore in the public domain because it consists entirely of information that is common property and contains no original authorship.</dc:description>
                  <dc:description>™ Wikimedia Foundation, Inc. This file is (or includes) one of the official logos or designs used by the Wikimedia Foundation or by one of its projects. Use of the Wikimedia logos and trademarks is subject to the Wikimedia trademark policy and visual identity guidelines, and may require permission.</dc:description>
                </rdf:Bag>
              </dc:rights>
              <dc:publisher>
                <cc:Agent>
                  <dc:title>Wikimedia Commons</dc:title>
                </cc:Agent>
              </dc:publisher>
            </dc:Image>
          </rdf:RDF>
        </metadata>
        <use id="V (Left)" x="3.02" y="23.909" xlink:href="#V"/>
        <use id="V (Right)" x="38.265" y="23.909" xlink:href="#V"/>
        <defs>
          <path id="V" d="M93.849,0l0,2.139c-2.822,0.501 -4.957,1.388 -6.407,2.659c-2.077,1.889 -4.525,4.779 -6.132,8.672l-32.685,66.712l-2.175,0l-32.813,-67.579c-1.528,-3.469 -3.606,-5.589 -4.233,-6.359c-0.979,-1.195 -2.184,-2.13 -3.614,-2.804c-1.431,-0.675 -3.361,-1.108 -5.79,-1.301l0,-2.139l31.928,0l-0,2.139c-3.683,0.347 -5.439,0.964 -6.537,1.85c-1.097,0.886 -1.645,2.023 -1.645,3.411c-0,1.927 0.901,4.933 2.703,9.018l24.233,45.959l23.692,-45.381c1.842,-4.47 3.37,-7.573 3.37,-9.307c0,-1.118 -0.568,-2.187 -1.705,-3.209c-1.136,-1.021 -2.422,-1.744 -5.125,-2.168c-0.196,-0.038 -0.529,-0.096 -1,-0.173l0,-2.139l23.935,0Z"/>
        </defs>
      </svg>"""

    css = bytes("""
      button {
        border-radius: 0;
        border: none;
        border-top: 1px solid #0002;
        background: none;
        transition: all 0.2s ease;
      }

      button:hover {
        border-top: 1px solid #0005;
        background-image: linear-gradient(to right, #0000, #0001, #0000);
      }
    """, 'utf-8')

    self.css_provider = Gtk.CssProvider()
    self.css_provider.load_from_data(css)

    loader = GdkPixbuf.PixbufLoader()
    loader.write(logo_svg.encode())
    loader.close()
    self.logo_pixbuf = loader.get_pixbuf()


  def intent_handler(self, subjects:Dict, context:Dict, query:str, tags:List,
    lang:str, datadir:str):
    if 'subject' not in subjects.keys():
      return None

    URL = 'https://en.wikipedia.org/w/api.php'
    PARAMS = {
      'action': 'query',
      'format': 'json',
      'srqiprofile': 'wsum_inclinks_pv',
      'list': 'search',
      'srsort': 'relevance',
      'srlimit': 2,
      'srsearch': subjects['subject']
    }
    response = self.portal.http_get(URL, PARAMS)
    if response is None:
      return None

    api_response = response.json()
    possible_results = []
    tts_output = ''
    for data in api_response['query']['search']:
      clean_text = html.unescape(re.sub(self.html_tag_regex, '',
        data['snippet']))
      if tts_output == '':
        tts_output = clean_text
      url = 'https://en.wikipedia.org/wiki/' + parse.quote(data['title'])
      possible_results += [[clean_text, url]]

    open_link = lambda x: self.portal.open_uri(possible_results[
      int(carousel.get_position())
    ][1])

    main_widget = Gtk.Box()
    main_widget.set_orientation(Gtk.Orientation.VERTICAL)

    carousel = Adw.Carousel()
    carousel.set_allow_scroll_wheel(True)
    carousel.set_allow_mouse_drag(True)

    for result in possible_results:
      answer_label = Gtk.Label()
      answer_label.set_margin_top(12)
      answer_label.set_margin_bottom(12)
      answer_label.set_margin_start(6)
      answer_label.set_margin_end(6)
      answer_label.set_max_width_chars(28)
      answer_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
      answer_label.set_wrap(True)
      answer_label.set_justify(Gtk.Justification.LEFT)
      answer_label.set_text(result[0])
      carousel.append(answer_label)

    main_widget.append(carousel)

    link_button = Gtk.Button()
    link_button.get_style_context().add_provider(self.css_provider, 800)

    main_widget.append(link_button)

    wikipedia_logo = Gtk.Image.new_from_pixbuf(self.logo_pixbuf)
    link_button.set_child(wikipedia_logo)
    link_button.connect('clicked', open_link)

    return { 'type': 'widget', 'value': main_widget,
      'utterance': 'According to Wikipedia. ' + tts_output,
      'style': self.bubble_style }
