#!/usr/bin/env python

# unlock_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Shows profile created
#

from template import Template
from swag_screen import SwagScreen
from kano_world.functions import is_registered
import kano_init_flow.constants as constants
from kano_init_flow.data import get_data


class UnlockScreen():
    profile_created_data = get_data("PROFILE_CREATED")
    no_profile_data = get_data("NO_PROFILE")

    def __init__(self, win):

        self.win = win
        self.win.set_resizable(True)
        image = constants.media

        # Check if user is registered
        login = is_registered()

        if login:
            header = self.profile_created_data["LABEL_1"]
            subheader = self.profile_created_data["LABEL_2"]
            image += self.profile_created_data["IMG_FILENAME"]
        else:
            header = self.no_profile_data["LABEL_1"]
            subheader = self.no_profile_data["LABEL_2"]
            image += self.no_profile_data["IMG_FILENAME"]

        self.template = Template(image, header, subheader, "UNLOCK REWARDS", "")
        self.win.add(self.template)
        self.template.kano_button.connect("button_release_event", self.activate)
        self.win.show_all()

    def activate(self, widget, event):
        self.win.clear_win()
        self.win.set_size_template("normal")
        SwagScreen(self.win)
