# pyfeetech

## Overview
`pyfeetech` is a Python library to control Feetech servomotors
The lib is forked from Waveshare code, downloadable at: https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A) 

## Hardware requirements
- Waveshare Bus Servo Adapter (A)
- Feetech servomotor (e.g. STS3215)
- 12 V, 5 A power supply

## Installation
Run the following command in your terminal:

```
pip install -e .
```

### Setup permissions for serial port
#### Option 1
```
sudo usermod -a -G dialout $USER
```
USER will need to log out & log back in again for this to take effect

#### Option 2
```
sudo adduser $USER dialout
```
USER will need to log out & log back in again for this to take effect

#### Option 3
```
sudo chmod 666 /dev/ttyACM0
```

## Un-install
If you need to un-install, run:

```
pip uninstall pyfeetech
```

## Usage
Use the following example files as starting point:
- examples/1_simple.py
- examples/2_advanced.py

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.