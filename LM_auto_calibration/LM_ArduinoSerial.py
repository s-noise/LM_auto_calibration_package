import serial
import sys


# class for managing the serial connection and reading of integer values
class LM_ArduinoSerial:


    def __init__(self):
        self.ser=None                                 # initialize serial object


    # open serial connection with static device name (see: arduino-Uno-Rev3.rules):
    def openconnection(self,the_serialport='/dev/LM_auto_calib_arduino'):
        # connect to serial interface
        # configure the serial connections 
        try:                                          # settings for default arduino (SERIAL_8N1)
            self.ser = serial.Serial(
                port=the_serialport, 
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print('established serial connection')               # confirm connection message
            return True                                          # returnvalue to confirm connection
        except (OSError, TypeError, ValueError, serial.SerialException) as err:
            print(err) 
            print("\ncould not connect to serial device")        # failed to connect message
            return False                                         # returnvalue if failed to connect


    def closeconnection(self):
        try:
            self.ser.close()
            print("closed serial connection")
        except: 
            pass


    # read 1 byte from serial device, convert it into an integer value and return it
    #     signed integer is choosen, to be able to send negative values:
    def readbyte_request(self,errorvalue=21,the_byteorder='little',the_signed='True'):
        try:
            returnbyte=int.from_bytes(self.ser.read(size=1),byteorder=the_byteorder,signed=the_signed)
            self.ser.reset_input_buffer()
            return returnbyte
        except (TypeError, ValueError, serial.SerialException) as err:
            print(err)
            print("\nerror when reading from connected serial device")     
            return int(errorvalue)                 # return integer for error handling, here: 21 as default


    # check function, checks if a serial device is connected:
    def connected(self):
        try:
            if(self.ser.cd==False):      # dc ... carrier detect signal (control signal):
                boolean=True             #     self.ser.cd returns False if a carrier (connected device) is detected and undefined (=> error) else
        except:
            boolean=False
        return boolean                   # returns True or False

