#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This code implements the suggestion buttons which appear right over the chat
textbox. These buttons can just insert text in the chat or even trigger certain
actions like launching apps or opening files and folders.
"""

# Base imports
import gi

from utils import utilities
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0")
#pylint: enable=wrong-import-position
from gi.repository import Gtk

#--------------CLASS-SEPARATOR---------------#

class SuggestionButton(Gtk.Button):
  """
  This provides suggestion buttons to the user,
  which the user can then click or activate
  to quickly perform that action.
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__click_callback = None
    self.get_style_context().add_class("suggestion-button")
    self.set_margin_top(5)
    self.set_margin_bottom(16)


  def set_button_details(self, data_type: str, data):
    """
    Set button details which can be later on referred to.

    :param data_type: Type of data in the suggestion
    :type data_type: str
    :param data: Data held by the button
    """
    self.__data_type = data_type
    self.__data = data

    self.box = Gtk.Box()
    self.box.set_spacing(4)
    self.set_child(self.box)

    if self.__data_type == "text":
      label = Gtk.Label()
      label.set_text(self.__data)
      self.get_style_context().add_class("suggestion-button-simple-text")

      self.box.append(label)

    elif self.__data_type == "file":
      self.icon = Gtk.Image()
      self.icon.set_icon_size(Gtk.IconSize.NORMAL)
      icon_name = utilities.get_icon_name_from_mime(self.__data[1])
      self.icon.set_from_icon_name(icon_name)
      self.get_style_context().add_class("suggestion-button-" + icon_name)

      self.box.append(self.icon)

      self.label = Gtk.Label()
      self.label.set_text(self.__data[0])
      self.box.append(self.label)

    elif self.__data_type == "app":
      self.icon = Gtk.Image()
      self.icon.set_icon_size(Gtk.IconSize.NORMAL)
      icon = self.__data.get_icon()
      if icon is not None:
        self.icon.set_from_gicon(self.__data.get_icon())
      else:
        self.icon.set_from_icon_name("application-default-icon")

      self.box.append(self.icon)
      self.get_style_context().add_class("suggestion-button-executable")

      self.label = Gtk.Label()
      self.label.set_text(self.__data.get_name())
      self.box.append(self.label)



  def connect_event(self, event_type, callback):
    """
    Add callback reference to particular events.

    Supported Event Type Options:

    :param event_type: Type of event. Can be one of supported event type options
    :type event_type: str
    :param callback: Callback function to handle this event
    """
    if event_type == "clicked":
      self.__click_callback = callback
      self.connect("clicked", self.__click_handler)


  # Event handlers
  # ----------------------------------------------------------------------------
  def __click_handler(self, _):
    self.__click_callback(self.__data_type, self.__data)
