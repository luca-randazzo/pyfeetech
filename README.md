# pyfeetech

## Overview
`pyfeetech` is a Python library to control Feetech servomotors.
The lib is forked from Waveshare code, downloadable at: https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A).

## Requirements
### Hardware
- Waveshare Bus Servo Adapter (A)
- Feetech servomotor (e.g. STS3215) + 3poles wire harness
- 12 V, 2+ A power supply

### Software
The library has been tested under Ubuntu 22.04.5 LTS running Pyhton 3.12

## Installation
- Download the repo from: https://github.com/luca-randazzo/pyfeetech 
- `cd` to the directory of the downloaded repo 
- Run the following command in your terminal:
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
(change "/dev/ttyACM0" to the port where the Waveshare adapted is connected)

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
