#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Meson post install script
"""

import sys
from os import environ, path
from subprocess import call

prefix = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
if prefix == "" or prefix is None:
  prefix = "/usr"
datadir = path.join(prefix, "share")
destdir = environ.get('DESTDIR', '')

if not destdir:
  print("Updating icon cache…")
  call(["gtk-update-icon-cache", "-qtf", path.join(datadir, "icons", "hicolor")])
  print("Installing new Schemas")
  call(["glib-compile-schemas", path.join(datadir, "glib-2.0/schemas")])
