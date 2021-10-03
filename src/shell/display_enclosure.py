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

class DisplayEnclosure(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mic_button = Gtk.Button.new_from_icon_name('audio-input-microphone', Gtk.IconSize.DIALOG)
        self.mic_button.get_style_context().remove_class('image_button')
        self.attach (self.mic_button, 0, 0, 1, 1)
