#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  joystick_handler.py
#  
#  Copyright 2019 Doug Sweeney <djsweene@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from threading import Thread
from threading import Lock
from enum import Enum

class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'
    
class Action(Enum):
    PRESSED = 'pressed'
    RELEASED = 'released'
    HELD = 'held'
        
class Stick_Daemon(object):
    
    def __init__(self, sense_hat_stick_object):
        self._daemon_thread = Thread(target=self.stick_daemon, daemon=True)
        self._callbacks = dict()
        self._stick = sense_hat_stick_object
        self._callback_guard = Lock()
        
    def register_callback(self, button_direction, button_action, callback):
        """
        button_direction: Direction enum
        button_action: Action enum
        callback: the function that is to be called without arguement when action occurs
        """
        with self._callback_guard:
            if button_direction in self._callbacks:
                self._callbacks[button_direction][button_action] = callback
            else:
                self._callbacks[button_direction] = {button_action: callback}
        
    def stick_daemon(self):
        while True:
            event = self._stick.wait_for_event()
            
            with self._callback_guard:
                if Direction(event.direction) in self._callbacks:
                    if Action(event.action) in self._callbacks[Direction(event.direction)]:
                        self._callbacks[Direction(event.direction)][Action(event.action)]()
            
    def start(self):
        self._daemon_thread.start()
        
