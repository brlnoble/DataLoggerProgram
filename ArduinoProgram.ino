#include "max6675.h" // max6675.h file is part of the library that you should download from Robojax.com

int soPin1 = 2;// SO = Serial Out for 1
int soPin2 = 3;// SO = Serial Out for 2
int soPin3 = 4;// SO = Serial Out for 3
int soPin4 = 10;// SO = Serial Out for 4
int soPin5 = 11;// SO = Serial Out for 5
int soPin6 = 12;// SO = Serial Out for 6

int csPin123 = 5;// CS = chip select CS pin for 1 2 3
int ckPin123 = 6;// SCK = Serial Clock pin for 1 2 3

int csPin456 = 8;// CS = chip select CS pin for 4 5 6
int ckPin456 = 9;// SCK = Serial Clock pin for 4 5 6

//Create pin sensors
MAX6675 TC1(ckPin123, csPin123, soPin1);
MAX6675 TC2(ckPin123, csPin123, soPin2);
MAX6675 TC3(ckPin123, csPin123, soPin3);
MAX6675 TC4(ckPin456, csPin456, soPin4);
MAX6675 TC5(ckPin456, csPin456, soPin5);
MAX6675 TC6(ckPin456, csPin456, soPin6);

double corr = 00.0; //Correction value

String serialReceived;
char commandChar;
String returnValue;

String anPins[] = {"0511.1","0522.2","0533.3","0544.4","0555.5","0566.6"};


void setup() {

          
  Serial.begin(9600);// initialize serial monitor with 9600 baud

}

void loop() {
  //If serial from computer is open
  if(Serial.available() > 0) {

      serialReceived = Serial.readStringUntil('\n');
      commandChar = serialReceived.charAt(0); //Switch only works with one char

      switch (commandChar) {
          case 'R':

            anPins[0] = String(TC1.readFahrenheit());
            anPins[1] = String(TC2.readFahrenheit());
            anPins[2] = String(TC3.readFahrenheit());
            anPins[3] = String(TC4.readFahrenheit());
            anPins[4] = String(TC5.readFahrenheit());
            anPins[5] = String(TC6.readFahrenheit());
            
            for(int i = 0; i<6; i++) {
              returnValue += "/";
              if (anPins[i] = "NaN")
              {
                returnValue += "000.0";
              }
              else {
                returnValue += anPins[i];
              }
              
            }
            Serial.print(returnValue);
            break;

          default:
            Serial.println("ERR");
      }
  }
  
//   Serial.print("TC1: F = "); 
//   Serial.println(corr + TC1.readFahrenheit());
//   Serial.print("TC2: F = "); 
//   Serial.println(corr + TC2.readFahrenheit());
//   Serial.print("TC3: F = "); 
//   Serial.println(corr + TC3.readFahrenheit());
//   Serial.print("TC4: F = "); 
//   Serial.println(corr + TC4.readFahrenheit());
//   Serial.print("TC5: F = "); 
//   Serial.println(corr + TC5.readFahrenheit());
//   Serial.print("TC6: F = "); 
//   Serial.println(corr + TC6.readFahrenheit());


//   Serial.println("###########################################");
   
//   delay(1000);
}

// https://electropeak.com/learn/interfacing-max6675-k-type-thermocouple-module-with-arduino/
