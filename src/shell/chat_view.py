#!/usr/bin/env python3
'''
Copyright 2021 Subhadeep Jasu <subhajasu@gmail.com>
Copyright 2019 Hannes Schulze <haschu0103@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later
'''

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk, GObject

#------------------CLASS-SEPARATOR------------------#

class ChatView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.make_ui()

    def make_ui(self):
        self.chat_box = Gtk.Box (Gtk.Orientation.VERTICAL, 0)
        self.chat_box.valign = Gtk.Align.START
        self.scrollable = Gtk.ScrolledWindow (None, None)
        self.scrollable.height_request = 196
        self.scrollable.get_style_context ().add_class ("chat-window")
        self.scrollable.add (self.chat_box)

        self.utterance_entry = Gtk.Entry ()
        self.utterance_entry.width_chars = 39
        self.utterance_entry.max_width_chars = 39
        self.utterance_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "mail-send-symbolic")

        self.attach (self.scrollable, 0, 0, 1, 1)
        # self.attach (suggest_area, 0, 1, 1, 1)
        self.attach (self.utterance_entry, 0, 1, 1, 1)

        self.margin_start = 15
