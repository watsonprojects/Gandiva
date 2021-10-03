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
src_path = path.join(install_path, 'src')
shell_path = path.join(src_path, 'shell')
data_path = path.join(install_path, 'data')
# icon_path = 'icons/hicolor'
# icon_sizes = ['16','24','32','48','64','128']
# icon_scalable = prefix_data + '/icons/hicolor/scalable/apps'
# icon_16 = prefix_data + '/icons/hicolor/16x16/apps'
# icon_24 = prefix_data + '/icons/hicolor/24x24/apps'
# icon_32 = prefix_data + '/icons/hicolor/32x32/apps'
# icon_48 = prefix_data + '/icons/hicolor/48x48/apps'
# icon_64 = prefix_data + '/icons/hicolor/64x64/apps'
# icon_128 = prefix_data + '/icons/hicolor/128x128/apps'
# icon_16_2x = prefix_data + '/icons/hicolor/16x16@2/apps'
# icon_24_2x = prefix_data + '/icons/hicolor/24x24@2/apps'
# icon_32_2x = prefix_data + '/icons/hicolor/32x32@2/apps'
# icon_48_2x = prefix_data + '/icons/hicolor/48x48@2/apps'
# icon_64_2x = prefix_data + '/icons/hicolor/64x64@2/apps'
# icon_128_2x = prefix_data + '/icons/hicolor/128x128@2/apps'


# Setup install data list
install_data = [(prefix_data + '/metainfo', ['data/' + app_id + '.appdata.xml']),
                (prefix_data + '/applications', ['data/' + app_id + '.desktop']),
                (prefix_data + '/glib-2.0/schemas',['data/' + app_id + '.gschema.xml']),
                # (data_path + '/icons',['data/icons/' + app_id + '-symbolic.svg']),
                # (data_path + '/icons',['data/icons/' + app_id + '-left.svg']),
                # (data_path + '/icons',['data/icons/' + app_id + '-right.svg']),
                (data_path,['data/application.css']),
                (src_path,['src' + '/application.py']),
                (shell_path,['src' + '/shell/__init__.py']),
                (shell_path,['src' + '/shell/custom_shortcut_settings.py']),
                (shell_path,['src' + '/shell/display_enclosure.py']),
                (shell_path,['src' + '/shell/chat_view.py']),
                (shell_path,['src' + '/shell/main_window.py'])]
                # (icon_scalable,['data/icons/' + app_id + '.svg']),
                # (icon_16,['data/icons/16/' + app_id + '.svg']),
                # (icon_16_2x,['data/icons/16/' + app_id + '.svg']),
                # (icon_24,['data/icons/24/' + app_id + '.svg']),
                # (icon_24_2x,['data/icons/24/' + app_id + '.svg']),
                # (icon_32,['data/icons/32/' + app_id + '.svg']),
                # (icon_32_2x,['data/icons/32/' + app_id + '.svg']),
                # (icon_48,['data/icons/48/' + app_id + '.svg']),
                # (icon_48_2x,['data/icons/48/' + app_id + '.svg']),
                # (icon_64,['data/icons/64/' + app_id + '.svg']),
                # (icon_64_2x,['data/icons/64/' + app_id + '.svg']),
                # (icon_128,['data/icons/128/' + app_id + '.svg']),
                # (icon_128_2x,['data/icons/128/' + app_id + '.svg'])]

# # Add icon data files to install data list
# for size in icon_sizes:
#     prefix_size = size + 'x' + size
#     prefix_size2x = size + 'x' + size + '@2'
#     icon_dir = path.join(prefix_data, icon_path, prefix_size, 'apps')
#     icon_dir2x = path.join(prefix_data, icon_path, prefix_size2x, 'apps')
#     icon_file = 'data/icons/' + size + '.svg'
#     if not os.path.exists('data/icons/' + size):
#         os.makedirs('data/icons/' + size)
#     new_icon_file = path.join('data/icons/', size, (app_id + '.svg'))
#     shutil.copyfile(icon_file, new_icon_file)
#     file = (icon_dir, [new_icon_file])
#     file2x = (icon_dir2x, [new_icon_file])
#     install_data.append(file)
#     install_data.append(file2x)

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
