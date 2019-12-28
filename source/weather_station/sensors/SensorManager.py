#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  SensorManager.py
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
import time
from collections import deque

def celsius_to_farenheit(temp_c):
    return (temp_c * 9/5) + 32

class QueueAccessTimedOut(Exception):
    'Timed out waiting for access to the queue'
    pass

class SensorRecord(object):
    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value

class PeriodicTask(Thread):
    default_lambda = lambda x: x

    def __init__(self, task, period_seconds, samples_per_average, conversion_lambda=None):
        self._period = period_seconds
        self._task = task
        self._window_size = samples_per_average
        self._queue_lock = Lock()
        self._run = False
        
        if conversion_lambda is not None:
            self._converter = conversion_lambda
        else:
            self._converter = self.default_lambda
            
        self._queue = deque()
        self.daemon = True
        
    def run(self):
        while self._run:
            value = self._converter(self._task())
            
            start_time = time.time()
            if self._queue_lock.acquire(timeout=self._period):
                
                self._queue.append_left(value)
                
                if self._queue.count() > self._window_size:
                    self._queue.pop()
                self._queue_lock.release()
                
                time.sleep(self._period - (time.time() - start)) 
            else:
                continue
                
    def get_average(timeout=-1):
        
        if self._queue_lock.acquire(timeout):
            for value in self._queue:
                mean += ((1 / self._queue.count()) * value)
            return value
        else:
            raise QueueAccessTimedOut
                
    
                
            
            
            
        
