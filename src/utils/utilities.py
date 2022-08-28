#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
Utilities used by various modules of the app.
Usually contains classes and functions that are common used
but I couldn't find a better place to have them in.
"""

import gi
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0") # Make sure Gtk 4 is imported
#pylint: enable=wrong-import-position
from gi.repository import Gtk, Gio, Pango

#--------------CLASS-SEPARATOR---------------#

class BubbleStyle():
  """
  This class represents all the essential paramters of a bubble"s
  style. When instantiated, it also provides the css for the bubble
  based on the given paramters
  """

  # Code ported from:
  # https://github.com/SubhadeepJasu/hemera/blob/master/src/bubbles/SVGData.vala
  # Originally authored by me and Hannes Schulze for Hemera

  def __init__(self, foreground_color:str, background_color:str,
               background_image: str, border_color: str):
    self.foreground_color = foreground_color
    self.background_color = background_color
    if background_image == "":
      self.__background_image = "none"
    else:
      self.__background_image = "linear-gradient(90deg, " \
                              + self.background_color \
                              + "," + self.background_color  \
                              + "50), url(file:" + background_image + ")"
    self.border_color = border_color

    # CSS for the bubble
    # converted to byte array for use with Gtk css_provider
    self.style = bytes("""
      .speech-bubble {
        color: %s;
        background-color: %s;
        background-image: %s;
        border: 1px solid %s;
        background-size: cover;
        background-position: center;
      }
    """ % (self.foreground_color, self.background_color,
           self.__background_image, self.border_color), "utf-8")

def strip_string(text: str) -> str:
  return text.replace(" ","").replace("-", "") \
    .replace("_", "").replace(".", "").replace(",", "")


class DesktopApplication():
  """
  Wrapper class for Gio.AppInfo and Gio.DesktopAppInfo
  """

  def __init__(self, app_info: Gio.AppInfo):
    self.__id = app_info.get_id()
    self.__name = app_info.get_name()
    self.__icon = app_info.get_icon()
    self.__description = app_info.get_description()
    if self.__description is None or len(self.__description) == 0:
      self.__description = self.__name

    desktop_info = Gio.DesktopAppInfo.new(self.__id)
    self.__keywords = desktop_info.get_keywords()
    categories = desktop_info.get_categories()
    if categories is not None:
      self.__categories = categories.split(";")
      if self.__categories[len(self.__categories) - 1] is None:
        self.__categories = self.__categories[:-2]
    else:
      self.__categories = []
    self.__actions = {}

    actions = desktop_info.list_actions()

    for action in actions:
      self.__actions[desktop_info.get_action_name(action)] = action

    self.__launch_lambda = lambda : app_info.launch()
    self.__launch_action_lambda = lambda action_name : \
        desktop_info.launch_action(action_name, Gio.AppLaunchContext())


  def get_id(self):
    return self.__id


  def get_name(self) -> str:
    return self.__name


  def set_name(self, name):
    self.__name = name


  def get_description(self) -> str:
    return self.__description


  def match_keyword(self, query: str) -> bool:
    if len(query) > 2:
      for keyword in self.__keywords:
        if keyword.upper().startswith(query.upper()):
          return True

    return False


  def match_category(self, query:str) -> bool:
    for category in self.__categories:
      if query == category:
        return True

    return False


  def get_icon(self):
    return self.__icon


  def get_actions(self) -> dict:
    return self.__actions


  def launch(self) -> bool:
    return self.__launch_lambda()


  def launch_action(self, action_name) -> bool:
    return self.__launch_action_lambda(action_name)


def get_app_bubble(desktop_application: DesktopApplication):
  main_grid = Gtk.Grid()
  main_grid.set_row_spacing(4)
  main_grid.set_column_spacing(4)
  main_grid.set_margin_start(8)
  main_grid.set_margin_end(8)
  main_grid.set_margin_top(8)
  main_grid.set_margin_bottom(8)
  main_grid.set_size_request(150, 20)

  icon = Gtk.Image()
  icon.set_icon_size(Gtk.IconSize.LARGE)
  icon.set_valign(Gtk.Align.START)
  if desktop_application.get_icon() is not None:
    icon.set_from_gicon(desktop_application.get_icon())
  else:
    icon.set_from_icon_name("application-default-icon")
  main_grid.attach(icon, 0, 0, 1, 2)

  app_name = Gtk.Label()
  app_name.set_ellipsize(Pango.EllipsizeMode.END)
  app_name.set_text(desktop_application.get_name())
  app_name.get_style_context().add_class("h2")
  app_name.set_halign(Gtk.Align.START)
  main_grid.attach(app_name, 1, 0, 1, 1)

  if desktop_application.get_description() is not None:
    app_description = Gtk.Label()
    app_description.set_wrap(True)
    app_description.get_style_context().add_class("h6")
    app_description.set_halign(Gtk.Align.START)
    app_description.set_justify(Gtk.Justification.LEFT)
    app_description.set_text(desktop_application.get_description())
    main_grid.attach(app_description, 1, 1, 1, 1)

  actions = desktop_application.get_actions()

  if len(actions.keys()) > 0:
    action_menu = Gtk.Box()
    action_menu.set_orientation(Gtk.Orientation.VERTICAL)
    action_menu.set_spacing(4)

    for action_name in actions.keys():
      action_button = ActionButton()
      action_button.set_hexpand(True)
      action_button.set_desktop_app(desktop_application)
      action_button.set_action(action_name, actions[action_name])
      action_menu.append(action_button)

    main_grid.attach(action_menu, 0, 3, 2, 1)

  box = Gtk.Box()
  box.append(main_grid)

  return box


class ActionButton(Gtk.Button):
  """
  Action buttons are used to launch apps
  or their actions
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.__action = ""

    self.connect("clicked", self.__launch)


  def set_desktop_app(self, desktop_app:DesktopApplication):
    self.__desktop_app = desktop_app
    self.set_tooltip_text("Run " + desktop_app.get_name())


  def set_action(self, label: str, action: str):
    self.__action = action
    self.set_label(label)


  def __launch(self, obj):
    if self.__action != "":
      self.__desktop_app.launch_action(self.__action)
    else:
      self.__desktop_app.launch()

