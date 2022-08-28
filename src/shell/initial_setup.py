#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
This code implements the initial setup page which
is displayed when the app is launched for the first time.
For further details look in the InitialSetup class.
"""

# Base imports
import math
import random
import gi
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
#pylint: enable=wrong-import-position
from gi.repository import Gtk, Adw, GLib, GObject

# Gandiva imports
from config import settings

#--------------CLASS-SEPARATOR---------------#

class InitialSetup(Gtk.Box):
  """
  ## Initial Setup
  This provides an interface to let the users
  know of the various features of the app and
  the permissions needed.

  ### Permissions
  The user can consent to certain common functions
  that the skills may use.

  ### Slides
  It's divided into a number of slides which are
  shown one after the other namely:
  - Welcome
  - Voice Activation
  - Geo Location
  - Skills
  - A Final Slide to confirm that the user is done
  with them

  ### Text-to-Speech
  There is full text-to-speech output on the contents
  of the slides.
  """

  __gsignals__ = {
    "send_utterance": (GObject.SIGNAL_RUN_FIRST, bool,
            (str,)),
    "complete": (GObject.SIGNAL_RUN_FIRST, bool,
            ()),
  }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.__eye_coord_x = 0
    self.__eye_coord_y = 0
    self.__blinking = 0

    self.set_hexpand(True)
    self.set_orientation(Gtk.Orientation.VERTICAL)

    # Make the custom title bar of the window
    self.headerbar = Adw.HeaderBar()
    self.headerbar.get_style_context().add_class("flat")
    self.append(self.headerbar)

    self.prev_button = Gtk.Button()
    self.prev_button.set_label("Back")
    self.prev_button.set_sensitive(False)
    self.prev_button.connect("clicked", self.prev_slide)
    self.headerbar.pack_start(self.prev_button)

    self.next_button = Gtk.Button()
    self.next_button.set_label("Next")
    self.next_button.get_style_context().add_class("suggested-action")
    self.next_button.connect("clicked", self.next_slide)
    self.headerbar.pack_end(self.next_button)

    self.face_canvas = Gtk.DrawingArea()
    self.face_canvas.set_size_request(160, 160)
    self.face_canvas.set_draw_func(self.__draw)
    self.face_canvas.get_style_context().add_class("face-canvas")
    self.face_canvas.get_style_context().add_class("face-start-animation")
    GLib.timeout_add(66, self.__redraw)
    GLib.timeout_add(800, self.__canvas_animate_face)
    self.append(self.face_canvas)

    self.main_stack = Gtk.Stack()
    self.main_stack.set_transition_type(
        Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    self.append(self.main_stack)

    self.slide_index = 0

    self.slides = [
      "welcome-grid",
      "voice-activation",
      "geolocation",
      "skills",
      "all-setup"
    ]

    self.__n_slides = len(self.slides)

    self.utterances = []

    welcome_slide, utterance = self.get_welcome_slide()
    self.utterances += [utterance]

    voice_slide, utterance = self.get_voice_activation_slide()
    self.utterances += [utterance]

    geolocation_slide, utterance = self.get_geolocation_slide()
    self.utterances += [utterance]

    skill_slide, utterance = self.get_skill_slide()
    self.utterances += [utterance]

    final_slide, utterance = self.get_final_slide()
    self.utterances += [utterance]

    self.main_stack.add_named(welcome_slide, self.slides[0])
    self.main_stack.add_named(voice_slide, self.slides[1])
    self.main_stack.add_named(geolocation_slide, self.slides[2])
    self.main_stack.add_named(skill_slide, self.slides[3])
    self.main_stack.add_named(final_slide, self.slides[4])

    self.main_stack.set_visible_child_name(self.slides[0])


  def next_slide(self, obj):
    if self.slide_index < self.__n_slides - 1:
      self.slide_index += 1
      self.main_stack.set_visible_child_name(self.slides[self.slide_index])
      self.prev_button.set_sensitive(True)
      self.emit("send_utterance", self.utterances[self.slide_index])
    else:
      settings.set_first_run(False)
      self.emit("complete")


    if self.slide_index == self.__n_slides - 1:
      self.next_button.set_label("Start")
      self.face_canvas.get_style_context().add_class("hide")
    else:
      self.next_button.set_label("Next")
      self.face_canvas.get_style_context().remove_class("hide")



  def prev_slide(self, obj):
    if self.slide_index > 0:
      self.slide_index -= 1

    self.main_stack.set_visible_child_name(self.slides[self.slide_index])
    self.prev_button.set_sensitive(self.slide_index != 0)

    if self.slide_index == self.__n_slides - 1:
      self.next_button.set_label("Start")
      self.face_canvas.get_style_context().add_class("hide")
    else:
      self.next_button.set_label("Next")
      self.face_canvas.get_style_context().remove_class("hide")


  def __draw(self, widget, cr, width, height):
    self.__draw_eyes(cr, width, height, self.__eye_coord_x,
        self.__eye_coord_y, self.__blinking)

  def __redraw(self):
    self.face_canvas.queue_draw()
    return True


  def get_welcome_slide(self) -> Gtk.Widget:
    #pylint: disable=line-too-long
    utterance_text = """Project Gandiva is a virtual sidekick. It's an app that is ready to help you anytime you are in need.

    For the Project Gandiva to work to it's fullest extent, the app uses your voice input, notification data,
    location, etc. You can always change the permissions at any moment. The app does not send any personal
    data to any online service. However, certain skills may connect to the internet to fetch data"""
    #pylint: enable=line-too-long

    main_grid = Gtk.Grid()
    main_grid.set_halign(Gtk.Align.CENTER)

    self.header = Gtk.Label()
    self.header.set_text("Hi!")
    self.header.get_style_context().add_class("h1")
    self.header.get_style_context().add_class("hide")
    self.header.set_halign(Gtk.Align.END)
    main_grid.attach(self.header, 0, 0, 1, 1)

    self.sub_header = Gtk.Label()
    self.sub_header.set_text(" I am Gandiva")
    self.sub_header.get_style_context().add_class("h1")
    self.sub_header.get_style_context().add_class("hide")
    self.sub_header.set_halign(Gtk.Align.START)
    main_grid.attach(self.sub_header, 1, 0, 1, 1)

    sub_text = Gtk.Label()
    sub_text.set_text(utterance_text)
    sub_text.get_style_context().add_class("sub-text")
    sub_text.set_justify(Gtk.Justification.CENTER)
    main_grid.attach(sub_text, 0, 1, 2, 1)

    self.animate_first_slide()

    return main_grid, "Hi! I am Gandiva, " + utterance_text


  def get_voice_activation_slide(self) -> Gtk.Widget:
    #pylint: disable=line-too-long
    utterance_text = """You can summon me by calling out my name.

    Just say "Hey Gandiva!" and I will be right there to help you. You can turn this feature off
    if you want. If it's off then you can open the app and click on the mic button to speak to me
    or type something in the chat and send me."""
    #pylint: enable=line-too-long

    main_grid = Gtk.Grid()
    main_grid.set_halign(Gtk.Align.CENTER)

    header = Gtk.Label()
    header.set_text("Wake me when you need me")
    header.get_style_context().add_class("h1")
    main_grid.attach(header, 0, 0, 2, 1)

    sub_text = Gtk.Label()
    sub_text.set_text(utterance_text)
    sub_text.get_style_context().add_class("sub-text")
    sub_text.set_justify(Gtk.Justification.CENTER)
    main_grid.attach(sub_text, 0, 1, 2, 1)

    label = Gtk.Label()
    label.set_text("Voice Invoke: ")
    label.set_halign(Gtk.Align.END)
    main_grid.attach(label, 0, 2, 1, 1)

    switch = Gtk.Switch()
    switch.set_halign(Gtk.Align.START)
    switch.set_active(True)
    switch.connect("state_set", self.set_voice_activation_mode)
    main_grid.attach(switch, 1, 2, 1, 1)

    return main_grid, header.get_text() + ". " + utterance_text


  def set_voice_activation_mode(self, obj, active):
    settings.set_voice_activation_mode(active)
    return False


  def get_geolocation_slide(self) -> Gtk.Widget:
    #pylint: disable=line-too-long
    utterance_text = """I can connect to geolocation services to find out where we are.

    This information can be used by certain skills to give you location specific information,
    like weather, local news, etc."""
    #pylint: enable=line-too-long

    main_grid = Gtk.Grid()
    main_grid.set_halign(Gtk.Align.CENTER)

    header = Gtk.Label()
    header.set_text("Location Access")
    header.get_style_context().add_class("h1")
    main_grid.attach(header, 0, 0, 1, 1)

    sub_text = Gtk.Label()
    sub_text.set_text(utterance_text)
    sub_text.get_style_context().add_class("sub-text")
    sub_text.set_justify(Gtk.Justification.CENTER)
    main_grid.attach(sub_text, 0, 1, 1, 1)

    return main_grid, header.get_text() + ". " + utterance_text


  def get_skill_slide(self) -> Gtk.Widget:
    #pylint: disable=line-too-long
    utterance_text = """I can learn anything.

    I do that using skill plug-ins. These are small python scripts stored in a folder
    that I can learn how to respond to specific queries and function according to the
    scripts. Make sure you trust the author of skills you install. You can turn skills
    off or remove them at any time."""
    #pylint: enable=line-too-long

    main_grid = Gtk.Grid()
    main_grid.set_halign(Gtk.Align.CENTER)

    header = Gtk.Label()
    header.set_text("Skills")
    header.get_style_context().add_class("h1")
    main_grid.attach(header, 0, 0, 1, 1)

    sub_text = Gtk.Label()
    sub_text.set_text(utterance_text)
    sub_text.get_style_context().add_class("sub-text")
    sub_text.set_justify(Gtk.Justification.CENTER)
    main_grid.attach(sub_text, 0, 1, 1, 1)

    return main_grid, header.get_text() + ". " + utterance_text


  def get_final_slide(self) -> Gtk.Widget:
    main_grid = Gtk.Grid()
    main_grid.set_halign(Gtk.Align.CENTER)

    header = Gtk.Label()
    header.set_text("Awesome! You are all set!")
    header.get_style_context().add_class("h1")
    main_grid.attach(header, 0, 0, 1, 1)

    done_icon = Gtk.Image.new_from_icon_name("emblem-default")
    done_icon.set_icon_size(Gtk.IconSize.LARGE)
    done_icon.set_margin_top(40)
    main_grid.attach(done_icon, 0, 1, 1, 1)

    return main_grid, header.get_text()


  def animate_first_slide(self):
    GLib.timeout_add(2000, self.animate_h1_0)
    GLib.timeout_add(3000, self.animate_h1_1)



  def animate_h1_0(self):
    self.header.get_style_context().add_class("h1_animate_show")
    self.emit("send_utterance", self.utterances[0])
    return False


  def animate_h1_1(self):
    self.sub_header.get_style_context().add_class("h1_animate_show")
    return False


  def __canvas_animate_face(self):
    if random.random() < 0.5:
      self.__eye_coord_x = (random.random() - 0.5) * 10
      self.__eye_coord_y = (random.random() - 0.5) * 6
    elif random.random() < 0.2:
      self.__blinking = True
      GLib.timeout_add(200, self.__blink)
      pass

    return True


  def __draw_eyes(self, cr, width, height, coord_x, coord_y, closed):
    cr.set_line_width(2)

    if closed:
      cr.rectangle(coord_x + (width / 2) - 50, coord_y + (height / 2), 40, 3)
      cr.rectangle(coord_x + (width / 2) + 10, coord_y + (height / 2), 40, 3)
      cr.set_source_rgb(0.2, 0.2, 0.2)
      cr.fill()
    else:
      # Left eye
      cr.arc(coord_x + (width / 2) - 30,
             coord_y + (height / 2), 20, 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, 1)
      cr.fill()
      cr.arc(coord_x + (width / 2) - 30,
             coord_y + (height / 2), 20, 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, 1)
      cr.stroke()

      # Right eye
      cr.arc(coord_x + (width / 2) + 30,
             coord_y + (height / 2), 20, 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, (1 - 0) * (2 - 0))
      cr.fill()
      cr.arc(coord_x + (width / 2) + 30,
             coord_y + (height / 2), 20, 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, 1)
      cr.stroke()


  def __blink(self):
    self.__blinking = False
