#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This file has a SystemPortal class which has functions that the skills can use
for various operations like, fetching data from the internet,
finding location, etc. It all goes through one central place.
"""

# Base imports
import requests
import subprocess
import geocoder

#--------------CLASS-SEPARATOR---------------#

class SystemPortal():
  """
  ## System Portal
  Connect to OS services using methods in this class.
  """

  # Error codes
  ERROR_NO_INTERNET = 0
  ERROR_NO_XDG_OPEN = 1
  ERROR_NO_GEO_LOCATION = 2

  def __init__(self):
    # Error callback
    self.__error_callback = None


  def connect_error_callback(self, callback):
    self.__error_callback = callback


  def handle_error(self, error_type:int):
    if self.__error_callback is not None:
      self.__error_callback(error_type)


  def http_get(self, url:str, params, auth=None):
    """
    Fetch data from an internet API.

    :param url: Uniform Resource Locator string or address of the API
    :type url: str
    :param params: Paramters supported by the API for HTTPGET request
    """
    response = None
    try:
      session = requests.Session()
      response = session.get(url=url, params=params, auth=auth, timeout=20)
    except:
      self.handle_error(SystemPortal.ERROR_NO_INTERNET)

    return response


  def open_uri(self, URI:str):
    """
    Opan a file or web resource based on the URI in the
    default app set by the OS.

    :params URI: path of the file or web resource
    :type URI: str
    """
    try:
      subprocess.call(('xdg-open', URI))
      return True
    except:
      self.handle_error(SystemPortal.ERROR_NO_XDG_OPEN)
      return False


  def get_location(self):
    """
    Get current location of the computer based on IP address.
    """
    latlng = None
    try:
      geo = geocoder.ip('me')
      latlng = geo.latlng
    except:
      self.handle_error(SystemPortal.ERROR_NO_GEO_LOCATION)

    return latlng
