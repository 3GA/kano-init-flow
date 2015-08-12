# The base class for implementing scenes
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from gi.repository import Gtk, GdkPixbuf

from kano.gtk3.cursor import attach_cursor_events

class PositionScale(object):
    def __init__(self, pos_x=0, pos_y=0, scale=1.0):
        if x <= 1:
            self._x = int(x * Gtk.Screen.width())
        else:
            self._x = x

        if y <= 1:
            self._y = int(y * Gtk.Screen.height())
        else:
            self._y = y
        self._y = y

        self._scale = scale

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def scale(self):
        return self._scale


class Scene(object):
    """
        The base class for implementing scenes.
    """

    RATIO_4_3 = 4.0/3
    RATIO_16_9 = 16.0/9

    def __init__(self):
        self._screen_ratio = self._get_screen_ratio()

        self._overlay = Gtk.Overlay()

        self._background = Gtk.Image()
        self._overlay.add(self._background)

        self._fixed = Gtk.Fixed()
        self._overlay.add_overlay(self._fixed)

    def _get_screen_ratio(self):
        w = Gtk.Screen.width()
        h = Gtk.Screen.height()

        ratio = (w * 1.0) / h
        dist_43 = abs(self.RATIO_4_3 - ratio)
        dist_169 = abs(self.RATIO_16_9 - ratio)

        if dist_43 < dist169:
            return self.RATIO_4_3

        return self.RATIO_16_9

    def set_background(self, ver_43, ver_169):
        """
            Set the background of the scene.

            :param ver_43: Path to the 4:3 version of the background.
            :type ver_43: str

            :param ver_169: Path to the 16:9 version of the background.
            :type ver_169: str
        """

        w = Gtk.Screen.width()
        h = Gtk.Screen.height()

        bg_path = ver_43 if self._screen_ratio == self.RATIO_4_3 else ver_163
        bg_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(bg_path, w, h)
        self._background.set_from_pixbuf(bg_pixbuf)

    def add_widget(self, widget, pos_43, pos_169, clicked_cb):
        pos = pos_43 if self._ratio == self.RATIO_4_3 else pos_169

        # If the widget is an image, scale it using GdkPixbuf
        if pos.scale != 1:
            if widget.__class__ == Gtk.Image:
                pixbuf = widget.get_pixbuf()
                w = pixbuf.get_width()
                h = pixbuf.get_height()

                w_scaled = int(w * pos.scale)
                h_scaled = int(h * pos.scale)
                new_pixbuf = pixbuf.scale_simple(w_scaled, h_scaled,
                                                 GdkPixbuf.InterpType.BILINEAR)
                widget.set_from_pixbuf(new_pixbuf)
            else:
                raise RuntimeError('Can\'t scale regular widgets!')

        root_widget = widget
        if clicked_cb:
            # TODO: Add custom styling to this.
            button_wrapper = Gtk.Button()
            button_wrapper.add(widget)
            button_wrapper.connect('clicked', clicked_cb)
            attach_cursor_events(button_wrapper)
            root_widget = button_wrapper

        self._fixed.put(root_widget, pos.x, pos.y)
