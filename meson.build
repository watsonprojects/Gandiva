project(
  'com.github.watsonprojects.gandiva',
  version: '0.0.1',
  meson_version: '>= 0.50.0'
)

organization = 'subhadeepjasu'
domain = 'com.github'
gitrepo = 'https://github.com/' + organization + '/' + meson.project_name()
website = gitrepo

# i18n = import('i18n')
pkg = import('pkgconfig')
# python = import('python')
# gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
# localedir = join_paths(prefix, get_option('localedir'))

dependency('gtk4', version:'>=4.6.0')
dependency('libadwaita-1')
dependency('glib-2.0')
dependency('gobject-2.0')
dependency('python3')
dependency('alsa')
dependency('espeak-ng')

subdir('data')
subdir('src')

meson.add_install_script('meson/post_install.py')
