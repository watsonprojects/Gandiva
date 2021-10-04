project(
    'com.github.watsonprojects.gandiva',
    version: '0.0.1',
    meson_version: '>= 0.50.0'
)

organization = 'watsonprojects'
domain = 'com.github'
# app_id built as: domain.organization.project_name
gitrepo = 'https://github.com/'+organization+'/'+meson.project_name()
website = gitrepo


i18n = import('i18n')
python = import('python')
gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
localedir = join_paths(prefix, get_option('localedir'))

dependency ('granite')
dependency ('gtk+-3.0')
dependency ('glib-2.0')
dependency ('gobject-2.0')

subdir('po')
subdir('data')

meson.add_install_script('install.py')
