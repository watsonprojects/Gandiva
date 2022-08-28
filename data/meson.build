# Install icons
icon_sizes = ['16', '24', '32', '48', '64', '128']

foreach size : icon_sizes
  install_data(
    join_paths('images', 'icons', size, meson.project_name() + '.svg'),
    install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', size + 'x' + size, 'apps')
  )
  install_data(
    join_paths('images', 'icons', size, meson.project_name() + '.svg'),
    install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', size + 'x' + size + '@2', 'apps')
  )
endforeach

install_data(
  join_paths('images', 'icons', '16', meson.project_name() + '-symbolic.svg'),
  install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', 'symbolic', 'apps')
)

# Install desktop
install_data(
  meson.project_name() + '.desktop',
  install_dir: join_paths(get_option('datadir'), 'applications')
)

# Install schemas
install_data (
  meson.project_name() + '.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)

# Install stylesheet
install_data (
  'application.css',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'data')
)

# Install rest of the images
install_subdir (
  'images',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'data')
)

# Install speech recognition models
install_subdir (
  'SpeechRecognitionModels',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'data')
)

# Install skill plugins. This however doesn't make them usable. Use the 'system run relearn'
# command to actually have Gandiva learn them.
install_subdir (
  'SkillPlugins',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'data')
)
