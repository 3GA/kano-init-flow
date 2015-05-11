#!/usr/bin/env python

# keyboard_screen.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk, GObject
import threading

from kano.network import is_internet
import kano_settings.system.keyboard_layouts as keyboard_layouts
import kano_settings.system.keyboard_config as keyboard_config
from kano_settings.config_file import get_setting, set_setting
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_combobox import KanoComboBox

from kano_init_flow.internet_screen import InternetScreen
from kano_init_flow.settings_intro_screen import SettingsIntroScreen

GObject.threads_init()

class KeyboardScreen(Gtk.Box):
    continents = [
        'Africa',
        'America',
        'Asia',
        'Australia',
        'Europe',
        'Others'
    ]

    def __init__(self, _win):
        self.selected_layout = None
        self.selected_country = None
        self.selected_variant = None

        self.selected_continent_index = 1
        self.selected_country_index = 21
        self.selected_variant_index = 0
        self.selected_continent_hr = "America"
        self.selected_country_hr = "USA"
        self.selected_variant_hr = "generic"

        # Set combobox styling to the screen
        KanoComboBox.apply_styling_to_screen()

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = _win
        self.win.set_main_widget(self)

        # Heading
        self.heading = Heading("Keyboard",
                               "Where do you live? So I can set your keyboard")
        self.heading.container.set_size_request(680, -1)

        heading_align = Gtk.Alignment()
        heading_align.add(self.heading.container)

        # Set padding around heading
        self.heading_align = Gtk.Alignment(yscale=0, yalign=0.5)

        # Button
        self.kano_button = KanoButton("APPLY CHANGES")
        self.kano_button.set_sensitive(False)  # Make sure continue button is enabled
        self.kano_button.connect("button_release_event", self.apply_changes)
        self.kano_button.connect("key_release_event", self.apply_changes)
        button_box = Gtk.ButtonBox(spacing=10)
        button_box.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        button_box.add(self.kano_button)
        button_box.set_margin_bottom(30)

        # Create Continents Combo box
        self.continents_combo = KanoComboBox(max_display_items=7)
        for continent in self.continents:
            self.continents_combo.append(continent)
        self.continents_combo.connect("changed", self.on_continent_changed)

        # Create Countries Combo box
        self.countries_combo = KanoComboBox(max_display_items=7)
        self.countries_combo.connect("changed", self.on_country_changed)
        self.countries_combo.props.valign = Gtk.Align.CENTER

        # Create Advance mode checkbox
        self.advance_button = Gtk.CheckButton("Advanced options")
        self.advance_button.set_can_focus(False)
        self.advance_button.props.valign = Gtk.Align.CENTER
        self.advance_button.connect("clicked", self.on_advance_mode)
        self.advance_button.set_active(False)

        # Create Variants Combo box
        self.variants_combo = KanoComboBox(max_display_items=7)
        self.variants_combo.connect("changed", self.on_variants_changed)
        self.variants_combo.props.valign = Gtk.Align.CENTER

        # Set up default values in dropdown lists
        self.set_defaults("continent")
        self.fill_countries_combo(
            self.continents_combo.get_selected_item_text())
        self.set_defaults("country")
        self.on_country_changed(self.countries_combo)
        self.set_defaults("variant")

        # Create various dropdown boxes so we can resize the dropdown
        # lists appropriately. We create two boxes side by side, and
        # then stack the country dropdow lists in one, and one by
        # itself in the other

        #   dropdown_box_countries     dropdown_box_keys
        # |                        |                        |
        # |-------continents-------|   Advance option       |
        # |                        |                        |
        # |                        |                        |
        # |-------countries -------|--------variants--------|
        # |                        |                        |

        dropdown_box_countries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                         spacing=20)
        dropdown_box_countries.set_size_request(230, 30)
        dropdown_box_countries.props.valign = Gtk.Align.CENTER
        dropdown_box_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                    spacing=20)
        dropdown_box_keys.set_size_request(230, 30)
        dropdown_box_countries.pack_start(self.continents_combo, False,
                                          False, 0)
        dropdown_box_countries.pack_start(self.countries_combo, False,
                                          False, 0)
        dropdown_box_keys.pack_start(self.advance_button, False, False, 0)
        dropdown_box_keys.pack_start(self.variants_combo, False, False, 0)
        dropdown_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                     spacing=20)
        dropdown_container.pack_start(dropdown_box_countries, False, False, 0)
        dropdown_container.pack_start(dropdown_box_keys, False, False, 0)

        valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
        valign.set_padding(15, 30, 0, 0)
        valign.add(dropdown_container)

        self.pack_start(heading_align, False, False, 0)
        self.pack_start(valign, False, False, 0)
        self.pack_start(button_box, False, False, 0)

        # Make the kano button grab the focus
        self.kano_button.grab_focus()

        # show all elements except the advanced mode
        self.refresh_window()

    def go_to_next_screen(self):
        self.win.clear_win()

        if not is_internet():
            InternetScreen(self.win)
        else:
            SettingsIntroScreen(self.win)

    def refresh_window(self):
        self.win.show_all()
        self.variants_combo.hide()

    def apply_changes(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:

            # Check for changes from default
            if not (self.selected_country.lower() == "us" and \
                    self.selected_variant == "generic"):

                # This is a callback called by the main loop, so it's safe to
                # manipulate GTK objects:
                watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
                self.kano_button.start_spinner()
                self.win.get_window().set_cursor(watch_cursor)
                self.kano_button.set_sensitive(False)

                def lengthy_process():
                    keyboard_config.set_keyboard(self.selected_country,
                                                 self.selected_variant)

                    def done():
                        self.win.get_window().set_cursor(None)
                        self.kano_button.stop_spinner()
                        self.kano_button.set_sensitive(True)
                        self.go_to_next_screen()

                    GObject.idle_add(done)

                thread = threading.Thread(target=lengthy_process)
                thread.start()

                # Save the changes in the config
                self.update_config()

            # keyboard does not need updating
            else:
                self.go_to_next_screen()

    def update_config(self):

        # Add new configurations to config file.
        set_setting("Keyboard-continent-index", self.selected_continent_index)
        set_setting("Keyboard-country-index", self.selected_country_index)
        set_setting("Keyboard-variant-index", self.selected_variant_index)
        set_setting("Keyboard-continent-human", self.selected_continent_hr)
        set_setting("Keyboard-country-human", self.selected_country_hr)
        set_setting("Keyboard-variant-human", self.selected_variant_hr)

    # setting = "variant", "continent" or "country"
    def set_defaults(self, setting):
        """
        Set the default info on the dropdown lists
            "Keyboard-continent": [
                continents_combo,
                "Keyboard-country",
                "Keyboard-variant"
            ]:
        """

        active_item = get_setting("Keyboard-" + setting + "-index")

        if setting == "continent":
            self.continents_combo.set_selected_item_index(int(active_item))
        elif setting == "country":
            self.countries_combo.set_selected_item_index(int(active_item))
        elif setting == "variant":
            self.variants_combo.set_selected_item_index(int(active_item))
        else:
            return

    def set_variants_to_generic(self):
        self.variants_combo.set_selected_item_index(0)

    def on_continent_changed(self, combo):

        ## making sure the continent has been set
        continent_text = combo.get_selected_item_text()
        continent_index = combo.get_selected_item_index()
        if not continent_text or continent_index == -1:
            return

        self.selected_continent_hr = continent_text
        self.selected_continent_index = continent_index

        self.kano_button.set_sensitive(False)
        self.fill_countries_combo(self.selected_continent_hr)

        # Select the first by default
        self.countries_combo.set_selected_item_index(0)
        self.on_country_changed(self.countries_combo)

    def on_country_changed(self, combo):

        # making sure the country has been set
        country_text = combo.get_selected_item_text()
        country_index = combo.get_selected_item_index()
        if not country_text or country_index == -1:
            return

        # Remove entries from variants combo box
        self.variants_combo.remove_all()
        self.selected_country_hr = country_text
        self.selected_country_index = country_index

        # Refresh variants combo box
        self.selected_country = keyboard_config.find_country_code(
            country_text, self.selected_layout)
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        self.variants_combo.append("generic")
        if variants:
            for variant in variants:
                self.variants_combo.append(variant[0])

        self.set_variants_to_generic()
        self.on_variants_changed(self.variants_combo)

    def on_variants_changed(self, combo):

        # making sure the variant has been set
        variant_text = combo.get_selected_item_text()
        variant_index = combo.get_selected_item_index()
        if not variant_text or variant_index == -1:
            return

        self.kano_button.set_sensitive(True)

        if variant_text == "generic":
            self.selected_variant = self.selected_variant_hr = variant_text
            self.selected_variant_index = 0
            return
        # Select the variant code
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        if variants is not None:
            for variant in variants:
                if variant[0] == variant_text:
                    self.selected_variant = variant[1]
                    self.selected_variant_index = variant_index
                    self.selected_variant_hr = variant_text

    def on_advance_mode(self, widget):

        if int(self.advance_button.get_active()):
            self.variants_combo.show()
        else:
            self.variants_combo.hide()

    def work_finished_cb(self):
        # Finished updating keyboard
        pass

    def fill_countries_combo(self, continent):
        continent = continent.lower()

        try:
            self.selected_layout = keyboard_layouts.layouts[continent]
        except KeyError:
            return

        self.selected_continent_hr = continent

        # Remove entries from countries and variants combo box
        self.countries_combo.remove_all()
        self.variants_combo.remove_all()

        sorted_countries = sorted(self.selected_layout)

        # Refresh countries combo box
        for country in sorted_countries:
            self.countries_combo.append(country)
