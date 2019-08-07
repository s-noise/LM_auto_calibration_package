import numpy
import threading
import time
import gettext
from nion.utils import Event
from mv_utils import connect_camera
import sys
from . import LM_ArduinoSerial


_ = gettext.gettext




# class for trigger an Event; used to change displayed text in a nionswift panel
class TriggerTextChange: 

     
    def __init__(self):
        self.text_change_event = Event.Event()


    def on_external_event(self):                 # tigger Event when this function is called
        self.text_change_event.fire()




# class that defines the panel in nionswift and the "main" (magnification calibration) fucntion that will run in a thread (t1)
class LMConnectionDelegate:
      

    def __init__(self, api,serialobject):
        self.__api = api
        self.panel_id = "LM_auto_calib_connection"
        self.panel_name = "LM auto calibration status:"
        self.panel_positions = ['left', 'right']
        self.panel_position = 'right'

        # initialize classes , threads and variables
        self.__trigger_text_change = TriggerTextChange() #class to change displayed text
        self.__live_text= None                           # init live text variable to change displayed text
        self.__t1=None                                   # init thread object
        self.__serialobject=serialobject               # pass on the class to read serial input; see: LMConnectionExtension() and LM_ArduinoSerial

        # initialize clamera settings
        # !!! HARDWARE SOURCE ID FOR CAMERA IS DEFINED HERE !!!
        #   it is not choosen automatically, this has to be looked up in 
        #   nionswift (see metadata)  and it has to match the choosen camera in the Matrix Vision Control panel
        ##################################################
        self.__hardware_source_id = 'video_device_1'     # look up in nionswift, metadata of camera play window
        ##################################################
        self.__current_camera_device = None
        self.__current_camera_settings = None

        # set magnification array: look up string names of possible magnifications in the .json calibration file
        #     the items in this array must fit to the entries there and 
        #     to the items in MVCamControlPanel.py in the mv_camera package, except for 'not_scaled'
        # the order of elements correspond to the received numbers (order of sensors / reed switches):
        #     self.__magnifications[1] == recieved 1 (sensor 1) , self.__magnifications[1] == recieved 2 (sensor 2) , ...
        #     self.__magnifications[0] == error values: recieved 11, 12 (special cases), or else (!= 1,2,3,4,5)
        ########################################################################
        self.__magnifications=['not_scaled','5x','10x','20x','50x','100x']     #
        ########################################################################
 

    # create the panel in nionswift the ui and document_controler will be asserted by the create panel funcion in the class call: 
    # see LMConnectionExtension():
    def create_panel_widget(self, ui, document_controller):
        #self.dc = document_controller                                          # not needed here
        self.__live_text_panel=ui.create_label_widget(text="OFF (start camera)")  # displays a line with text or values in a nionswift panel
        self.main()                                                             # run the main (magnification calibration) function 
        return self.__live_text_panel


    # function to get a text for displaying and to trigger the text changing event (to tell nionswift to change the text) :
    def get_panel_text(self,string):
        self.__trigger_text_change.on_external_event()                            # see: TriggerTextChange()
        return str(string)   


    # function to set the text of the display panel :
    def set_panel_text(self,string):
        self.__live_text_panel.text=str(string)


    # function to set the spatial calibration scale of the camera,
    # read and writes to the .json file with the spatial calibrations (see connect_camera.py file of mv_utils package) :
    def autoscale(self,magnification,hardware_source_id): 
        try:
            # load camera settings to get binning value & calibration (read from .json calibration file): 
            self.__current_camera_device = self.__api.get_hardware_source_by_id(hardware_source_id,'1')  
            self.__current_camera_settings=connect_camera.CameraSettings(self.__current_camera_device._hardware_source.video_device)
            connect_camera.load_spatial_calibrations(self.__current_camera_settings)
        
            # get magnifincation from serial connection (LM microscope) and 
            #     get "active" setting, that is the currently choosen magnification (item) in nionswift;
            #     (MVCamControlPanel.py in the mv_camera package writes the "active" setting to the .json calibration file):
            calib=self.__current_camera_settings.spatial_calibration_dict.get(str(magnification), dict()).copy()
            active=self.__current_camera_settings.spatial_calibration_dict.get('active', dict())

            # update .json calibration file: write the new 'auto' calibration :
            self.__current_camera_settings.spatial_calibration_dict.update(auto = calib)
            connect_camera.save_spatial_calibrations(self.__current_camera_settings)
          
            # multiply not binned pixel scale by the current binning :
            calib['scale'] = calib['scale'] * self.__current_camera_settings.binning

            # set calibration of camera only if the active (choosen) setting in the Matrix Vision Control panel is the 'auto' setting:
            if (active=='auto'):  
                self.__current_camera_device._hardware_source.video_device.spatial_calibrations = [calib, calib]           
        except (OSError, EOFError, IOError, KeyError) as err:
            print(err)
            print('\nerror in autoscale function')


    # main (magnification calibration) function:
    def main(self):


        # will run in a separated thread (t1) so that it does not block nionswift
        # thread terminates explicitly on serial disconnect and on switching nionswift libraries:
        def thread_this(self):

            # a listener that listems for a text changing event and then executes the text setting function on the main thread (not on t1);
            # nionswift only allows the panel text to be set on the main thread: 
            listener = self.__trigger_text_change.text_change_event.listen(lambda: self.__api.queue_task(lambda: self.set_panel_text(self.__live_text)))
            
            library=self.__api.library                               # get active nionswift library

            # wait once until camera is set to play the first time; this prevents (loading) errors on nionswift startup:
            while (not self.__api.get_hardware_source_by_id(self.__hardware_source_id,'1').is_playing) and library == self.__api.library:
                pass
            
            #print('start LM auto calibration')                       # message for thread t1 is active          
            numbers=[1,2,3,4,5]                                      # int array of valued received numbers (sensors / reed switches)
            old_readint = -1                                         # initialize recieved number
            connected=self.__serialobject.openconnection()           # open serial connection; see: LMConnectionExtension() and LM_ArduinoSerial
            while connected and library == self.__api.library:       # read serial and set calibration as long as connected and the library does not change        
                readint = self.__serialobject.readbyte_request()     # read 1 byte (receive number) from serial and empty buffer
                time.sleep(0.2)                                      # wait; reading frequency is smaller than sendig frequency from the serial device 
                                                                     #    works by emptying the reading buffer every time
  
                # if statements to process received number (sensor / reed switch)
                #     set new magnification scale only when the recieved number changes
                #     set live text message in nionswift panel
                if readint != old_readint:
                    old_readint = readint
                    if readint in numbers:                                                                  # "normal" recieved number (sensor / reed switch)
                        self.autoscale(self.__magnifications[readint],self.__hardware_source_id)
                        self.__live_text=self.get_panel_text("objective: " + self.__magnifications[readint])
                    elif readint == 11:                                                                     # special error: 11 == no sensor detected: 
                        self.autoscale(self.__magnifications[0],self.__hardware_source_id)                  #    e.g.: sensor broken, cable detached,...
                        self.__live_text=self.get_panel_text("error: no objective detected")
                    elif readint == 12:                                                                     # special error: 12 == multiple sesnors: 
                        self.autoscale(self.__magnifications[0],self.__hardware_source_id)                  #    e.g.: sensor stuck, short circuit,...
                        self.__live_text=self.get_panel_text("error: multiple objectives detected")
                    elif readint == 21:                                                                     # special error: 21 == error in serial read function 
                        self.autoscale(self.__magnifications[0],self.__hardware_source_id)                  #    e.g.: no serial connection, input error,...
                        self.__live_text=self.get_panel_text("error when reading from serial")
                    else:                                                                                   # other errors
                        self.__live_text=self.get_panel_text("unknown read error")
                
                connected=self.__serialobject.connected()                                                   # check if still connected to serial device

            if not connected:
                self.__live_text=self.get_panel_text("no serial connection (USB port)")
                self.autoscale('not_scaled',self.__hardware_source_id)
            #print('end LM auto calibration')
            else:                                                                                            # message for thread t1 finished
                self.__serialobject.closeconnection()                                                       # close serial connection


        # initiate and start thread t1:
        self.__t1=threading.Thread(target=thread_this, args=[self])  # define the thread
        self.__t1.start()




# nionswift will notice this class because of the word "Extension" at the end of the class name
# it will execute __init__() at startup and close() when nionswift is closed
# nionswift will assert the correct API and UI (see api_broker and get_api(...) )
class LMConnectionExtension():

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.LM_auto_calibration.status_panel"

    def __init__(self, api_broker):

        # grab the api object.
        api = api_broker.get_api(version='~1.0', ui_version='~1.0')      
        # api can be used to access Nion Swift.


        self.__LMserial=LM_ArduinoSerial.LM_ArduinoSerial()                                             # initiate the class to read serial input; see: LM_ArduinoSerial
        self.__panel_ref = api.create_panel(LMConnectionDelegate(api,self.__LMserial)) # initiate the user panel defined in the class LMConnectionDelegate

    # this part will be run when nionswift gets closed
    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None
        self.__LMserial.closeconnection()                                              # close serial connection when nionswift is closing
