#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
Constants to be used through out the application
"""

#pylint: disable=global-variable-undefined

import os
import sys


def init(app_id: str, datadir: str, version: str):
  """
  Initialize global constants

  :param app_id: The RDNN of the application
  :type app_id: str
  :param datadir: The user data directory
  :type datadir: str
  :param version: The version string of the application
  :type version: str
  """

  global APPLICATION_ID
  APPLICATION_ID = app_id

  global VERSION
  VERSION = version
  # Set launch directory
  global LAUNCH_DIR
  LAUNCH_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

  # Check Flatpak
  global IS_FLATPAK
  IS_FLATPAK = os.path.isfile("/.flatpak-info")

  # Get data path
  global DATA_PATH
  DATA_PATH = datadir + "/data"
