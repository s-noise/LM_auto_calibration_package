//////////////////////////////////////////////////////////////////////////////////////////////////
// LMikro_Arduino_1.ino
// does: read 5 sensors on digital Pins (2-6) with pull up resistors (> 20kOhm) activated, 
//       other part of the connections go to ground;
//       selects one sensor per time that is active, sends error codes as integer if more / no sensor is active;
//       selected sensor number (as intereger) is smoothed over time (loop-round):
//       signal (integer) must be constant for 3 seconds (default) to be selected for sending,
//       sends previous signal otherwise;
//       sends the integer value via serial connection (virtual com port over USB) as 1 byte per time (loop-round);
//
// authors: Tobias Mittelbauer, Simon Schafler, Stefan Manuel Noisternig

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);       // set internal LED (digital Pin 13)

// set internal pull up resistors (>20 kOhm) for digital Pins 2-6:
// these are the Pins for sensor read out
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  
  Serial.begin(9600);                 // connect serial bautrate = 9600

}

//////////////////////////////////////////////////////////////////////////////////////////////////
// initialize variables:

////////////////////////////////////////
int Pins[]= {2, 3, 4, 5, 6};          //   define Pins for sensor read out
////////////////////////////////////////

////////////////////////////////////              
int intervall = 3000;             //    time interval for smoothing algorithm (time of constant signal) in msec,
////////////////////////////////////    default value 3000 msec, can be adjusted

unsigned long previousmillis = 0;     // Arduino time (mills()) since start of program is passed to this variable, must be unsigned long

// variables for sensor signals
int oldvalue = -1;                    // compare value (stored)       
int newvalue = -1;                    // actual value (measured)
int storedvalue = 11;                 // send value (send per serial)

int lowcount = 0;                     // dummy count variable for smoothing algorithm
int led = 1;                          // variable for switching internal LED on / off: led = 1 or -1 (see: function ledblink()) 
//int incomingByte = 0;               // for incoming serial data


//////////////////////////////////////////////////////////////////////////////////////////////////
// define functions:

// function to check (read) the state of the sensors and set sensor variable
//     sensor variable (newvalue): "normal" behaviour: 1-5, "no sensor active" error: 11, "multiple senor active" error: 12 
void pincheck(){
  lowcount = 0;
  newvalue = 11;
    for(int i=0;i<5;i++){
     if(digitalRead(Pins[i]) == LOW){
    lowcount = lowcount + 1;
    newvalue = i+1 ;
     }
    }
 if(lowcount > 1){
  newvalue = 12;
  
 }
}

// function to set the internal LED, change LED state (on/off) with every call
void ledblink(){
      if (led==1){
      digitalWrite(LED_BUILTIN, LOW);
    }
    else {
      digitalWrite(LED_BUILTIN, HIGH);
    }
    led=led*(-1);
}


///////////////////////////////////////////////////////////////////////////////////////////////////
// main loop

void loop() {

pincheck();

// smoothing algorithm: send signal continuously to serial, but only send signal that is stable for "interval" time
if(oldvalue == newvalue){
  if(millis() - previousmillis > intervall){     // this condition works even after overflow, when mills() exceeds 
                                                 //     the unsigned long range (after ~ 50 days) and starts from zero
    storedvalue = oldvalue;   
    previousmillis = millis();
    ledblink();
  }
}
else{
  oldvalue = newvalue;
  previousmillis = millis();
}


//if (Serial.available() > 0) {                              // part for getting send request first
//    incomingByte = Serial.read();
    Serial.write(storedvalue);                               // sends the integer "storedvalue" as 1 byte
    Serial.flush();                                          // waits till data is send
//}

delay(100);                                     // loop execution needs 102 - 110 ms now (10 ms else), this value is correlated
                                                //     with the serial read program (LM_auto_calibration.py) in python

}
