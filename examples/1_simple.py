#!/usr/bin/env python
# file allows to test pyfeetech library
# simple functionalities

# ----------------------------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------------------------
from pyfeetech import * # pyfeetech library


# ----------------------------------------------------------------------------------------------
# variables
# ----------------------------------------------------------------------------------------------
# Default setting
STS_ID          = 3                 # ID
STS_BAUDRATE    = 1000000           # default baudrate : 1000000
STS_PORT        = '/dev/ttyACM0'    # e.g.: Windows: "COM1", Linux: "/dev/ttyUSB0"


# ----------------------------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # - Initialize PortHandler instance
    portHandler = PortHandler(STS_PORT)

    # - initialize bus
    bus = feetechsts(portHandler)
    bus.set_verbose(True)

    # - open port
    if portHandler.openPort():
        print("[__main__] Succeeded to open port")
    else:
        print("[__main__] Failed to open port")
        quit()

    # - set port baudrate
    if portHandler.setBaudRate(STS_BAUDRATE):
        print(f"[__main__] Succeeded to set baudrate to: {STS_BAUDRATE} bps")
    else:
        print("[__main__] Failed to change baudrate")
        quit()

    # - deactivate torque
    bus.sram_set_torque_enable(STS_ID, 0)
    print("[__main__] Torque deactivated. Move the servomotor, and see its status change")
    
    # - loop
    print("[__main__] Press 'Ctrl+C' to exit this program")
    try:
        while True:
            print(
                f"position: {bus.get_position(STS_ID):5d}, "
                f"speed: {bus.get_speed(STS_ID):4d}, "
                f"load: {bus.get_load(STS_ID):4d}, "
                f"current: {bus.get_current(STS_ID):4d}, "
                f"voltage: {bus.get_voltage(STS_ID):3d}, "
                f"temperature: {bus.get_temperature(STS_ID):2d}, "
                f"status: 0b{ format( bus.get_status(STS_ID) ,'05b') }"
            )

    except KeyboardInterrupt:
        print("[__main__] Keyboard interrupt detected. Exiting.")

    finally:
        # - deactivate torque
        bus.sram_set_torque_enable(STS_ID, 0)
        
        # - close connection
        portHandler.closePort()
        print("[__main__] Connection closed")

    # - close connection
    #portHandler.closePort()
    print("[__main__] Connection closed. Exit program")