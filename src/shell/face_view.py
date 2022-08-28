#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

#pylint: disable=unused-argument

"""
This file contains a FaceView class which
provides a memetic interface (a face) for the app.

There is also a Particle class which is used to
render the thinking animation

There is a LightRing Animator class for animating
the light ring around the face main button
"""

# Base imports
import math
import random
import gi
import _thread
import time
#pylint: disable=wrong-import-position
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
#pylint: enable=wrong-import-position
from gi.repository import Gdk, Gtk, GObject, Adw, GLib

import numpy
from numpy import double

# Gandiva imports

from config import settings

#--------------CLASS-SEPARATOR---------------#

class FaceView(Gtk.Box):
  """
  ## Face
  Provides a memetic visual interface for the user to gauge the AI system.
  ### Graphics
  It has three graphical modes:
  - Mic glyph (default)
  - Processing / thinking animation
  - Face with eyes (when the AI is speaking)

  ### Listen Button
  It also acts a button to start/stop listening.Clicking the button
  does the following:
  - When idle or in wakeword listening mode, start listening
  - When listening, cancel listening
  - When AI is speaking, stop the audio output
  """

  __gsignals__ = {
    "toggle_face_view": (GObject.SIGNAL_RUN_FIRST, bool,
            (bool,))
  }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # canvas animation variables
    self.__canvas_animation_type = 0
    self.__canvas_animation_func = self.__canvas_animate_bounce
    self.__canvas_animation_tick = 0
    self.__eye_coord_x = 0
    self.__eye_coord_y = 0
    self.__blinking = 0
    self.__mic_form = 1
    self.__mic_form_target = 1
    self.__thinking_form = 0
    self.__thinking_form_target = 0

    # loader variables
    self.particle_array = []
    self.__init_particle()

    # audio
    self.audio_buffer = bytes()


  def make_ui(self):
    """
    Make the UI widgets.
    """
    self.__main_button_callback = None
    self._voice_activation_mode_callback = None

    self.set_orientation(Gtk.Orientation.VERTICAL)
    self.get_style_context().add_class("darken")
    self.set_size_request(280, 160)
    self.set_hexpand(True)

    self.headerbar = Adw.HeaderBar()
    self.headerbar.get_style_context().add_class("flat")
    self.headerbar.set_show_start_title_buttons(False)
    self.headerbar.set_show_end_title_buttons(False)
    self.append(self.headerbar)

    self.hide_face_button = Gtk.Button()
    self.hide_face_button.set_icon_name("go-previous-symbolic")
    self.hide_face_button.set_visible(False)
    self.hide_face_button.connect("clicked", self.toggle_revealer)
    self.headerbar.pack_end(self.hide_face_button)

    self.toggle_box = Gtk.Box()
    self.toggle_box.get_style_context().add_class("linked")
    self.headerbar.set_title_widget(self.toggle_box)

    self.toggle_detection_verbal = Gtk.ToggleButton()
    self.toggle_detection_verbal.set_label("Verbal Invoke")
    self.toggle_detection_verbal.set_active(True)
    self.toggle_box.append(self.toggle_detection_verbal)

    self.toggle_detection_manual = Gtk.ToggleButton()
    self.toggle_detection_manual.set_label("Manual Invoke")
    self.toggle_detection_manual.set_group(self.toggle_detection_verbal)
    self.toggle_box.append(self.toggle_detection_manual)

    self.toggle_detection_verbal.connect("toggled",
                                         self.toggle_button_handler)
    self.toggle_detection_verbal.set_active(
        settings.get_voice_activation_mode())
    self.toggle_detection_manual.set_active(not
        settings.get_voice_activation_mode())

    self.main_button_container = Gtk.Box()
    self.main_button_container.set_vexpand(True)
    self.main_button_container.set_halign(Gtk.Align.CENTER)
    self.append(self.main_button_container)

    self.listen_button = Gtk.Button()
    self.listen_button.get_style_context().add_class("listen-button")
    self.listen_button.get_style_context().add_class("squishy-button")
    self.listen_button.set_halign(Gtk.Align.CENTER)
    self.listen_button.set_valign(Gtk.Align.CENTER)
    self.listen_button.set_size_request(160, 160)
    self.main_button_container.append(self.listen_button)

    self.listen_button_face = Gtk.Box()
    self.listen_button_face.get_style_context().add_class("listen-button-face")
    self.listen_button_face.set_halign(Gtk.Align.CENTER)
    self.listen_button_face.set_valign(Gtk.Align.CENTER)
    self.listen_button_face.set_size_request(160, 160)
    self.listen_button.connect("clicked", self.start_listening)
    self.listen_button.set_child(self.listen_button_face)

    self.face_canvas = Gtk.DrawingArea()
    self.face_canvas.set_hexpand(True)
    self.face_canvas.set_vexpand(True)
    self.face_canvas.set_draw_func(self.__draw)
    GLib.timeout_add(66, self.__redraw)
    GLib.timeout_add(500, self.__canvas_animation_func)
    self.listen_button_face.append(self.face_canvas)

    self.__light_ring_animator = LightRingAnimator(
        self.__animation_start_handler,
        self.__animation_end_handler)


  def toggle_button_handler(self, toggle_button):
    settings.set_voice_activation_mode(toggle_button.get_active())
    if self._voice_activation_mode_callback is not None:
      self._voice_activation_mode_callback(toggle_button.get_active())


  def show_extra_controls(self, show: bool):
    """
    Show certain controls that are hidden for responsive UI.
    """
    self.hide_face_button.set_visible(show)


  def toggle_revealer(self, event):
    self.emit("toggle_face_view", True)


  def start_listening(self, event):
    if self.__main_button_callback is not None:
      self.__main_button_callback()


  def connect_event(self, event_type:str, callback):
    if event_type == "main-button-clicked":
      self.__main_button_callback = callback
    elif event_type == "voice-activation-mode-changed":
      self._voice_activation_mode_callback = callback


  def light_ring_animate_recognition(self, value):
    if self.__mic_form_target > 0.5:
      self.__light_ring_animator.set_animation_type(1)
      self.__light_ring_animator.set_value(value)

  def light_ring_animate_talking(self, value):
    self.__light_ring_animator.set_animation_type(2)
    self.__light_ring_animator.set_value(value)


  def light_ring_animation_begin(self):
    self.__light_ring_animator.begin_animation()


  def light_ring_animation_end(self):
    self.__light_ring_animator.end_animation()


  def __animation_start_handler(self):
    self.listen_button.get_style_context().add_class("listen-button-animating")


  def __animation_end_handler(self):
    self.__light_ring_animator.set_animation_type(0)
    self.listen_button.get_style_context().remove_class(
        "listen-button-animating")


  def set_talking_audio(self, buffer:bytes):
    self.audio_buffer = buffer


  def start_talking(self):
    self.__mic_form_target = 0
    self.__thinking_form_target = 0


  def stop_talking(self):
    self.__mic_form_target = 1
    self.__thinking_form_target = 0


  def start_thinking(self):
    self.__mic_form_target = 0
    self.__thinking_form_target = 1


  def stop_thinking(self):
    self.__thinking_form_target = 0

  # Drawing functions:
  def __draw(self, widget, cr, width, height):
    if self.audio_buffer is not None and self.__mic_form < 0.1:
      self.__draw_talking_indicator(cr, width, height,
                                    self.__eye_coord_x * (1 - self.__mic_form),
                                    self.__eye_coord_y * (1 - self.__mic_form),
                                    self.audio_buffer)
    self.__draw_eyes(cr, width, height,
                    self.__eye_coord_x * (1 - self.__mic_form),
                    self.__eye_coord_y * (1 - self.__mic_form),
                    self.__blinking, self.__mic_form, self.__thinking_form)
    if self.__thinking_form > 0.1:
      self.__draw_loader(cr, width, height, 0)


  def __redraw(self):
    if self.__canvas_animation_type == 0:
      self.__canvas_animation_func = self.__canvas_animate_bounce

    if self.__canvas_animation_tick > 1:
      self.__canvas_animation_tick = 0
    else:
      self.__canvas_animation_tick += 0.06

    self.__update(self.__canvas_animation_tick, 0.06)
    self.face_canvas.queue_draw()
    return True


  def __update(self, animation_progress, delta_time):
    self.__mic_form = self.__interp(self.__mic_form,
                                    self.__mic_form_target, 8, delta_time)
    self.__thinking_form = self.__interp(self.__thinking_form,
                                         self.__thinking_form_target,
                                         6, delta_time)


  def __canvas_animate_bounce(self):
    if self.__mic_form < 0.1 and self.__thinking_form < 0.1:
      if random.random() < 0.5:
        self.__eye_coord_x = (random.random() - 0.5) * 10
        self.__eye_coord_y = (random.random() - 0.5) * 6
      elif random.random() < 0.2:
        self.__blinking = True
        GLib.timeout_add(200, self.__blink)

    return True


  def __blink(self):
    self.__blinking = False


  def __interp(self, current:double, target:double,
               speed:double, delta_time:double):
    return current + (target - current) * speed * delta_time


  def __draw_eyes(self, cr, width, height, coord_x, coord_y,
                  closed, mic_form, center):
    cr.set_line_width(2)

    if closed:
      cr.rectangle(coord_x + (width / 2) - 50, coord_y + (height / 2), 40, 3)
      cr.rectangle(coord_x + (width / 2) + 10, coord_y + (height / 2), 40, 3)
      cr.set_source_rgb(0.2, 0.2, 0.2)
      cr.fill()
    else:
      # Left eye
      cr.arc(coord_x + (width / 2) - 30 * (1 - mic_form) * (1 - center),
        coord_y + (height / 2) - 26 * mic_form * (1 - center),
        16 + (4 * (1 - mic_form)) + (center * 10), 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2,
        (1 - self.__mic_form) * (1.5 - self.__thinking_form))
      cr.fill()
      cr.arc(coord_x + (width / 2) - 30 * (1 - mic_form) * (1 - center),
        coord_y + (height / 2) - 26 * mic_form * (1 - center),
        16 + (4 * (1 - mic_form)) + (center * 10),
        math.pi * self.__mic_form, 2 * math.pi)
      cr.set_source_rgba(0.2 + self.__thinking_form,
        0.2 + (self.__thinking_form * 0.5), 0.2, 1)
      cr.stroke()

      # Right eye
      cr.arc(coord_x + (width / 2) + 30 * (1 - mic_form) * (1 - center),
        coord_y + (height / 2) + 6 * mic_form * (1 - center),
        16 + (4 * (1 - mic_form)), 0, 2 * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2,
        (1 - self.__mic_form) * (2 - self.__thinking_form))
      cr.fill()
      cr.arc(coord_x + (width / 2) + 30 * (1 - mic_form) * (1 - center),
        coord_y + (height / 2) + 6 * mic_form * (1 - center),
        16 + (4 * (1 - mic_form)), 0, (2 - self.__mic_form) * math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, 1)
      cr.stroke()
      cr.arc((width / 2) + 30 * (1 - mic_form) * (1 - center),
        (height / 2) + 6 * mic_form * (1 - center),
        24 + (4 * (1 - mic_form)), 0, math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, self.__mic_form)
      cr.stroke()

    # Draw mic outlines
    if mic_form > 0.01 and center < 0.9:
      cr.move_to((width / 2) - 16, (height / 2) - 26)
      cr.line_to((width / 2) - 16, (height / 2) + 6)
      cr.set_source_rgba(0.2, 0.2, 0.2, mic_form * (1 - center))
      cr.stroke()
      cr.move_to((width / 2) + 16, (height / 2) - 26)
      cr.line_to((width / 2) + 16, (height / 2) + 6)
      cr.set_source_rgba(0.2, 0.2, 0.2, mic_form * (1 - center))
      cr.stroke()
      cr.arc((width / 2) - 12, (height / 2) + 30, 10, 0, math.pi / 2)
      cr.set_source_rgba(0.2, 0.2, 0.2, mic_form * (1 - center))
      cr.stroke()
      cr.arc((width / 2) + 12, (height / 2) + 30, 10, math.pi / 2, math.pi)
      cr.set_source_rgba(0.2, 0.2, 0.2, mic_form * (1 - center))
      cr.stroke()
      cr.set_source_rgba(0.2, 0.2, 0.2, mic_form * (1 - center))
      cr.rectangle((width / 2) - 20, (height / 2) + 40, 40, 5)
      cr.stroke()

  # Reference: https://codepen.io/MinzCode/pen/yLaZOoV
  def __draw_loader(self, cr, width, height, animation_progress):
    cr.set_line_width(1)
    for particle in self.particle_array:
      particle.update(width, height, self.__thinking_form)
      particle.draw(cr, width, height, self.__thinking_form)
    for particle in self.particle_array:
      self.__draw_connection(cr, particle, width, height)


  def __draw_connection(self, cr, particle, w, h):
    for p in self.particle_array:
      center_distance = math.sqrt(math.pow(w/2 - p.x, 2) \
        + math.pow(h/2 - p.y, 2))
      distance = math.sqrt(math.pow(p.x - particle.x, 2) \
        + math.pow(p.y - particle.y, 2))
      opacity = (1 - distance / p.link_radius) \
        * (center_distance / 40) * self.__thinking_form
      if opacity > 0:
        cr.set_source_rgba(0.7, 0, opacity, opacity)
        cr.move_to(p.x, p.y)
        cr.line_to(particle.x, particle.y)
        cr.stroke()

  def __init_particle(self):
    if len(self.particle_array) == 0:
      for _ in range(50):
        x = 80.0 + (40.0 * math.sqrt(random.random())) \
            * math.cos(random.random() * 2.0 * math.pi)
        y = 80.0 + (40.0 * math.sqrt(random.random())) \
            * math.sin(random.random() * 2.0 * math.pi)
        particle = Particle(x, y)
        self.particle_array += [particle]
    else:
      for p in self.particle_array:
        x = 80.0 + (40.0 * math.sqrt(random.random())) \
            * math.cos(random.random() * 2.0 * math.pi)
        y = 80.0 + (40.0 * math.sqrt(random.random())) \
            * math.sin(random.random() * 2.0 * math.pi)
        p.randomize(x, y)


  def __draw_talking_indicator(self, cr, width, height,
                               x, y, audio_buffer:bytes):
    n = len(audio_buffer) / 32
    if n > 0:
      d = 2.0 * math.pi / n

      cr.set_source_rgba(0.9, 0.24, 0.5, (1 - self.__mic_form))
      cr.set_line_width(2)
      cr.arc(x + width / 2, y + height / 2, 30, 0, 2 * math.pi)
      cr.stroke()

      try:
        arr1 = numpy.fromstring(audio_buffer, dtype="int")

        for i in range((int)(n)):
          arr = numpy.fromstring(audio_buffer[i*8:][:8], dtype="int8")
          clamped = min(max(numpy.abs(arr).mean(), 20), 80)
          cr.arc(x + width / 2, y + height / 2,
            32 + clamped * 0.2 * (1 - self.__mic_form) \
            * (1 - self.__thinking_form),
            i * d, i * d + d)
          cr.set_source_rgba(clamped / 20, 0.8 \
            * clamped / 40, 1 - (clamped / 80),
            (1 - self.__mic_form))
          cr.set_line_width(1 if clamped < 40 else 2)
          cr.stroke()

        self.light_ring_animate_talking(numpy.abs(arr1).mean() * 150)
      except ValueError:
        pass



