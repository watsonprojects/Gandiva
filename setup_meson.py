#!/usr/bin/python3
'''
Copyright 2021 Subhadeep Jasu <subhajasu@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later
'''

from distutils.core import setup
from distutils.command.install import install

import pathlib, os, shutil
from os import path
from subprocess import call


# Base application info
base_rdnn = 'com.github.watsonprojects'
app_name = 'gandiva'
app_id = base_rdnn + '.' + app_name
app_url = 'https://github.com/watsonprojects/' + app_name
saythanks_url = ''

# Setup file paths for data files
# Check Flatpak
flatpak_sandbox = os.path.isfile("/.flatpak-info")

if flatpak_sandbox:
    prefix = '/app'
else:
    prefix = '/usr'
prefix_data = path.join(prefix, 'share')
install_path = path.join(prefix_data, app_id)
src_path = path.join(install_path, 'gandiva')
shell_path = path.join(src_path, 'shell')
data_path = path.join(install_path, 'data')


# Setup install data list
install_data = [(data_path, ['data/application.css']),
                (src_path,  ['gandiva' + '/__init__.py']),
                (src_path,  ['gandiva' + '/gandiva.py']),
                (shell_path,['gandiva' + '/shell/__init__.py']),
                (shell_path,['gandiva' + '/shell/custom_shortcut_settings.py']),
                (shell_path,['gandiva' + '/shell/display_enclosure.py']),
                (shell_path,['gandiva' + '/shell/chat_view.py']),
                (shell_path,['gandiva' + '/shell/main_window.py'])]
print ("data goes in " + data_path)

setup(
    name=app_name,  # Required
    license='GNU GPL3',
    version='0.0.1',  # Required
    url=app_url,  # Optional
    author='Subhadeep Jasu',  # Optional
    author_email='subhajasu@gmail.com',  # Optional
    scripts=[app_id],
    packages=['gandiva', 'gandiva.shell', 'gandiva.core'],
    data_files=install_data  # Optional
    # cmdclass={
    #     'install': PostInstall,
    # }
)
