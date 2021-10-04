#!/usr/bin/env python3

import sys
from os import environ, path
from subprocess import call

prefix = sys.argv[1]
if prefix == '' or prefix == None:
    prefix = '/usr'
datadir = path.join(prefix, 'share')

print('Updating icon cache...')
call(['gtk-update-icon-cache', '-qtf', path.join(datadir, 'icons', 'hicolor')])
print("Installing new Schemas")
call(['glib-compile-schemas', path.join(datadir, 'glib-2.0/schemas')])
