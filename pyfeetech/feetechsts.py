#!/usr/bin/env python

# Author: Luca Randazzo
# Description: Python library to control Feetech STS motors.
# Forked from waveshare code for feetech servomotors 

# ---------------------------------------------------------------
# Bus class
# ---------------------------------------------------------------
# imports
import math
from .stservo_def import *
from .protocol_packet_handler import *
from .group_sync_read import *
from .group_sync_write import *

# Baudrates
STS_1M                  = 0
STS_0_5M                = 1
STS_250K                = 2
STS_128K                = 3
STS_115200              = 4
STS_76800               = 5
STS_57600               = 6
STS_38400               = 7

# Modes
STS_MODE_POSITION       = 0
STS_MODE_SPEED          = 1
STS_MODE_PWM            = 2
STS_MODE_STEP           = 3

# Registers
# - EPROM
STS_MODEL_L             = 3
STS_MODEL_H             = 4
STS_ID                  = 5
STS_BAUD_RATE           = 6
STS_MIN_ANGLE_LIMIT_L   = 9
STS_MAX_ANGLE_LIMIT_L   = 11
STS_MAX_TORQUE_LIMIT_L  = 16
STS_MIN_STARTUP_FORCE_L = 24
STS_CW_DEAD             = 26
STS_CCW_DEAD            = 27
STS_PROTECTION_CURRENT_L= 28
STS_OFS_L               = 31
STS_OFS_H               = 32
STS_MODE                = 33
STS_PROTECTIVE_TORQUE   = 34

# - SRAM
STS_TORQUE_ENABLE       = 40
STS_ACC                 = 41
STS_GOAL_POSITION_L     = 42
STS_GOAL_TIME_L         = 44
STS_GOAL_SPEED_L        = 46
STS_TORQUE_LIMIT_L      = 48
STS_LOCK                = 55
STS_PRESENT_POSITION_L  = 56
STS_PRESENT_SPEED_L     = 58
STS_PRESENT_LOAD_L      = 60
STS_PRESENT_VOLTAGE     = 62
STS_PRESENT_TEMPERATURE = 63
STS_STATUS              = 65
STS_MOVING              = 66
STS_PRESENT_CURRENT_L   = 69