def get_icon_name_from_mime(mime: str):
  icon_name = ""
  if mime == "inode/directory":
    icon_name = "folder"
  elif "image" in mime:
    icon_name = "image-x-generic"
  elif "audio" in mime:
    icon_name = "audio-x-generic"
  elif "video" in mime:
    icon_name = "video-x-generic"
  elif "text" in mime:
    if mime == "text/css":
      icon_name = "text-css"
    elif mime == "text/html":
      icon_name = "text-html"
    elif mime == "text/x-python":
      icon_name = "text-x-python"
    elif mime == "text/x-bibtext":
      icon_name = "text-x-bibtext"
    elif mime == "text/x-go":
      icon_name = "text-x-go"
    elif mime == "text/x-install":
      icon_name = "text-x-install"
    elif mime == "text/x-readme":
      icon_name = "text-x-readme"
    elif mime == "text/x-sass":
      icon_name = "text-x-sass"
    elif mime == "text/x-vala":
      icon_name = "text-x-vala"
    elif mime == "text/csv":
      icon_name = "x-office-spreadsheet"
    else:
      icon_name = "text-x-generic"

    if Gtk.IconTheme().has_icon(icon_name):
      icon_name = "text-x-generic"

  elif "spreadsheet" in mime:
    icon_name = "x-office-spreadsheet"
  elif "presentation" in mime:
    icon_name = "x-office-presentation"
  elif "word" in mime:
    icon_name = "x-office-document"
  elif "font" in mime:
    icon_name = "font-x-generic"
  elif "application/pdf" in mime:
    icon_name = "application-pdf"
  else:
    icon_name = "unknown"

  return icon_name
