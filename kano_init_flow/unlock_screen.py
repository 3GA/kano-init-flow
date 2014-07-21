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


class UnlockScreen():
    def __init__(self, win):

        self.win = win
        image = constants.media
        # Check if user is registered
        login = is_registered()

        if login:
            header = "Profile created!"
            subheader = "Now you can download music and videos, share your character, and connect with friends around the world."
            image += "/profile_created.png"
        else:
            header = "No online profile for now"
            subheader = "Your profile is where you can store all your swag, badges and challenges. But fear not - we will save everything for when you have internet."
            image += "/no_profile.png"

        self.template = Template(image, header, subheader, "UNLOCK REWARDS", "")
        self.win.add(self.template)
        self.template.kano_button.connect("button_release_event", self.activate)
        self.win.show_all()

    def activate(self, widget, event):
        self.win.clear_win()
        SwagScreen(self.win)
