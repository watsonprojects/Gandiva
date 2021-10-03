#!/usr/bin/env python3
'''
Copyright 2021 Subhadeep Jasu <subhajasu@gmail.com>
Copyright 2019 Hannes Schulze <haschu0103@gmail.com>
Copyright 2020 Adi Hezral <hezral@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later
'''

import sys, os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gio, Gdk, Granite, GObject, Pango

# Gandiva imports
from display_enclosure import DisplayEnclosure
from chat_view import ChatView

#------------------CLASS-SEPARATOR------------------#


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- variables --------#
        app = self.props.application

        #-- view --------#
        self.enclosure_display = DisplayEnclosure()
        self.chatbox = ChatView()
        self.separator = Gtk.Separator.new(Gtk.Orientation.VERTICAL)

        self.main_grid = Gtk.Grid ()
        self.main_grid.attach (self.enclosure_display, 0, 0, 1, 1)
        self.main_grid.attach (self.separator, 1, 0, 1, 1)
        self.main_grid.attach (self.chatbox, 2, 0, 1, 1)
        self.main_grid.valign = Gtk.Align.CENTER


        #-- stack --------#
        stack = Gtk.Stack()
        stack.props.transition_type = Gtk.StackTransitionType.UNDER_UP
        stack.add_named(self.main_grid, "main-grid")

        #-- header --------#
        headerbar = self.generate_headerbar(settings_view=None)

        #-- MainWindow construct--------#
        self.props.resizable = False #set this and window will expand and retract based on child
        self.title = "Gandiva"
        self.set_keep_above(True)
        self.get_style_context().add_class("rounded")
        self.set_size_request(600, -1) #set width to -1 to expand and retract based on content
        self.props.window_position = Gtk.WindowPosition.MOUSE
        self.set_titlebar(headerbar)
        self.add(stack)

        #-- QuickWordWindow variables--------#

        # this is for tracking window state flags for persistent mode
        self.state_flags_changed_count = 0
        self.active_state_flags = ['GTK_STATE_FLAG_NORMAL', 'GTK_STATE_FLAG_DIR_LTR']

        self.on_start_settings()

    def on_start_settings(self):
        # read user saved settings
        gio_settings = Gio.Settings(schema_id="com.github.watsonprojects.gandiva")
        if not gio_settings.get_value("persistent-mode"):
            self.state_flags_on = self.connect("state-flags-changed", self.on_persistent_mode)
            # print('state-flags-on')
        if gio_settings.get_value("sticky-mode"):
            self.stick()

    def generate_headerbar(self, settings_view):
        header_label = Gtk.Label("Gandiva")
        header_label.props.vexpand = True
        header_label.get_style_context().add_class("gandiva-header")

        headerbar = Gtk.HeaderBar()
        headerbar.pack_start(header_label)
        headerbar.props.decoration_layout = "close:maximize"
        headerbar.props.show_close_button = True
        headerbar.get_style_context().add_class("default-decoration")
        headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)
        return headerbar

    def on_persistent_mode(self, widget, event):
        # state flags for window active state
        self.state_flags = self.get_state_flags().value_names
        # print(self.state_flags)
        if not self.state_flags == self.active_state_flags and self.state_flags_changed_count > 1:
            self.destroy()
        else:
            self.state_flags_changed_count += 1
