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
from enum import Enum
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

    def __init__(self, task, period_seconds, samples_per_average, conversion_lambda=default_lambda):
        Thread.__init__(self)
        self._period = period_seconds
        self._task = task
        self._window_size = samples_per_average
        self._queue_lock = Lock()
        self._run = False
        
        self._converter = conversion_lambda
            
        self._queue = deque()
        self.daemon = True
        
    def run(self):
        self._run = True
        
        while self._run:
            value = self._converter(self._task())

            start_time = time.time()
            
            if self._queue_lock.acquire(timeout=self._period):
                try:
                    self._queue.appendleft(SensorRecord(time.time(), value))
                
                    if len(self._queue) > self._window_size:
                        self._queue.pop()
                except:
                    pass
                finally:
                    self._queue_lock.release()
                
                time.sleep(self._period - (time.time() - start_time))
            else:
                continue
                
    def get_average(self, timeout=-1):
        mean = 0
        
        if self._queue_lock.acquire(timeout):
            try:
                if len(self._queue) != 0:
                    for record in self._queue:
                        mean += ((1 / len(self._queue) * record.value))
            except:
                pass
            finally:    
                self._queue_lock.release()
        else:
            raise QueueAccessTimedOut
        
        return SensorRecord(time.time(), mean)
        
    def stop(self):
        self._run = False
                
class SensorEnum(Enum):
    TEMPERATURE = 0
    HUMIDITY = 1
    PRESSURE = 2
    
class SensorConfig(object):
    def __init__(self, sensor_enum, period, window, conversion=PeriodicTask.default_lambda):
        self.sensor_type = sensor_enum
        self.period = period
        self.window = window
        self.conversion = conversion


class SensorManager(object):
    #ten samples a minute
    default_sensor_configs = [SensorConfig(sensor_type, 6, 10) for sensor_type in SensorEnum]
    
    def __init__(self, sense_hat, list_of_sensor_configs=default_sensor_configs):
        self._sensor_get_functions = {SensorEnum.TEMPERATURE: sense_hat.get_temperature, 
            SensorEnum.PRESSURE: sense_hat.get_pressure, SensorEnum.HUMIDITY: sense_hat.get_humidity}
        
        self._tasks = dict()

        for config in list_of_sensor_configs:
            print(config.sensor_type.name)
            self._tasks[config.sensor_type] = PeriodicTask(
                self._sensor_get_functions[config.sensor_type], 
                config.period, config.window, config.conversion)
            
    def start(self):
        for task in self._tasks:
            self._tasks[task].start()
            
    def stop(self):
        for task in self._tasks:
            self._tasks[task].stop()
        for task in self._tasks:
            self._tasks[task].join()
            
    def get_average(self, sensor_enum):
        return self._tasks[sensor_enum].get_average()


