#!/usr/bin/env python3
'''
Gtk application module for Gandiva


Copyright 2021 Subhadeep Jasu <subhajasu@gmail.com>
Copyright 2019 Hannes Schulze <haschu0103@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later
'''

# base imports
import sys, os

# gtk imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk, GObject

# thread import
from threading import Thread
from datetime import datetime

# Gandiva imports
from shell.main_window import MainWindow
from shell.custom_shortcut_settings import CustomShortcutSettings

#------------------CLASS-SEPARATOR------------------#

class GandivaApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set application properties
        self.props.application_id = "com.github.watsonprojects.gandiva"

        # initialize objects
        self.window = None

        gio_settings = Gio.Settings(schema_id="com.github.watsonprojects.gandiva")
        self.first_run = gio_settings.get_value("first-run")

        # Set shortcut
        SHORTCUT = "<Super>g"
        ID = "gtk-launch" + " " + self.props.application_id

        _custom_shortcut_settings = CustomShortcutSettings()

        has_shortcut = False
        for shortcut in _custom_shortcut_settings.list_custom_shortcuts():
            if shortcut[1] == ID:
                has_shortcut = True

        if has_shortcut is False:
            shortcut = _custom_shortcut_settings.create_shortcut()
            if shortcut is not None:
                _custom_shortcut_settings.edit_shortcut(shortcut, SHORTCUT)
                _custom_shortcut_settings.edit_command(shortcut, ID)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # setup quiting app using Escape, Ctrl+Q
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>Q", "Escape"])

        # set CSS provider
        provider = Gtk.CssProvider()
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "..", "data", "application.css"))

        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # prepend custom path for icon theme
        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "data", "icons"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if self.window is None:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(application=self)
            self.add_window(self.window)
            self.window.show_all()

        if self.first_run:
            print ("First run")

    def after_activate(self, app):
        if not self.first_run:
            print ("Not first run")

    def on_quit_action(self, action, param):
        if self.window is not None:
            self.window.destroy()

class RunInBackground(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        #print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,**self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return