#
class feetechsts(protocol_packet_handler):
    #
    def __init__(self, portHandler):
        self.verbose = False
        protocol_packet_handler.__init__(self, portHandler, 0)
        self.groupSyncWrite = GroupSyncWrite(self, STS_ACC, 7)   

    #
    def set_verbose(self, verbosity):
        self.verbose = verbosity

    #
    def print_status(self, status):
        if status == 0:      print(f"[print_status]: No error")
        if status & 0b00001: print(f"[print_status]: ERROR: Overload")
        if status & 0b00010: print(f"[print_status]: ERROR: Angle")
        if status & 0b00100: print(f"[print_status]: ERROR: Current")
        if status & 0b01000: print(f"[print_status]: ERROR: Temperature")
        if status & 0b10000: print(f"[print_status]: ERROR: Voltage")


    # ----- setters, EEPROM
    # for all eeprom calls, if you want changes to be stored on the motor also after power-cycling
    # you have to: set lock to 0, then write on the register, and then set lock to 1
    # if the lock is not set to 0, changes will not be stored on the motor after power-cycling,
    # i.e. they will only be applied to the current session
    #
    def eeprom_set_id(self, motor_id, new_id):
        current_id = self.get_id(motor_id)
        
        # write on EEPROM only if needed
        if current_id != new_id:
            if self.verbose: print(f"[feetechsts::eeprom_set_id] (EEPROM) Setting ID to: {new_id}...")

            # write
            sts_comm_result, sts_error = self.write1ByteTxRx(motor_id, STS_ID, new_id)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_id] (EEPROM) ID correctly set to: {new_id}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_id] ID was already: {new_id}. Not setting")
            return current_id

    #
    # {0, 1, 2, 3}
    # 0: Position mode
    # 1: Constant speed mode
    # 2: PWM open-loop speed regulation mode
    # 3: Step servo mode
    def eeprom_set_mode(self, motor_id, mode):
        current_mode = self.get_mode(motor_id)
        
        # write on EEPROM only if needed
        if current_mode != mode:
            if self.verbose: print(f"[feetechsts::eeprom_set_mode] (EEPROM) Setting mode to: {mode}...")

            # write
            sts_comm_result, sts_error = self.write1ByteTxRx(motor_id, STS_MODE, mode)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_mode] (EEPROM) mode correctly set to: {mode}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_mode] Mode was already: {mode}. Not setting")
            return current_mode

    #
    # {0, 1}
    # 0: closes the write lock, and the value written to EPROM address is saved after power-cycling
    # 1: opens the write lock, and the value written to EPROM address is not saved after power-cycling
    def eeprom_set_lock(self, motor_id, lock_status):
        current_lock = self.get_lock(motor_id)
        
        # write on EEPROM only if needed
        if current_lock != lock_status:
            if self.verbose: print(f"[feetechsts::eeprom_set_lock] (EEPROM) Setting lock status to: {lock_status}...")

            # write
            sts_comm_result, sts_error = self.write1ByteTxRx(motor_id, STS_LOCK, lock_status)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_lock] (EEPROM) lock status correctly set to: {lock_status}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_lock] lock status was already: {lock_status}. Not setting")
            return current_lock

    #
    # [0, 4094]
    def eeprom_set_angle_min(self, motor_id, angle):
        min_angle = self.get_angle_min(motor_id)
        
        # write on EEPROM only if needed
        if min_angle != angle:
            if self.verbose: print(f"[feetechsts::eeprom_set_angle_min] (EEPROM) Setting min angle to: {angle}...")

            # write
            temp_angle = self.sts_toscs(angle, 15)
            #sts_comm_result, sts_error = self.write2ByteTxRx(motor_id, STS_MIN_ANGLE_LIMIT_L, temp_angle)
            txpacket = [self.sts_lobyte(temp_angle), self.sts_hibyte(temp_angle)]
            sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_MIN_ANGLE_LIMIT_L, len(txpacket), txpacket)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_angle_min] (EEPROM) min angle correctly set to: {angle}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_angle_min] min angle was already: {angle}. Not setting")
            return min_angle

    #
    # [0, 4095]
    def eeprom_set_angle_max(self, motor_id, angle):
        max_angle = self.get_angle_max(motor_id)
        
        # write on EEPROM only if needed
        if max_angle != angle:
            if self.verbose: print(f"[feetechsts::eeprom_set_angle_max] (EEPROM) Setting max angle to: {angle}...")

            # write
            temp_angle = self.sts_toscs(angle, 15)
            #sts_comm_result, sts_error = self.write2ByteTxRx(motor_id, STS_MAX_ANGLE_LIMIT_L, temp_angle)
            txpacket = [self.sts_lobyte(temp_angle), self.sts_hibyte(temp_angle)]
            sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_MAX_ANGLE_LIMIT_L, len(txpacket), txpacket)

            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_angle_max] (EEPROM) max angle correctly set to: {angle}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_angle_max] max angle was already: {angle}. Not setting")
            return max_angle

    #
    # [0, 1000]
    def eeprom_set_torque_max(self, motor_id, torque):
        max_torque = self.get_torque_max(motor_id)
        
        # write on EEPROM only if needed
        if torque != max_torque:
            if self.verbose: print(f"[feetechsts::eeprom_set_torque_max] (EEPROM) Setting max torque to: {torque}...")

            # write
            temp_torque = self.sts_toscs(torque, 15)
            #sts_comm_result, sts_error = self.write2ByteTxRx(motor_id, STS_MAX_TORQUE_LIMIT_L, temp_torque)
            txpacket = [self.sts_lobyte(temp_torque), self.sts_hibyte(temp_torque)]
            sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_MAX_TORQUE_LIMIT_L, len(txpacket), txpacket)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_torque_max] (EEPROM) max torque correctly set to: {torque}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_torque_max] max torque was already: {torque}. Not setting")
            return max_torque

    #
    # [0, 1000]
    def eeprom_set_force_startup_min(self, motor_id, force):
        present_force = self.get_force_startup_min(motor_id)
        
        # write on EEPROM only if needed
        if force != present_force:
            if self.verbose: print(f"[feetechsts::eeprom_set_force_startup_min] (EEPROM) Setting min startup force to: {force}...")

            # write
            temp_force = self.sts_toscs(force, 15)
            #sts_comm_result, sts_error = self.write2ByteTxRx(motor_id, STS_MIN_STARTUP_FORCE_L, temp_force)
            txpacket = [self.sts_lobyte(temp_force), self.sts_hibyte(temp_force)]
            sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_MIN_STARTUP_FORCE_L, len(txpacket), txpacket)
            
            # process errors
            if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
            if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

            # result
            if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
                if self.verbose: print(f"[feetechsts::eeprom_set_force_startup_min] (EEPROM) min startup force correctly set to: {force}")
    
        else:
            if self.verbose: print(f"[feetechsts::eeprom_set_force_startup_min] min startup force was already: {force}. Not setting")
            return present_force


    # ----- setters, RAM
    #
    # {0, 1, 128}
    # 0: turn off torque output
    # 1: turn on torque output
    # 128: current position correction is 2048    
    def sram_set_torque_enable(self, motor_id, torque_status):
        if self.verbose: print(f"[feetechsts::sram_set_torque_enable] Setting torque to: {torque_status}...")

        # write
        sts_comm_result, sts_error = self.write1ByteTxRx(motor_id, STS_TORQUE_ENABLE, torque_status)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # result
        if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
            if self.verbose: print(f"[feetechsts::sram_set_torque_enable] torque correctly set to: {torque_status}")

    #
    # [0, 254]
    def sram_set_acceleration(self, motor_id, acceleration):
        if self.verbose: print(f"[feetechsts::sram_set_acceleration] Setting acceleration to: {acceleration}...")

        # write
        sts_comm_result, sts_error = self.write1ByteTxRx(motor_id, STS_ACC, acceleration)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # result
        if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
            if self.verbose: print(f"[feetechsts::sram_set_acceleration] acceleration correctly set to: {acceleration}")

    #
    # [-32766, 32766]    
    def sram_set_position(self, motor_id, position):
        if self.verbose: print(f"[feetechsts::sram_set_position] Setting position to: {position}...")

        # write
        temp_position = self.sts_toscs(position, 15)
        txpacket = [self.sts_lobyte(temp_position), self.sts_hibyte(temp_position)]
        sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_GOAL_POSITION_L, len(txpacket), txpacket)

        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # result
        if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
            if self.verbose: print(f"[feetechsts::sram_set_position] position correctly set to: {position}")

    #
    # [0, 254]    
    def sram_set_speed(self, motor_id, speed):
        if self.verbose: print(f"[feetechsts::sram_set_speed] Setting speed to: {speed}...")

        # write
        temp_speed = self.sts_toscs(speed, 15)
        txpacket = [self.sts_lobyte(temp_speed), self.sts_hibyte(temp_speed)]
        sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_GOAL_SPEED_L, len(txpacket), txpacket)

        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # result
        if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
            if self.verbose: print(f"[feetechsts::sram_set_speed] speed correctly set to: {speed}")

    #
    # [0, 1000]    
    def sram_set_torque_limit(self, motor_id, torque):
        if self.verbose: print(f"[feetechsts::sram_set_torque_limit] Setting torque limit to: {torque}...")

        # write
        temp_torque = self.sts_toscs(torque, 15)
        txpacket = [self.sts_lobyte(temp_torque), self.sts_hibyte(temp_torque)]
        sts_comm_result, sts_error = self.writeTxRx(motor_id, STS_TORQUE_LIMIT_L, len(txpacket), txpacket)

        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # result
        if (sts_comm_result == COMM_SUCCESS) & (sts_error == 0):
            if self.verbose: print(f"[feetechsts::sram_set_torque_limit] torque limit correctly set to: {torque}")


    # ----- getters
    #
    def get_id(self, motor_id):
        sts_id, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_ID)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_id, 15)

    #
    def get_angle_min(self, motor_id):
        sts_angle_min, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_MIN_ANGLE_LIMIT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_angle_min, 15)

    #
    def get_angle_max(self, motor_id):
        sts_angle_max, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_MAX_ANGLE_LIMIT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_angle_max, 15)

    #
    def get_torque_max(self, motor_id):
        sts_torque_max, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_MAX_TORQUE_LIMIT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_torque_max, 15)

    #
    def get_force_startup_min(self, motor_id):
        sts_force_startup_min, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_MIN_STARTUP_FORCE_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_force_startup_min, 15)

    #
    def get_protection_current(self, motor_id):
        sts_protection_current, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_PROTECTION_CURRENT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_protection_current, 15)

    #
    def get_mode(self, motor_id):
        sts_mode, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_MODE)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_mode, 15)

    #
    def get_torque_enable(self, motor_id):
        sts_torque_enable, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_TORQUE_ENABLE)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_torque_enable, 15)
    
    #
    def get_protective_torque(self, motor_id):
        sts_protective_torque, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_PROTECTIVE_TORQUE)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_protective_torque, 15)

    #
    def get_position(self, motor_id):
        sts_position, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_PRESENT_POSITION_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_position, 15)

    #
    def get_speed(self, motor_id):
        sts_speed, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_PRESENT_SPEED_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_speed, 15)

    #
    def get_load(self, motor_id):
        sts_load, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_PRESENT_LOAD_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_load, 15)

    #
    def get_voltage(self, motor_id):
        sts_voltage, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_PRESENT_VOLTAGE)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_voltage, 15)

    #
    def get_status(self, motor_id):
        sts_status, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_STATUS)
        
        # print status if there is an error
        if (sts_status!=0): self.print_status(sts_status)

        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_status, 15)

    #
    def get_temperature(self, motor_id):
        sts_temperature, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_PRESENT_TEMPERATURE)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return sts_temperature

    #
    def get_current(self, motor_id):
        sts_current, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_PRESENT_CURRENT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_current, 15)

    #
    def get_torque_limit(self, motor_id):
        sts_current, sts_comm_result, sts_error = self.read2ByteTxRx(motor_id, STS_TORQUE_LIMIT_L)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_current, 15)

    #
    def get_lock(self, motor_id):
        sts_lock_status, sts_comm_result, sts_error = self.read1ByteTxRx(motor_id, STS_LOCK)
        
        # process errors
        if sts_comm_result != COMM_SUCCESS: print("%s" % self.getTxRxResult(sts_comm_result))
        if sts_error != 0:                  print("%s" % self.getRxPacketError(sts_error))

        # convert to signed and return
        return self.sts_tohost(sts_lock_status, 15)    
# ---------------------------------------------------------------