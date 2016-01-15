# The Status class
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Keeps user's progression through the init flow
#

from gi.repository import Gtk, GLib, GObject, Gdk

from kano.gtk3.apply_styles import apply_common_to_screen
from kano.logging import logger

from kano_init_flow.controller import Controller
from kano_init_flow.ui.css import apply_styling_to_screen
from kano_init_flow.ui.scene import Scene
from kano_init_flow.paths import common_css_path


class MainWindow(Gtk.Window):
    """
        Manages the full-screen top level window of the application.
    """

    EMERGENCY_EXIT_CLICKS = 5

    def __init__(self, start_from=None):
        """
            :param start_from: Overrides the status and makes the init flow
                               start from this stage.
            :type start_from: str
        """

        super(MainWindow, self).__init__()
        self._ctl = Controller(self, start_from)
        self.connect("delete-event", Gtk.main_quit)
        self._child = None

        self._press_signal_id = None
        self._release_signal_id = None
        self._emergency_counter = 0

        self._to_id_counter = 0
        self._timeouts = []

        apply_common_to_screen()
        apply_styling_to_screen(common_css_path('scene.css'))
        apply_styling_to_screen(common_css_path('speech_bubble.css'))

        self.set_decorated(False)

        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()
        self.set_size_request(width, height + 1)
        self.set_position(Gtk.WindowPosition.CENTER)

        overlay = Gtk.Overlay()
        self._child = Gtk.EventBox()
        overlay.add(self._child)
        self.add(overlay)
        self._container = overlay
        self._container.set_halign(Gtk.Align.CENTER)
        self._container.set_valign(Gtk.Align.CENTER)

        emergency_exit = Gtk.EventBox()
        emergency_exit.set_halign(Gtk.Align.START)
        emergency_exit.set_valign(Gtk.Align.START)
        emergency_exit.set_size_request(20, 20)
        emergency_exit.connect('button-release-event', self._emergency_exit_cb)
        overlay.add_overlay(emergency_exit)

        self.connect('key-release-event', self._key_emergency_exit)
        self.connect('key-release-event', self._key_skip_stage)

        if start_from:
            debug_button = Gtk.EventBox()
            debug_button.add(Gtk.Label('Close'))
            debug_button.set_halign(Gtk.Align.END)
            debug_button.set_valign(Gtk.Align.START)
            debug_button.connect('button-release-event', Gtk.main_quit)
            overlay.add_overlay(debug_button)

    def _key_emergency_exit(self, widget, event):
        if (hasattr(event, 'keyval') and
           event.keyval in [Gdk.KEY_Q, Gdk.KEY_q] and
           event.state & Gdk.ModifierType.SHIFT_MASK and
           event.state & Gdk.ModifierType.CONTROL_MASK):
            self._emergency_exit_cb(widget)

        return False

    def _key_skip_stage(self, widget, event):
        if (hasattr(event, 'keyval') and
           event.keyval in [Gdk.KEY_N, Gdk.KEY_n] and
           event.state & Gdk.ModifierType.SHIFT_MASK and
           event.state & Gdk.ModifierType.CONTROL_MASK):
            self._ctl.next_stage()

        return False

    def _emergency_exit_cb(self, widget, data=None):
        self._emergency_counter += 1
        msg = "Emergency button pressed {}x".format(self._emergency_counter)
        logger.warn(msg)
        if self._emergency_counter >= self.EMERGENCY_EXIT_CLICKS:
            logger.warn("Emergency exiting the init flow")
            self._ctl.complete()
            Gtk.main_quit()

    @property
    def return_value(self):
        return self._ctl.return_value

    def prepare_first_stage(self):
        return self._ctl.first_stage()

    def push(self, child):
        GLib.idle_add(self._do_push, child)

    def schedule_event(self, event):
        # The callback must always return False not to be rescheduled.
        # This wrapper makes sure of that.
        self._to_id_counter += 1
        t_id = self._to_id_counter

        def __wrapper1():
            def __wrapper2():
                if t_id in self._timeouts:
                    event['callback'](*event['args'])
                    idx = self._timeouts.index(t_id)
                    del self._timeouts[idx]
                return False
            GLib.idle_add(__wrapper2)

        GLib.timeout_add_seconds(event['delay'], __wrapper1)
        self._timeouts.append(t_id)

    def set_key_events_handlers(self, press=None, release=None):
        if self._press_signal_id:
            GObject.signal_handler_disconnect(self, self._press_signal_id)
            self._press_signal_id = None

        if self._release_signal_id:
            GObject.signal_handler_disconnect(self, self._release_signal_id)
            self._release_signal_id = None

        if press:
            self._press_signal_id = self.connect('key-press-event', press)

        if release:
            self._release_signal_id = self.connect('key-release-event',
                                                   release)

    def _do_push(self, child):
        # Cleans up any pending scheduled events
        for i, src in enumerate(self._timeouts):
            del self._timeouts[i]
            #print GLib.source_remove_by_funcs_user_data(src.source_funcs,
            #                                            src.callback_data)
            #src.destroy()
            #if not src.is_destroyed():
            #    GLib.source_remove(src.get_id())

        if issubclass(child.__class__, Scene):
            for event in child.scheduled_events:
                self.schedule_event(event)

            child.set_active()
            child = child.widget

        if self._child:
            self._container.remove(self._child)
            self._child.destroy()

        self._child = child
        self._container.add(child)
        child.show_all()
        return False
