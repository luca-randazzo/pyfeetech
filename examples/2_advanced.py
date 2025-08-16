#!/usr/bin/env python
# this file allows to test pyfeetech library
# advanced functionalities

# -----------------------------------------------
# imports
# -----------------------------------------------
from __future__ import print_function
import sys
import os
import time
import threading
# imports for keyboard
import tty
import termios
import atexit

# 
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# pyfeetech library
from pyfeetech import * 

# ----------------------------------------------------------------------------------------------
# variables
# ----------------------------------------------------------------------------------------------
# Default setting
STS_ID          = 4                 # ID
STS_BAUDRATE    = 1000000           # default baudrate : 1000000
STS_PORT        = '/dev/ttyACM0'    # e.g.: Windows: "COM1", Linux: "/dev/ttyACM0"

thread_sleep_time = 0.001

# ----------------------------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------- Keyboard
    #
    def keyboard_restore_settings(): termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    #    
    def keyboard_thread():
        global key

        # - init keyboard
        global old_settings
        atexit.register(keyboard_restore_settings)
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        # info
        print("[keyboard_thread] use the following commands: ")
        print("[keyboard_thread] -> keyboard 'arrow up':   position=-4095")
        print("[keyboard_thread] -> keyboard 'arrow down': position=4095")
        print("[keyboard_thread] -> keyboard 'space-bar':  position=0")
        print("")

        try:
            while True:
                c = sys.stdin.read(1)
                #print("[keyboard_thread] pressed: '%s'" % c)
                
                if    c=='A':
                    #print("[keyboard_thread] pressed 'arrow_up'")
                    key = 1

                elif  c=='B':
                    #print("[keyboard_thread] pressed 'arrow down'")
                    key = 2

                elif  c==' ':
                    #print("[keyboard_thread] pressed 'spacebar'")
                    key = 3

                #
                time.sleep(thread_sleep_time)

        except Exception as e:
            print(f"[thread_keyboard] Exception: {e}")

    #
    global key
    key = 0

    # start keyboard handling in a separate thread
    key_thread = threading.Thread(target=keyboard_thread)
    key_thread.daemon = True  # Daemonize thread so it automatically exits when the main program ends
    key_thread.start()


    # --------- Bus
    # - Initialize PortHandler instance
    portHandler = PortHandler(STS_PORT)

    # - initialize bus
    bus = feetechsts(portHandler)
    #bus.set_verbose(False)
    bus.set_verbose(True)

    # - open port
    if portHandler.openPort():
        print("[__main__] Succeeded to open port")
    else:
        print("[__main__] Failed to open port")
        print("[__main__] Press any key to terminate...")
        getch()
        quit()

    # - set port baudrate
    if portHandler.setBaudRate(STS_BAUDRATE):
        print("[__main__] Succeeded to change baudrate")
    else:
        print("[__main__] Failed to change baudrate")
        print("[__main__] Press any key to terminate...")
        getch()
        quit()


    # --------- Control motors directly via bus
    # for all eeprom calls, if you want changes to be stored on the motor also after power-cycling
    # you have to: set lock to 0, then write on the register, and then set lock to 1
    # if the lock is not set to 0, changes will not be stored on the motor after power-cycling,
    # i.e. they will only be applied to the current session

    # - set ID
    #bus.eeprom_set_lock(1, 0)     # motor with ID = 1: set lock status = 0. this ensures that the next EEPROM write is stored on the motor also after power-cycling it
    #bus.eeprom_set_id(1, 7)       # motor with ID = 1: set ID=7
    #bus.eeprom_set_lock(1, 1)     # motor with ID = 1: set lock status = 1

    # - set max torque
    #bus.eeprom_set_lock(STS_ID, 0)
    #bus.eeprom_set_torque_max(STS_ID, 1000)
    #bus.eeprom_set_lock(STS_ID, 1)
    #print(f"[__main__] torque max:         {bus.get_torque_max(STS_ID):04d}")

    # - set min startup force
    #bus.eeprom_set_lock(STS_ID, 0)
    #bus.eeprom_set_force_startup_min(STS_ID, 1000)
    #bus.eeprom_set_lock(STS_ID, 1)
    #print(f"[__main__] force_startup_min:  {bus.get_force_startup_min(STS_ID):04d}")

    # - activate/deactivate torque
    #bus.sram_set_torque_enable(STS_ID, 0)
    #print(f"[__main__] torque enable:         {bus.get_torque_enable(STS_ID):04d}")

    # - set speed and acceleration
    #bus.sram_set_speed(STS_ID, 254)
    #bus.sram_set_acceleration(STS_ID, 254)

    # - set torque limit
    #bus.sram_set_torque_limit(STS_ID, 500)
    #print(f"[__main__] torque limit:       {bus.get_torque_limit(STS_ID):04d}")

    # - position mode
    #bus.eeprom_set_mode(STS_ID, STS_MODE_POSITION)
    #bus.sram_set_position(STS_ID, 0)

    # - step mode
    #bus.eeprom_set_mode(STS_ID, STS_MODE_STEP)
    #bus.sram_set_position(STS_ID, 100)  # +100 steps
    #bus.sram_set_position(STS_ID, -100) # -100 steps

    # - multiturn mode
    # note: Feetech manual reports "power failure does not save the number of turns"
    #       i.e. if motor is powered off, it will not record how many muliturns it made,
    #       but it will start from the current value of its encoder
    # in order to activate multiturn mode, the following 3 calls have to be made 
    #bus.eeprom_set_mode(STS_ID, STS_MODE_POSITION)    
    #bus.eeprom_set_angle_min(STS_ID, 0)
    #bus.eeprom_set_angle_max(STS_ID, 0)
    # then, motor can achieve multiturns with e.g.:
    #bus.sram_set_position(STS_ID, -1*4095)  # -1 full rotation
    #bus.sram_set_position(STS_ID, 1*4095)   # +1 full rotation

    # - speed mode
    #bus.eeprom_set_mode(STS_ID, STS_MODE_SPEED)
    #bus.sram_set_speed(STS_ID, 500)

    # - test print_status() function
    #bus.print_status(0b11111)    

    # - loop
    print("[__main__] Press 'Ctrl+C' to exit this program")
    try:
        while True:
            # - Get current time
            current_time = time.time()
            milliseconds = int((current_time - int(current_time)) * 1000)
            
            # - Format date and time
            date = time.strftime('%Y%m%d')  # Date as YYYYMMDD
            time_str = time.strftime(f'%Hh%Mm%Ss{milliseconds:03d}ms')  # Time with milliseconds

            # --- Read and print from motor, through bus        
            #( f"[{time_str}] " f"position: {bus.get_position(STS_ID):5d}, ")
            
            print(
                f"[{time_str}] "
                f"position: {bus.get_position(STS_ID):5d}, "
                f"speed: {bus.get_speed(STS_ID):4d}, "
                f"load: {bus.get_load(STS_ID):4d}, "
                f"current: {bus.get_current(STS_ID):4d}, "
                f"voltage: {bus.get_voltage(STS_ID):3d}, "
                f"temperature: {bus.get_temperature(STS_ID):2d}, "
                f"status: 0b{ format( bus.get_status(STS_ID) ,'05b') }"
            )


            # --- Process keyboard
            if      key==1: # arrow up
                bus.sram_set_position(STS_ID, -1*4095) # multiturn mode
                #bus.set_position(STS_ID, 100)  # +100 steps
                key = 0
            
            elif    key==2: # arrow down
                bus.sram_set_position(STS_ID, 1*4095)  # multiturn mode
                #bus.set_position(STS_ID, -100)  # -100 steps
                key = 0
            
            elif    key==3: # spacebar
                bus.sram_set_position(STS_ID, 0)
                key = 0

    except KeyboardInterrupt:
        print("[__main__] Keyboard interrupt detected. Exiting.")

    finally:
        # - deactivate torque
        bus.sram_set_torque_enable(STS_ID, 0)
        
        # - close connection
        portHandler.closePort()
        print("[__main__] Connection closed")