class Particle():
  """
  ### A 2D dot graphics
  """
  def __init__(self, x, y):
    self.size = 3
    self.link_radius = 20
    self.randomize(x, y)


  def randomize(self, x, y):
    self.x = x
    self.y = y
    self.init_x = self.x
    self.init_y = self.y
    self.speed = 1 + random.random() * 2
    self.density = random.random() * 30 + 1
    self._direction_angle = math.floor(random.random() * 360)
    self._vector = [
      math.cos(self._direction_angle) * self.speed,
      math.sin(self._direction_angle) * self.speed
    ]


  def update(self, width, height, radius_mod):
    self.border(width, height, 50 * (max(radius_mod, 0.1)))
    self.x += self._vector[0]
    self.y += self._vector[1]
    pass


  def border(self, w, h, radius_mod):
    center_distance = math.sqrt(math.pow(w/2 - self.x, 2) \
        + math.pow(h/2 - self.y, 2))

    if center_distance > radius_mod:
      self._vector[0] *= -1
      self._vector[1] *= -1
    if self.x < w/2 - radius_mod:
      self.x = w/2 - radius_mod
    if self.y < h/2 - radius_mod:
      self.y = h/2 - radius_mod
    if self.x > w/2 + radius_mod:
      self.x = w/2 + radius_mod
    if self.y > h/2 + radius_mod:
      self.y = h/2 + radius_mod


  def draw(self, cr, w, h, opacity):
    center_distance = math.sqrt(math.pow(w/2 - self.x, 2) \
        + math.pow(h/2 - self.y, 2))
    cr.set_source_rgba(1, 0.7, 0, min((1 - center_distance/40) \
        * opacity, 1))
    cr.arc(self.x, self.y, self.size, 0, 2 * math.pi)
    cr.fill()



