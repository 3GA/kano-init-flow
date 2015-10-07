# The desktop stage
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import time
import subprocess
import threading
from gi.repository import Gtk, Gdk, GLib

from kano_init_flow.stage import Stage
from kano_init_flow.ui.scene import Scene, Placement
from kano_init_flow.ui.speech_bubble import SpeechBubble
from kano_init_flow.paths import common_media_path
from kano_init_flow.ui.world_icon import WorldIcon
from kano_init_flow.ui.profile_icon import ProfileIcon
from kano_init_flow.ui.components import NextButton
from kano_avatar_gui.CharacterCreator import CharacterCreator
from kano.gtk3.buttons import KanoButton
from kano.logging import logger
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_world.functions import is_registered


class Desktop(Stage):
    """
        The desktop video replacement flow
    """

    id = 'desktop'
    _root = __file__

    def __init__(self, ctl):
        super(Desktop, self).__init__(ctl)
        apply_styling_to_screen(self.css_path("style.css"))

        # Flag to see whether to launch the character creator
        # and registration page.
        self._char_window_launched = False
        self._login_launched = False

    def first_scene(self):
        s = self._setup_first_scene()
        self._ctl.main_window.push(s)

    def second_scene(self):
        s = self._setup_second_scene()
        self._ctl.main_window.push(s)

    def third_scene(self):
        s = self._setup_third_scene()
        self._ctl.main_window.push(s)

    def fourth_scene(self):
        s = self._setup_fourth_scene()
        self._ctl.main_window.push(s)

    def next_stage(self):
        self._ctl.next_stage()

    def _setup_first_scene(self):
        self._first_scene = scene = Scene(self._ctl.main_window)
        scene.set_background(common_media_path('blueprint-bg-4-3.png'),
                             common_media_path('blueprint-bg-16-9.png'))

        # Pass the callback of what we want to launch in the profile icon
        self._add_profile_icon(self._first_scene, self._char_creator_window, True)

        '''
        # Add judoka
        scene.add_widget(
            Gtk.Image.new_from_file(self.media_path("left-pointing-judoka.png")),
            Placement(0.4, 0.4),
            Placement(0.2, 0.4)
        )

        scene.add_widget(
            SpeechBubble(
                text='Welcome to the desktop!\n'
                     'Click on this icon to set up\n'
                     'your profile',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.4, 0.1),
            Placement(0.2, 0.1)
        )
        '''

        scene.add_widget(
            SpeechBubble(
                text='Welcome to the desktop!\n'
                     'Click on this icon to set up\n'
                     'your profile',
                source=SpeechBubble.TOP,
                source_align=0.0,
                scale=scene.scale_factor
            ),
            Placement(0.15, 0.2),
            Placement(0.12, 0.2)
        )

        # Shortcut
        '''
        scene.add_widget(
            NextButton(),
            Placement(0.5, 0.5),
            Placement(0.5, 0.5),
            self.second_scene
        )
        '''

        return scene

    def _char_creator_window(self):

        if not self._char_window_launched:
            # Stop this being launched again
            self._char_window_launched = True

            # Add watch cursor
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self._ctl.main_window.get_window().set_cursor(watch_cursor)
            self._first_scene.show_all()

            while Gtk.events_pending():
                Gtk.main_iteration()

            # This doesn't have to be in separate thread since this window
            # doesn't change size, so it doesn't matter whether the GUI behind it
            # updates
            CharacterWindow(self.second_scene, self.css_path("style.css"))
            self._ctl.main_window.get_window().set_cursor(None)

    def _setup_second_scene(self):
        self._second_scene = scene = Scene(self._ctl.main_window)
        scene.set_background(common_media_path('blueprint-bg-4-3.png'),
                             common_media_path('blueprint-bg-16-9.png'))

        self._add_profile_icon(self._second_scene)
        self._add_world_icon(scene, self._launch_login,
                             offline=(not is_registered()))

        # Add judoka
        '''
        scene.add_widget(
            Gtk.Image.new_from_file(self.media_path("right-pointing-judoka.png")),
            Placement(0.6, 0.45),
            Placement(0.8, 0.45)
        )

        scene.add_widget(
            SpeechBubble(
                text='This icon is Kano World!\n'
                     'This is where Judokas make\n'
                     'and share projects togther\n'
                     'online.',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.6, 0.1),
            Placement(0.8, 0.1)
        )
        '''

        scene.add_widget(
            SpeechBubble(
                text='This icon is Kano World!\n'
                     'This is where Judokas make\n'
                     'and share projects togther\n'
                     'online.',
                source=SpeechBubble.TOP,
                source_align=1.0,
                scale=scene.scale_factor
            ),
            Placement(0.8, 0.2),
            Placement(0.88, 0.2)
        )

        # Shortcut
        '''
        scene.add_widget(
            NextButton(),
            Placement(0.5, 0.5),
            Placement(0.5, 0.5),
            self.third_scene
        )
        '''

        return scene

    def _setup_third_scene(self):
        scene = Scene(self._ctl.main_window)
        scene.set_background(common_media_path('blueprint-bg-4-3.png'),
                             common_media_path('blueprint-bg-16-9.png'))

        self._add_profile_icon(scene)
        self._add_world_icon(scene, offline=(not is_registered()))

        '''
        # Add judoka
        scene.add_widget(
            Gtk.Image.new_from_file(self.media_path("taskbar-judoka.png")),
            Placement(0.5, 0.8),
            Placement(0.5, 0.8)
        )

        scene.add_widget(
            SpeechBubble(
                text='This is the Taskbar! Here you can\n'
                     'manage settings and make\n'
                     'changes to the computer.',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.5, 0.4),
            Placement(0.5, 0.4)
        )
        '''

        scene.add_widget(
            SpeechBubble(
                text='This is the Taskbar! Here you can\n'
                     'manage settings and make\n'
                     'changes to the computer.',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.5, 0.9),
            Placement(0.5, 0.9)
        )

        self._add_taskbar(scene)

        scene.add_widget(
            NextButton(),
            Placement(0.5, 0.6, 0),
            Placement(0.5, 0.6, 0),
            self.fourth_scene,
        )

        return scene

    def _setup_fourth_scene(self):
        scene = Scene(self._ctl.main_window)
        scene.set_background(common_media_path('blueprint-bg-4-3.png'),
                             common_media_path('blueprint-bg-16-9.png'))

        # Pass the callback of what we want to launch in the profile icon
        self._add_profile_icon(scene)
        self._add_world_icon(scene, offline=(not is_registered()))
        self._add_taskbar(scene)

        # Go through all the desktop icons and add them to the desktop
        # Either go through all files in a folder with a specific pattern, or
        # just list them in an array

        # All icons are in /usr/share/icons/Kano/88x88/apps
        # or /usr/share/kano-desktop/icons
        parent_dir = "/usr/share/kano-desktop/icons"
        parent_dir_2 = "/usr/share/icons/Kano/88x88/apps"

        # Order the icons needed
        icon_files = [
            os.path.join(parent_dir, "snake.png"),
            os.path.join(parent_dir, "pong.png"),
            os.path.join(parent_dir, "make-minecraft.png"),
            os.path.join(parent_dir, "sonicpi.png"),
            os.path.join(parent_dir, "internet-desktop.png"),
            os.path.join(parent_dir, "apps.png"),
            os.path.join(parent_dir, "kano-homefolder.png"),
            os.path.join(parent_dir_2, "kano-draw.png"),
            os.path.join(parent_dir_2, "linux-story.png"),
            os.path.join(parent_dir, "scratch.png"),
            os.path.join(parent_dir_2, "video.png"),
            os.path.join(parent_dir, "plus-icon.png")

        ]

        icon_grid = Gtk.Grid()
        icon_grid.set_row_spacing(50)
        icon_grid.set_column_spacing(50)
        row = 1
        column = 0

        for f in icon_files:
            icon = Gtk.Image.new_from_file(f)
            icon_grid.attach(icon, column, row, 1, 1)
            column += 1

            if column >= 7:
                column = 0
                row -= 1

        scene.add_widget(
            icon_grid,
            Placement(0.5, 0.85, 0),
            Placement(0.5, 0.85, 0)
        )

        '''
        scene.add_widget(
            Gtk.Image.new_from_file(self.media_path("apps-judoka.png")),
            Placement(0.8, 0.6),
            Placement(0.7, 0.6)
        )

        scene.add_widget(
            SpeechBubble(
                text='And these are your apps! With\n'
                     'them you can make amazing\n'
                     'code creations to share in\n'
                     'Kano World',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.85, 0.25),
            Placement(0.7, 0.25)
        )
        '''

        scene.add_widget(
            SpeechBubble(
                text='And these are your apps! With\n'
                     'them you can make amazing\n'
                     'code creations to share in\n'
                     'Kano World',
                source=SpeechBubble.BOTTOM,
                scale=scene.scale_factor
            ),
            Placement(0.5, 0.5),
            Placement(0.5, 0.5)
        )

        scene.add_widget(
            NextButton(),
            Placement(0.85, 0.55, 0),
            Placement(0.75, 0.55, 0),
            self.next_stage
        )

        return scene

    def _add_profile_icon(self, scene, callback=None, use_default=False):
        # We always want to add the widget to the same position in each screen
        scene.add_widget(
            ProfileIcon(use_default),
            Placement(0.03, 0.05, 0),
            Placement(0.03, 0.05, 0),
            callback,
            name="profile_icon"
        )

    def _add_world_icon(self, scene, callback=None, offline=True):
        scene.add_widget(
            WorldIcon(offline),
            Placement(0.97, 0.05, 0),
            Placement(0.97, 0.05, 0),
            callback
        )

    def _add_taskbar(self, scene):

        # Need to collect the icons from the taskbar
        taskbar = Gtk.EventBox()
        taskbar.get_style_context().add_class("taskbar")

        # Make the the right width and height
        taskbar.set_size_request(scene.get_width(), 44)

        # Get all the icons

        scene.add_widget(
            taskbar,
            Placement(1, 1, 0),
            Placement(1, 1, 0)
        )

        start_menu = Gtk.Image.new_from_file("/usr/share/kano-desktop/images/startmenu.png")

        end_filenames = [
            "/usr/share/kano-settings/settings-widget.png",
            "/usr/share/kano-updater/images/widget-no-updates.png",
            "/usr/share/kano-settings/icon/widget-wifi.png",
            "/usr/share/kano-profile/icon/profile-login-widget.png",
            "/usr/share/kano-feedback/media/icons/feedback-widget.png",
            "/usr/share/kano-widgets/icons/home-widget.png"
        ]

        # Black box to show "how hard" the processor is working
        processor_monitor = Gtk.EventBox()
        processor_monitor.get_style_context().add_class("black")
        processor_monitor.set_size_request(40, 45)

        # Get time
        time_label = Gtk.Label(time.strftime("%H:%M"))
        time_label.get_style_context().add_class("time")

        hbox = Gtk.Box()
        hbox.pack_start(start_menu, False, False, 0)
        hbox.pack_end(processor_monitor, False, False, 3)
        hbox.pack_end(time_label, False, False, 3)

        for f in end_filenames:
            image = Gtk.Image.new_from_file(f)
            hbox.pack_end(image, False, False, 3)

        taskbar.add(hbox)
        taskbar.show_all()
        return taskbar

    def _launch_login(self):

        # Only launch this once
        if not self._login_launched:
            self._login_launched = True

            # Add watch cursor
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self._ctl.main_window.get_window().set_cursor(watch_cursor)
            self._second_scene.show_all()

            while Gtk.events_pending():
                Gtk.main_iteration()

            self._launch_login_process_thread()

    def _launch_login_process_thread(self):
        t = threading.Thread(target=self._launch_login_process)
        t.start()

    def _launch_login_process(self):
        try:
            p = subprocess.Popen(['/usr/bin/kano-login', '-r'])
            p.wait()
        except Exception:
            logger.debug("kano-login failed to launch")

        GLib.idle_add(self._finish_login_thread)

    def _finish_login_thread(self):
        self._ctl.main_window.get_window().set_cursor(None)
        self.third_scene()

    def _create_blur(self):
        blur = Gtk.EventBox()

        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()

        blur.get_style_context().add_class("blur")
        blur.set_size_request(width, height)
        return blur


class CharacterWindow(Gtk.Window):
    def __init__(self, cb, css_path):
        super(CharacterWindow, self).__init__()

        apply_styling_to_screen(css_path)
        self.get_style_context().add_class("character_window")
        self.set_decorated(False)
        self.close_cb = cb

        self.char_edit = CharacterCreator(randomise=True)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self.char_edit, False, False, 0)
        button = KanoButton("OK")
        button.connect("clicked", self.close_window)
        button.pack_and_align()

        self.connect("delete-event", Gtk.main_quit)
        self.set_keep_above(True)

        vbox.pack_start(button.align, False, False, 10)
        self.show_all()

        self.char_edit.show_pop_up_menu_for_category("judoka-faces")
        self.char_edit.select_category_button("judoka-faces")

    def close_window(self, widget):
        self.char_edit.save()
        self.destroy()
        GLib.idle_add(self.close_cb)
