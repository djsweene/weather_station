#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
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


run = True

def middle_released_callback():
    global run
    print("middle released!")
    run = False
    
def middle_pressed_callback():
    print("middle pressed!")

def test_joystick_handler(args):
    from weather_station.joystick import joystick_handler
    from sense_emu import SenseHat
    import time
    
    hat = SenseHat()
    
    handler = joystick_handler.Stick_Daemon(hat.stick)
    handler.register_callback(joystick_handler.Direction.MIDDLE, joystick_handler.Action.RELEASED, middle_released_callback)
    handler.register_callback(joystick_handler.Direction.MIDDLE, joystick_handler.Action.PRESSED, middle_pressed_callback)
    handler.start()
    
    while run:
        time.sleep(1)
    
    
    print ("exiting!")
    return 0
    
def test_periodic_task():
    from weather_station.sensors import SensorManager
    from sense_emu import SenseHat
    import time
    
    
    hat = SenseHat()
    manager = SensorManager.PeriodicTask(hat.get_humidity, 1, 20)
    manager.start()
    
    while True:
        average = manager.get_average()
        print("average = " + str(average.timestamp) + ", " + str(average.value))
        time.sleep(0.25)
        print("out of sleep")
  
def main(args):
    import threading
    import time
    from sense_emu import SenseHat
    from weather_station.sensors import SensorManager
    
    manager = SensorManager.SensorManager(SenseHat())
    manager.start()
    
    def get_averages():
        print("----------------")
        for sensor in SensorManager.SensorEnum:
            print(sensor.name)
            print(manager.get_average(sensor).value)
        print("----------------")

    for i in range(0, 360):
        print(i)
        time.sleep(1)
        get_averages()
        
    manager.stop()

    print("exit!")
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
