#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Settings to be accessible through out the application
"""

import gi

#pylint: disable=global-variable-undefined
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
#pylint: enable=wrong-import-position
from gi.repository import Gio

def init(app_id:str):
  """
  Initialize global settings using Gio.Settings

  :param app_id: The RDNN of the application which is the schema id
  :type app_id: str
  """
  global _GIO_SETTINGS
  _GIO_SETTINGS = Gio.Settings(schema_id=app_id)


def get_first_run() -> bool:
  return _GIO_SETTINGS.get_boolean('first-run')


def set_first_run(done: bool):
  _GIO_SETTINGS.set_boolean('first-run', done)


def get_voice_activation_mode() -> bool:
  return _GIO_SETTINGS.get_boolean('voice-invoke')


def set_voice_activation_mode(active: bool):
  _GIO_SETTINGS.set_boolean('voice-invoke', active)
