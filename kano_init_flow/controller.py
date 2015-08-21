# The Controller class
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the progression through the flow
#

import os
import json
from gi.repository import Gtk
from kano.logging import logger

from .status import Status

from .stages.wifi import Wifi
from .stages.overscan import Overscan
from .stages.drag_and_drop import DragAndDrop
from .stages.quests import Quests


class Controller(object):
    """
        Controls the flow through the setup procedure.

        The MainWindow class uses it to determine what comes next.
    """

    INIT_CONF = '/boot/init.conf'

    def __init__(self, main_window, start_from=None):
        """
            :param start_from: Overrides the status and makes the init flow
                               start from this stage.
            :type start_from: str
        """

        self._main_window = main_window

        self._status = Status.get_instance()
        if start_from:
            self._status.debug_mode(start_from)

        # 0 means that this was the first complete boot
        # 1 means that the init flow was completed before
        self._return_value = 0

        self._stages = [
            Overscan,
            DragAndDrop,
            Wifi,
            Quests
        ]

    @property
    def main_window(self):
        return self._main_window

    def first_stage(self):
        """
            Runs the first stage.

            Note: The first stage is determined by the location variable from
            the status file, not necessarily the very first stage.
        """

        if self._status.completed:
            self._return_value = 1
            Gtk.main_quit()

        if self._should_skip_init_flow():
            Gtk.main_quit()

        if len(self._stages):
            index = self._get_stage_index(self._status.location)
            stage_ctl = self._stages[index](self)
            stage_ctl.first_scene()
        else:
            raise RuntimeError('No flow stages available')

    def next_stage(self):
        """
            This callback is passed over to each stage to be called once
            it's over and the control should be handed to the subsequent one.
        """

        index = self._get_stage_index(self._status.location)
        if index is not None and index < len(self._stages) - 1:
            stage_ctl = self._stages[index + 1](self)
            stage_ctl.first_scene()
        else:
            # TODO: Exit the application, there are no more stages to do.
            Gtk.main_quit()

    @property
    def return_value(self):
        return self._return_value

    def _get_stage_index(self, stage_id):
        index = None
        for i, s in enumerate(self._stages):
            if s.id == stage_id:
                index = i
                break

        return index

    def _get_stage_class_by_id(self, stage_id):
        index = self._get_stage_index(stage_id)
        return self._stages[index] if index else None

    def _should_skip_init_flow(self):
        if os.path.exists(self.INIT_CONF):
            with open(self.INIT_CONF, 'r') as f:
                try:
                    init_conf = json.load(f)
                    return ('kano_init_flow' in init_conf and
                            'skip' in init_conf['kano_init_flow'] and
                            init_conf['kano_init_flow']['skip'])
                except:
                    logger.warn('Failed to parse init.conf')

        return False
