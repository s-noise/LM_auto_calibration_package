[//]: # (open e.g. with grip: grip -b README.md)

# LM_auto_calibration

*LM_auto_calibration* is a python package and nionswift extension for use in combination with a light microscope (LM) and camera.
It is used for the determination of the inserted objective of the LM and for automatically setting the correct pixel to um scale in nionswift from a *.json* calibration file.

The package requires the *matrix_vision_camera* python package from Andreas Mittelberger. The *matrix_vision_camera* package implemets the use of a Matrix Vision camera in nionswift. The hardware setup consists of a Matrix Vision camera for the LM, a microcontroller (Arduino Uno Rev3) and one sensor (here: reed switch) per objective at the LM. The *LM_auto_calibration* package default state is written for 5 objectives (senors) but can be easily adapted.

An inserted objective corresponds to one specific sensor beeing active at the LM. The microcontroller numbers the sensors, reads out all sensors at the LM, detects the active one and sends an integer number corresponding to the active senor to the PC with nionswift installed (per serial connection; virtual com port over USB). Different error values are send if no sensor or multiple senors are detected. A smoothing algorithm only sends the signal that has been stable for 3 seconds (default vaule). The microcontroller continuously sends signals as long as nionswift is open and as long as the camera was started once.

Arduino Uno Rev3 microcontroller: A "send" LED blinks fast when data is send. A "control" LED blinks in a 3 second (default value) interval as long as the program is running on the microcontroller.

*LM_auto_calibration* reads the signal as a single byte per time and converts it back to an integer value. The continuous reading rate is slower that the sending rate of the microconroller on purpose. The read buffer is emptied after every read to keep the read signal up-to-date. On objective change the integer value changes. A LM_auto_calibration status panel in nionswift will show the active objective (magnification) for the auto calibration. On objective change the new auto calibration will be read from the *.json* calibration file (e.g.: in */home/username/.config/matrix_vision/*). If the active setting of the Matrix Vision Control panel in nionswift is the "auto" setting (this setting is added by the *LM_auto_calibration* python package), the new pixel to um scale will be set for the camera by *LM_auto_calibration*.


### Included files

* Python modules in the *LM_auto_calibration* package and nionswift extension:
  - *LM_ArduinoSerial.py*, *LM_auto_calibration.py*
* adapted Python module of *the matrix_vision_camera* python package (*mv_camera* sub-package):
  - *MVCamControlPanel.py*
* adapted *.json* calibration file; rename the file to the hardware source id of the camera in nionswift:
  - *hardware-source-id.json*
* Arduino Uno Rev3 microcontroller script for sensor read out and serial communication (virtual com port over USB) with the PC:
  - *LMikro_Arduino_1.ino* (for Arduino Uno Rev3)
* Linux:  udev rules file to add a static device adress for the microcontroller (Arduino Uno Rev3):
  - *arduino-Uno-Rev3.rules*

## Installation

For Linux systems.  
For other systems: change serial connection - device name (see: LM_ArduinoSerial.py and arduino-Uno-Rev3.rules)
<br />
<br />
Move to the *LM_auto_calibration_package* directory where the *setup.py* file is located  
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install *LM_auto_calibration* if the conda nionswift environment is active:

```bash
conda activate nionswift
```

```bash
pip install .
```

pip can also be found in the bin directory of the conda nionswift environment  
executing pip from there makes activating the conda nionswift environmet redundant:

```bash
/home/username/miniconda3/envs/nionswift/bin/pip install .
```

Move to the *mv_camera* directory in the *matrix_vision_camera* package where the *MVCamControlPanel.py* file is located.  
Rename the file, e.g.: *MVCamControlPanel__original.py*  
Replace *MVCamControlPanel.py* with the file provided in the *LM_auto_calibration_package* directory  
(same name: *MVCamControlPanel.py*)
<br />
<br />
In nionswift: get the hardware source id of the camera (in the metadata of camera play window).  
The id must match the hardware source id in *LM_auto_calibration.py* (*'video_device_1'* is the default id string)
<br />
<br />
Move to the directory with the *.json* calibration file, e.g.: in */home/username/.config/matrix_vision/*.  
Note the current pixel to um scales in the file. Replace the file with the *hardware-source-id.json* calibration file  
provided in the *LM_auto_calibration_package* directory. Rename the file to the original file name,  
which is given by the hardware source id of the camera (e.g.: *video_device_1.json*).  
Insert the correct pixel to um scales in the new *.json* calibration file.
<br />
<br />
Copy the udev rule file named *arduino-Uno-Rev3.rules* to */etc/udev/rules.d/*  
The file is provided in the *LM_auto_calibration_package* directory
<br />
<br />
Load the *LMikro_Arduino_1.ino* script to the Arduino Uno Rev3 microcontroller.  
The file is provided in the *LM_auto_calibration_package* directory
<br />
<br />
Connect sensors (reed switches) and microcontroller  
Connect microcontroller and PC via USB



## Setting up the Arduino Uno Rev3 microcontroller


Voltage controlled sensor circuits:

The internal pull up resistors (>20 kOhm) are used for the digital Pins 2-6 at the microcontroller.
The 5 reed switches (sensors) are connected to the 5 digital Pins 2-6 on one side and to a ground Pin on the other side.
Thus, if a switch is closed the Pin is pulled to ground (Low). The switches are on 5 V (High) otherwise.
The switches are closed by a magnet on the objective revolver. The magnet turns with the revolver and closes one switch at a time in accordance with the objective positions.


## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)

