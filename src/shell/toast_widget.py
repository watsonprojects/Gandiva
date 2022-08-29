#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This code file implements a custom toast widget
"""

# Gtk imports
import gi
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0") # Make sure Gtk 4 are imported
#pylint: enable=wrong-import-position
from gi.repository import Gtk, GLib

class ToastWidget(Gtk.Box):
  """
  Toast widget class to display momentary information
  and allow user to take instant action
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_spacing(8)
    self.set_margin_top(48)
    self.set_margin_start(8)
    self.set_margin_end(8)
    self.set_halign(Gtk.Align.CENTER)
    self.set_valign(Gtk.Align.START)

    self.get_style_context().add_class("toast")
    self.get_style_context().add_class("toast-fade-in")

    self.set_orientation(Gtk.Orientation.HORIZONTAL)
    self.dismiss_button = Gtk.Button()
    self.dismiss_button.set_icon_name("window-close-symbolic")
    self.dismiss_button.connect("clicked", self.__dismiss_handler)

    self.__action = ""
    self.__application = None


  def set_data(self, message:str, application, action_label="", action=""):
    """
    Set data for the toast widget

    :param message: Message or title of toast
    :type message: str
    :param application: Gtk.Application instance which this widget belongs to
    :param action_label: Action title. String to be displayed in the main button
    :type action_label: str
    :param action: Action string which is added to the action group of
    application
    :type action: str
    """
    self.message_label = Gtk.Label.new(message)
    self.message_label.set_hexpand(True)
    self.message_label.set_wrap(True)
    self.append(self.message_label)

    if action_label != "" and action != "":
      self.action_button = Gtk.Button()
      self.action_button.set_label(action_label)
      self.action_button.connect("clicked", self.__activate_action)
      self.append(self.action_button)

      self.__action = action
      self.__application = application

    self.append(self.dismiss_button)
    GLib.timeout_add(4000, self.dismiss)


  def __dismiss_handler(self, _):
    self.dismiss()


  def dismiss(self):
    """
    Hides this toast
    """
    self.get_style_context().add_class("toast-hide")
    GLib.timeout_add(500, self.__dismiss)
    return False


  def __activate_action(self, _):
    self.__application.activate_action(self.__action)


  def __dismiss(self):
    self.hide()
    return False
