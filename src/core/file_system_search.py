#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
This file has code to index file and folder found in the `home` directory which
is given by `HOME` environment variable, and provide a fast search capability.
"""

# Base imports
import sqlite3
import os
import mimetypes
from gi.repository import GLib
from config import constants

#--------------CLASS-SEPARATOR---------------#

class FileSystemSearch():
  """
  ## File System Search
  Indexes file and folder found in the `home`
  directory which is given by `HOME` environment variable,
  and provides a fast search capability.
  """

    # DB query expressions
  CREATE_TABLE_QUERY = """
    CREATE TABLE file_system (
          fid INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          path TEXT NOT NULL
      )
  """
  CREATE_INDEX_QUERY = "CREATE INDEX fs_index ON \
    file_system (name, path)"
  INSERT_FILE_QUERY = """
    INSERT INTO file_system (name, type, path)
    VALUES (?, ?, ?)
  """
  SEARCH_QUERY = """
    SELECT name, type, path
      FROM file_system
      WHERE name LIKE ?
  """
  REDUNDANCY_CHECK_QUERY = "SELECT fid FROM file_system WHERE \
    name = ? AND path = ?"

  def __init__(self):
    # DB setup
    self.__db_location = GLib.get_user_cache_dir() + "/" \
      + constants.APPLICATION_ID
    if not os.path.exists(self.__db_location):
      os.mkdir(self.__db_location)
    self.__db_location += "/databases"
    if not os.path.exists(self.__db_location):
      os.mkdir(self.__db_location)

    self.__db_location += "/file_system.db"
    self.__usr_home = GLib.get_home_dir()


  def __create_tables(self):
    """
    (Re)Create tables.
    """
    # Create table
    self.__db_conn.execute(FileSystemSearch.CREATE_TABLE_QUERY)
    # Create index
    self.__db_conn.execute(FileSystemSearch.CREATE_INDEX_QUERY)
    self.__db_conn.commit()


  def index_files(self, force: bool):
    """
    Store all the file locations and other details in the DB
    and index them using sqlite3 indexing.
    """
    # If forced, delete the DB and create a new one
    if force:
      if os.path.exists(self.__db_location):
        os.remove(self.__db_location)
      self.__db_conn = sqlite3.connect(self.__db_location)
      self.__create_tables()
    else:
      if not os.path.exists(self.__db_location):
        self.__db_conn = sqlite3.connect(self.__db_location)
        self.__create_tables()
      else:
        self.__db_conn = sqlite3.connect(self.__db_location)

    self.__db_cursor = self.__db_conn.cursor()
    try:
      self.__scan_directories_recursive(self.__usr_home)
      self.__db_conn.commit()
    except sqlite3.Error as error:
      print("Failed to index some files", error)
    finally:
      if self.__db_conn:
        self.__db_conn.close()


  def __scan_directories_recursive(self, path):
    """
    Discover files and folders recursively within the user home folder.
    """
    # https://stackoverflow.com/questions/18394147/how-to-do-a-recursive-sub-folder-search-and-return-files-in-a-list
    sub_directories = []

    for dir_entry in os.scandir(path):
      print(dir_entry)
      if not (dir_entry.name.startswith(".") or
        # ignore build system files
        dir_entry.name == "build" or
        dir_entry.name == "builddir" or
        dir_entry.name == "_build"):
        if dir_entry.is_dir():
          sub_directories += [dir_entry]
          self.__insert_path_to_db(dir_entry.name,
            "inode/directory", dir_entry.path)
        if dir_entry.is_file():
          self.__insert_path_to_db(dir_entry.name, mimetypes.MimeTypes()\
            .guess_type(dir_entry.path)[0], dir_entry.path)


    for dir_path in sub_directories:
      other_sub_directories = self.__scan_directories_recursive(dir_path.path)
      sub_directories.extend(other_sub_directories)

    return sub_directories


  def __insert_path_to_db(self, name, ftype, path: str):
    """
    Insert the discovered path to DB.
    """
    self.__db_cursor.execute(FileSystemSearch.REDUNDANCY_CHECK_QUERY,
      ( name, path[:-len(name)] ))
    if len(self.__db_cursor.fetchall()) == 0:
      self.__db_cursor.execute(FileSystemSearch.INSERT_FILE_QUERY,
        ( name, ftype if ftype is not None else "unknown", path[:-len(name)] ))


  def search_file(self, query_text: str, fetch_all = False) -> list:
    """
    Search for files or folders from the DB based on the given keyword.

    :param query_text: Keyword to search
    :type query_text: str
    :param fetch_all: Whether or not to fetch all results instead of first five
    :type fetch_all: bool
    """
    if query_text == "":
      return []
    self.__db_conn = sqlite3.connect(self.__db_location)
    self.__db_cursor = self.__db_conn.cursor()
    results = []
    searched = False
    try:
      self.__db_cursor.execute(FileSystemSearch.SEARCH_QUERY \
        + ("" if fetch_all else " LIMIT 5"), ("%" + query_text + "%", ))
      results = self.__db_cursor.fetchall()
      searched = True
    except Exception as e:
      print("[FileSystemSearch] No index found:", e)
    finally:
      self.__db_conn.close()
    return results, searched
