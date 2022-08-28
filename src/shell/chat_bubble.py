#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2022 Subhadeep Jasu <subhajasu@gmail.com>

# Code ported from https://github.com/SubhadeepJasu/hemera/blob/master/src/bubbles/SVGData.vala
# Originally authored by me and Hannes Schulze

#pylint: disable=unused-argument

# Base imports
import subprocess
import gi
#pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
#pylint: enable=wrong-import-position
from gi.repository import Gtk, GdkPixbuf, GLib, Pango
from PIL import ImageColor

# Gandiva imports
from config import constants
from utils import utilities
from utils.utilities import BubbleStyle, ActionButton, DesktopApplication

#--------------CLASS-SEPARATOR---------------#

class ChatBubble(Gtk.Box):
  """
  ## Chat Bubble
  This shows a generic speech bubble, which may show
  a gtk widget within it or simply some text.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.set_valign(Gtk.Align.START)
    self.set_margin_top(8)
    self.set_margin_bottom(8)
    self.set_margin_start(8)
    self.set_margin_end(8)


  def set_content(self, content, bubble_style: BubbleStyle, from_user=True):
    """
    Set the internal contents of the speech bubble and it's style.

    :param content: Content to be shown in the bubble. Could be text or widget
    :param bubble_style: Style of the bubble (see BubbleStyle)
    :param from_user: Whether this bubble is from the user or not
    :type from_user: bool
    """
    # If content if supposed to be simple text
    if isinstance(content, str):
      label = Gtk.Label()
      label.set_text(content)
      label.set_margin_top(12)
      label.set_margin_bottom(12)
      label.set_margin_start(6)
      label.set_margin_end(6)
      label.set_max_width_chars(28)
      label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
      label.set_wrap(True)
      label.set_justify(Gtk.Justification.RIGHT if from_user else Gtk.Justification.LEFT)
      self.__content = Gtk.Box()
      self.__content.append(label)
    # Otherwise it might be a widget in which case
    # add it directly
    elif isinstance(content, list):
      expander = Gtk.Expander()
      expander.set_label('Results')

      listbox = Gtk.Box()
      listbox.set_margin_start(8)
      listbox.set_margin_bottom(8)
      listbox.set_margin_end(8)
      listbox.set_margin_top(8)
      listbox.set_size_request(150, 20)
      listbox.set_orientation(Gtk.Orientation.VERTICAL)
      expander.set_child(listbox)
      for item in content:
        if isinstance(item, str):
          label = Gtk.Label()
          label.set_text(item)
          listbox.append(label)

      self.__content = Gtk.Box()
      self.__content.append(expander)
    else:
      self.__content = content

    self.__content.get_style_context().add_class('speech-bubble')
    self.__css_provider = Gtk.CssProvider()
    self.__css_provider.load_from_data(bubble_style.style)
    self.__content.get_style_context().add_provider(self.__css_provider, 800)

    self.__main_overlay = Gtk.Overlay()
    self.__main_overlay.set_child(self.__content)

    self.__callout_gfx_mask = Gtk.DrawingArea()
    self.__callout_gfx_mask.set_can_target(False)
    self.__callout_gfx_mask_color = bubble_style.background_color
    self.__callout_gfx_mask.set_draw_func(self.__draw)
    self.__callout_gfx_mask.set_size_request(2, 5)
    self.__callout_gfx_mask.set_margin_bottom(4)
    self.__callout_gfx_mask.set_valign(Gtk.Align.END)
    self.__main_overlay.add_overlay(self.__callout_gfx_mask)

    self.__svg = self.__format_svg('/images/callout_gfx/', from_user, bubble_style.background_color, bubble_style.border_color)
    loader = GdkPixbuf.PixbufLoader()
    loader.write(self.__svg.encode())
    loader.close()
    pixbuf = loader.get_pixbuf()
    self.__callout_gfx = Gtk.Image.new_from_pixbuf(pixbuf)

    # Speech bubbles which represent user query are always on the right
    # The ones from the system should be on the left
    if from_user:
      self.__callout_gfx_mask.set_halign(Gtk.Align.END)
      self.append(self.__main_overlay)
      self.append(self.__callout_gfx)
      self.__callout_gfx.get_style_context().add_class('callout-gfx-right')
      self.__callout_gfx.set_halign(Gtk.Align.END)
      self.__callout_gfx.set_valign(Gtk.Align.END)
      self.set_halign(Gtk.Align.END)
    else:
      self.__callout_gfx_mask.set_halign(Gtk.Align.START)
      self.append(self.__callout_gfx)
      self.append(self.__main_overlay)
      self.__callout_gfx.get_style_context().add_class('callout-gfx-left')
      self.__callout_gfx.set_halign(Gtk.Align.END)
      self.__callout_gfx.set_valign(Gtk.Align.END)
      self.set_halign(Gtk.Align.START)


  def __draw(self, widget, cr, width, height):
    """
    Hide the border of the speech bubble where the little notch appears.
    """
    # Reference: https://www.tutorialspoint.com/pygtk/pygtk_drawingarea_class.htm
    parsed_color = ImageColor.getcolor(self.__callout_gfx_mask_color, 'RGB')
    cr.set_source_rgb(parsed_color[0] / 255.0, parsed_color[1] / 255.0, parsed_color[2] / 255.0)
    cr.rectangle(0, 0, 2, 5)
    cr.fill()

    cr.save()
    cr.restore()


  def __format_svg(self, uri: str, from_user: bool, background: str, edge: str):
    """
    Change svg style based on the background and border color of the bubble.
    """
    with open(constants.DATA_PATH + uri + ('right' if from_user else 'left') + '.svg') as file:
      data = file.read()

    return data.format(background, edge)


  def animate_bubble(self):
    """
    Add a little bit of eye candy and make sure the speech bubbles appear smoothly.
    """
    self.get_style_context().add_class('speech-bubble-animate')
    GLib.timeout_add(2000, self.__animate_stop_bubble)


  def __animate_stop_bubble(self):
    """
    Reset animation.
    """
    self.get_style_context().remove_class('speech-bubble-animate')



class ChatBubbleSearch(ChatBubble):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


  def set_category(self, category):
    self.__category = category


  def set_content(self, content, bubble_style: BubbleStyle, from_user=True):
    main_box = Gtk.Box()
    main_box.set_orientation(Gtk.Orientation.VERTICAL)
    main_box.set_size_request(150, 5)

    expander = Gtk.Expander()
    expander.set_margin_top(4)
    expander.set_margin_bottom(4)
    expander.set_label('Results (%d)' % len(content))

    listbox = Gtk.Box()
    listbox.get_style_context().add_class('list-content')
    listbox.set_margin_start(8)
    listbox.set_margin_bottom(8)
    listbox.set_margin_end(8)
    listbox.set_margin_top(8)
    listbox.set_size_request(150, 20)
    listbox.set_orientation(Gtk.Orientation.VERTICAL)
    expander.set_child(listbox)

    for item in content:
      if isinstance(item, DesktopApplication):
        app_item_grid = Gtk.Grid()

        icon = Gtk.Image()
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.set_valign(Gtk.Align.START)
        icon.set_margin_start(4)
        icon.set_margin_top(4)
        icon.set_margin_end(4)
        if item.get_icon() is not None:
          icon.set_from_gicon(item.get_icon())
        else:
          icon.set_from_icon_name('application-default-icon')
        app_item_grid.attach(icon, 0, 0, 1, 2)

        title = Gtk.Label()
        title.set_margin_top(4)
        title.get_style_context().add_class('h4')
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)
        title.set_ellipsize(Pango.EllipsizeMode.END)
        title.set_text(item.get_name())
        app_item_grid.attach(title, 1, 0, 1, 1)

        if item.get_description() is not None:
          description = Gtk.Label()
          description.set_text(item.get_description())
          description.get_style_context().add_class('h6')
          description.set_halign(Gtk.Align.START)
          description.set_justify(Gtk.Justification.LEFT)
          description.set_wrap(True)
          app_item_grid.attach(description, 1, 1, 1, 1)

        button_box_scrollable = Gtk.ScrolledWindow()
        app_item_grid.attach(button_box_scrollable, 0, 2, 2, 1)

        button_box = Gtk.Box()
        button_box.set_spacing(4)
        button_box.set_homogeneous(True)
        button_box.set_hexpand(True)
        button_box.set_valign(Gtk.Align.END)
        button_box.set_margin_bottom(4)
        button_box_scrollable.set_child(button_box)

        launch_button = ActionButton()
        launch_button.set_desktop_app(item)
        launch_button.get_style_context().add_class('action-button')
        launch_button.get_style_context().add_class('suggested-action')
        launch_button.set_icon_name('media-playback-start-symbolic')
        button_box.append(launch_button)

        actions = item.get_actions()
        for action_name in actions.keys():
          action_button = ActionButton()
          action_button.set_desktop_app(item)
          action_button.set_action(action_name, actions[action_name])
          button_box.append(action_button)

        listbox.append(app_item_grid)
      elif type(item) == tuple:
        file_item_box = Gtk.Box()
        file_item_box.set_tooltip_text(item[2])
        file_item_box.set_margin_start(4)
        file_item_box.set_margin_top(4)
        file_item_box.set_margin_end(4)
        file_item_box.set_margin_bottom(4)
        file_item_box.set_spacing(8)

        icon = Gtk.Image()
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        icon.set_from_icon_name(utilities.get_icon_name_from_mime(item[1]))
        file_item_box.append(icon)

        filename_label = Gtk.Label()
        filename_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        filename_label.set_text(item[0])
        filename_label.set_halign(Gtk.Align.START)
        filename_label.set_hexpand(True)
        file_item_box.append(filename_label)

        open_button = Gtk.Button()
        open_button.set_tooltip_text(item[2] + item[0])
        open_button.set_icon_name('document-open-symbolic')
        open_button.get_style_context().add_class('suggested-action')
        file_item_box.append(open_button)

        listbox.append(Gtk.Separator())
        listbox.append(file_item_box)

        open_file_lamda = lambda x: subprocess.call(('xdg-open', x.get_tooltip_text()))
        open_button.connect('clicked', open_file_lamda)

    main_header = Gtk.Label()
    main_header.get_style_context().add_class('h3')
    main_header.set_halign(Gtk.Align.START)
    main_header.set_margin_start(8)
    main_header.set_margin_top(8)
    main_header.set_margin_bottom(8)
    main_box.append(main_header)
    main_box.append(expander)
    if self.__category == 'apps-generic':
      main_header.set_text('Search Apps')

      new_bubble_style = BubbleStyle('#FFF', '#868DFF', '', '#333')
      new_bubble_style.style = bytes("""
      .speech-bubble {
        color: #FFF;
        background-image: linear-gradient(216deg, #8B1DFF, #868DFF);
        border: 1px solid #333;
      }
      """, 'utf-8')
    elif self.__category == 'apps-games':
      listbox.get_style_context().add_class('listbox-games')
      main_header.set_text('Games')

      new_bubble_style = BubbleStyle('#000', '#77C700', '', '#333')
      new_bubble_style.style = bytes("""
      .speech-bubble {
        color: #000;
        background-image: linear-gradient(216deg, #029700, #77C700);
        border: 1px solid #333;
      }
      """, 'utf-8')
    elif self.__category == 'apps-accessories':
      listbox.get_style_context().add_class('listbox-accessories')
      main_header.set_text('Accessories')

      new_bubble_style = BubbleStyle('#333', '#95a3ab', '', '#333')
      new_bubble_style.style = bytes("""
      .speech-bubble {
        color: #FFF;
        background-image: linear-gradient(216deg, #667885, #95a3ab);
        border: 1px solid #333;
      }
      """, 'utf-8')
    elif self.__category == 'files-generic':
      listbox.get_style_context().add_class('listbox-accessories')
      main_header.set_text('File Search')

      new_bubble_style = BubbleStyle('#333', '#95a3ab', '', '#333')
      new_bubble_style.style = bytes("""
      .speech-bubble {
        color: #FFF;
        background-image: linear-gradient(216deg, #667885, #95a3ab);
        border: 1px solid #333;
      }
      """, 'utf-8')


    return super().set_content(main_box, new_bubble_style, False)
