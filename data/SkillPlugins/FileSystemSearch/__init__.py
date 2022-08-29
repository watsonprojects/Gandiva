#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

"""
File system search skill for Gandiva
"""

#pylint: disable=invalid-name
#pylint: disable=unused-argument

from gandiva.core.skill_backend import Skill, Intent

class FileSystemSearchSkill(Skill):
  """
  This is an internal skill which allows Gandiva to search for files and folders
  based on the name or keyword. It also allows Gandiva to open specific
  libraries or special user folders as per _XDG Directory Specification_.
  The output is a speechbubble with a list of files and folder with buttons to
  open them using the default file manager of the OS.
  """

  def __init__(self, skill_backend):
    super().__init__(skill_backend)

    self.keyword_search_intent = Intent(
      'keyword_search',
      [
        '[find,search,show] all files by [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] all files [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] files by [name,keyword] {keyword,NN,JJ}',
        '[find,search,show] files [name,keyword] {keyword,NN,JJ}'
      ],
      'en-us'
    )

    self.register_intent(self.keyword_search_handler,
      self.keyword_search_intent, 'Search files by keyword wallpaper')

    self.library_intent = Intent(
      'library',
      [
        'open the xdg [folder,directory] of {library,NN,NNP}',
        'open xdg [folder,directory] of {library,NN,NNP}',
        'open {library,NN,NNP} library',
        'open [a,the] library of {library,NN,NNP}',
        'open library of {library,NN,NNP}'
      ],
      'en-us'
    )

    self.register_intent(self.library_handler,
      self.library_intent, 'Open Music Library')

    # self.attribute_search_intent = Intent(
    #   'attribute',
    #   [
    #     'search for files more than {value} {unit} older',
    #     'search for files {comparator} than {value} {unit}',
    #     'search for files of type {type}',
    #     'search for files of {type} type',
    #     '[search,find] files more than {value} {unit} older',
    #     '[search,find] files {comparator} than {value} {unit}',
    #     '[search,find] files of type {type}',
    #     '[search,find] files of {type} type',
    #     'search for all {type} files'
    #   ],
    #   'en-us'
    # )


  def keyword_search_handler(self, subjects, context, query, tags,
    lang:str, datadir:str):
    if 'keyword' in subjects.keys():
      return { 'type': 'internal-action', 'action': 'file-search-keyword',
        'value': subjects['keyword'] }

    return None


  def library_handler(self, subjects, context, query, tags, lang:str,
    datadir:str):
    if 'library' in subjects.keys():
      library = subjects['library'].upper()
      if library in ['HOME', 'DOCUMENT', 'DOCUMENTS', 'AUDIO', 'MUSIC',
                     'VIDEO', 'VIDEOS', 'PICTURE', 'PICTURES','PHOTO',
                     'PHOTOS', 'IMAGE', 'IMAGES', 'DOWNLOAD', 'DOWNLOADS',
                     'TEMPLATES']:
        return { 'type': 'internal-action', 'action': 'file-open-library',
          'value': library }
      else:
        return { 'type': 'text', 'value': 'Sorry, no such library exists' }

    return None
