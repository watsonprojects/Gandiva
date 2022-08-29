#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
OpenWeatherMap skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from typing import Dict, List
from gandiva.core.skill_backend import Skill, Intent
from gandiva.utils.utilities import BubbleStyle

import gi
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0")
#pylint: enable=wrong-import-position

from gi.repository import Gtk, Pango, GdkPixbuf

class OpenWeatherMapSkill(Skill):
  """
  This skill allows Gandiva to fetch weather information of the
  current location, using the OpenWeatherMap API.
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    # This uses a ID that I generated. It's for test purpose only
    # Generate a new one from openweathermap.org to get the full quota
    # TODO: Move this to a unified skill settings UI
    self._APP_ID = "2d33150abd911d5648439cf2756492ae"

    # Always use portal to connect to internet
    self.portal = skill_backend.portal

    self.weather_intent = Intent(
      "weather",
      [
        "how is the weather now",
        "how's the weather now",
        "how is the weather",
        "how's the weather"
      ],
      "en-us"
    )

    self.register_intent(self.intent_handler, self.weather_intent,
      "How's the weather now?")


  def intent_handler(self, subjects:Dict, context:Dict, query:str,
    tags:List, lang:str, datadir:str):
    URL = "https://api.openweathermap.org/data/2.5/weather"
    latlng = self.portal.get_location()
    if latlng is not None:
      PARAMS = {
        "lat": latlng[0],
        "lon": latlng[1],
        "appid": self._APP_ID
      }
    else:
      return None

    api_response = self.portal.http_get(URL, PARAMS).json()

    speech_response = ""

    if api_response is not None:
      place = api_response["name"]
      weather = api_response["weather"][0]
      temp = api_response["main"]["temp"]
      humidity = api_response["main"]["humidity"]
      wind_speed = api_response["wind"]["speed"]
      icon = weather["icon"]

      speech_response += "The weather in %s is %.1f degrees, %s. \
        Humidity is %.1f percent with wind speed of %.1f" \
        % (place, temp - 273.15, weather["description"], humidity, wind_speed)

      background_image = datadir + "/images/" + icon + ".jpg"

      background_color = "#000000"
      foreground_color = "#FFFFFF"

      if icon == "01d":
        background_color = "#003271"
        foreground_color = "#FFFFFF"
      elif icon == "01n":
        background_color = "#0E2256"
        foreground_color = "#F3F3F3"
      elif icon == "02d":
        background_color = "#405F8B"
        foreground_color = "#FFFFFF"
      elif icon == "02n":
        background_color = "#2F5582"
        foreground_color = "#F3F3F3"
      elif icon == "03d":
        background_color = "#E4ECE8"
        foreground_color = "#333333"
      elif icon == "03n":
        background_color = "#253236"
        foreground_color = "#F3F3F3"
      elif icon == "04d":
        background_color = "#25333E"
        foreground_color = "#FFFFFF"
      elif icon == "04n":
        background_color = "#0B1218"
        foreground_color = "#F3F3F3"
      elif icon == "09d":
        background_color = "#AAB1A9"
        foreground_color = "#810A32"
      elif icon == "09n":
        background_color = "#050F18"
        foreground_color = "#77909B"
      elif icon == "10d":
        background_color = "#252525"
        foreground_color = "#FFFFFF"
      elif icon == "10n":
        background_color = "#283031"
        foreground_color = "#F3F3F3"
      elif icon == "11d":
        background_color = "#2D3575"
        foreground_color = "#D0D4F6"
      elif icon == "11n":
        background_color = "#0C0E23"
        foreground_color = "#D0D4F6"
      elif icon == "13d":
        background_color = "#D7E5E7"
        foreground_color = "#2F4D5F"
      elif icon == "13n":
        background_color = "#0F3D5F"
        foreground_color = "#FFFFFF"
      elif icon == "50d":
        background_color = "#C0C2BF"
        foreground_color = "#333333"
      elif icon == "50n":
        background_color = "#C0C2BF"
        foreground_color = "#333333"

      main_grid = Gtk.Grid()
      main_grid.set_column_homogeneous(True)

      upper_grid = Gtk.Grid()
      upper_grid.set_margin_start(8)
      upper_grid.set_margin_end(8)
      upper_grid.set_margin_top(8)
      upper_grid.set_margin_bottom(8)

      icon_image = self.get_image(datadir, icon, 48)
      icon_image.set_halign(Gtk.Align.START)
      upper_grid.attach(icon_image, 0, 0, 1, 2)

      location_label = Gtk.Label()
      location_label.set_text(place.upper())
      location_label.set_halign(Gtk.Align.END)
      location_label.set_valign(Gtk.Align.END)
      location_label.set_hexpand(True)
      location_label.set_ellipsize(Pango.EllipsizeMode.END)
      location_label.get_style_context().add_class("bold")
      upper_grid.attach(location_label, 1, 0, 1, 1)

      condition_label = Gtk.Label()
      condition_label.set_halign(Gtk.Align.END)
      condition_label.set_valign(Gtk.Align.START)
      condition_label.set_text(weather["description"].capitalize())
      upper_grid.attach(condition_label, 1, 1, 1, 1)

      main_grid.attach(upper_grid, 0, 0, 3, 1)

      # main_grid.attach(Gtk.Separator(), 0, 1, 3, 1)

      temp_box = Gtk.Box()
      temp_box.set_margin_start(8)

      temp_image = self.get_image(datadir, "temp", 16)
      temp_box.append(temp_image)

      temp_label = Gtk.Label()
      temp_label.set_text("%.1f°" % (temp - 273.15,))
      temp_box.append(temp_label)

      main_grid.attach(temp_box, 0, 2, 1, 1)

      humidity_box = Gtk.Box()
      humidity_box.set_margin_bottom(8)
      humidity_box.set_margin_top(8)

      humidity_image = self.get_image(datadir, "humidity", 16)
      humidity_box.append(humidity_image)

      humidity_label = Gtk.Label()
      humidity_label.set_text("%.f%%" % (humidity))
      humidity_box.append(humidity_label)

      main_grid.attach(humidity_box, 1, 2, 1, 1)

      wind_speed_box = Gtk.Box()
      wind_speed_box.set_margin_end(8)

      wind_speed_image = self.get_image(datadir, "wind_speed", 16)
      wind_speed_box.append(wind_speed_image)

      wind_speed_label = Gtk.Label()
      wind_speed_label.set_text("%.1f" % (wind_speed))
      wind_speed_box.append(wind_speed_label)

      main_grid.attach(wind_speed_box, 2, 2, 1, 1)

      bubble_style = BubbleStyle(foreground_color, background_color,
        background_image, "#000000")
      return { "type": "widget", "value": main_grid,
        "utterance": speech_response, "style": bubble_style }
    else:
      return None


  def get_image(self, datadir:str, name:str, size:int) -> Gtk.Image:
    with open(datadir + "/images/" + name + ".svg", encoding="utf-8") \
      as icon_file:
      icon_data = icon_file.read()

    loader = GdkPixbuf.PixbufLoader()
    loader.write(icon_data.encode())
    loader.close()

    icon_pixbuf = loader.get_pixbuf()
    icon_image = Gtk.Image.new_from_pixbuf(icon_pixbuf)
    icon_image.set_pixel_size(size)

    return icon_image
