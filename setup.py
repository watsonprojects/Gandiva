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
prefix = '/usr'
prefix_data = path.join(prefix, 'share')
install_path = path.join(prefix_data, app_id)
src_path = path.join(install_path, 'gandiva')
shell_path = path.join(src_path, 'shell')
data_path = path.join(install_path, 'data')


# Setup install data list
install_data = [(prefix_data + '/metainfo', ['data/' + app_id + '.appdata.xml']),
                (prefix_data + '/applications', ['data/' + app_id + '.desktop']),
                (prefix_data + '/glib-2.0/schemas',['data/' + app_id + '.gschema.xml']),
                # (data_path + '/icons',['data/icons/' + app_id + '-symbolic.svg']),
                # (data_path + '/icons',['data/icons/' + app_id + '-left.svg']),
                # (data_path + '/icons',['data/icons/' + app_id + '-right.svg']),
                (data_path,['data/application.css']),
                (src_path,['gandiva' + '/__init__.py']),
                (src_path,['gandiva' + '/main.py']),
                (shell_path,['gandiva' + '/shell/__init__.py']),
                (shell_path,['gandiva' + '/shell/custom_shortcut_settings.py']),
                (shell_path,['gandiva' + '/shell/display_enclosure.py']),
                (shell_path,['gandiva' + '/shell/chat_view.py']),
                (shell_path,['gandiva' + '/shell/main_window.py'])]

# Post install commands
class PostInstall(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        # print('Updating icon cache...')
        # call(['gtk-update-icon-cache', '-qtf', path.join(prefix_data, 'icons', 'hicolor')])

        # print("Installing new Schemas")
        # call(['glib-compile-schemas', path.join(prefix_data, 'glib-2.0/schemas')])

        # print("Clean-up")
        # import shutil
        # for size in icon_sizes:
        #     shutil.rmtree('data/icons/' + size)

setup(
    name=app_name,  # Required
    license='GNU GPL3',
    version='0.0.1',  # Required
    url=app_url,  # Optional
    author='Subhadeep Jasu',  # Optional
    author_email='subhajasu@gmail.com',  # Optional
    scripts=[app_id],
    data_files=install_data  # Optional
    # cmdclass={
    #     'install': PostInstall,
    # }
)
