pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'gandiva')
gnome = import('gnome')

conf = configuration_data()
conf.set('pkgdatadir', pkgdatadir)
conf.set('version_string', meson.project_version())
conf.set('app_id', meson.project_name())

configure_file(
  input: 'gandiva.in',
  output: meson.project_name(),
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

install_data(
  [
    '__init__.py',
    'main.py',
  ], install_dir: moduledir
)

install_subdir('config', install_dir: moduledir)
install_subdir('core', install_dir: moduledir)
install_subdir('shell', install_dir: moduledir)
install_subdir('utils', install_dir: moduledir)