class LightRingAnimator():
  """
  ## Light Ring Animator

  This takes care of animating the light ring
  which is around the face main button.
  The light ring has an animation for:
  - Speech Recognition mic intensity
  - TTS audio output intensity
  """

  def __init__(self, animation_start_callback, animation_end_callback):
    self.__animation_enabled = False

    self.__top_color = "#808080"
    self.__center_color = "#6B6B6B"
    self.__bottom_color = "#595959"
    self.__center_stop = 50

    self._animation_mode = 0

    self.__css = ".listen-button { background: \
      linear-gradient(to bottom, %s 0%%, %s %d%%, %s 100%%); }"

    self.__css_provider = Gtk.CssProvider()

    self.__start_callback = animation_start_callback
    self.__end_callback = animation_end_callback


  def begin_animation(self):
    if not self.__animation_enabled:
      self.__animation_enabled = True
      _thread.start_new_thread(self.__animation_thread, ())


  def end_animation(self):
    self.__animation_enabled = False


  def __animation_thread(self):
    if self.__start_callback is not None:
      self.__start_callback()

    while self.__animation_enabled:
      self.__animate()
      time.sleep(0.2)

    if self.__end_callback is not None:
      self.__end_callback()
      self.__center_stop = 50
      self.__animate()


  def set_animation_type(self, animation_type: int):
    if animation_type != self._animation_mode:
      self._animation_mode = animation_type
      if animation_type == 0:
        self.__top_color = "#808080"
        self.__center_color = "#6B6B6B"
        self.__bottom_color = "#595959"
      elif animation_type == 1:
        self.__top_color = "#808080"
        self.__center_color = "#3689E6"
        self.__bottom_color = "#64BAFF"
      elif animation_type == 2:
        self.__top_color = "#808080"
        self.__center_color = "#DE3E80"
        self.__bottom_color = "#F9C440"
      elif animation_type == 3:
        self.__top_color = "#CE9EF8"
        self.__center_color = "#A56CE2"
        self.__bottom_color = "#743BB5"


  def set_value(self, value, is_random=False):
    if is_random:
      self.__center_stop = random.random() * 100
    else:
      val = max(400, min(2000, value))
      # print(val)
      self.__center_stop = 101 - ((val / 2000) * 100)


  def __animate(self):
    GLib.idle_add(self.__set_css)


  def __set_css(self):
    provider_data = self.__css % (self.__top_color, self.__center_color,
                                  self.__center_stop, self.__bottom_color)
    self.__css_provider.load_from_data(bytes(provider_data, "utf-8"))
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),
                                            self.__css_provider, 800)
