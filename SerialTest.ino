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

void setup() {

          
  Serial.begin(9600);// initialize serial monitor with 9600 baud

}

void loop() {
  // basic readout test, just print the current temp
  
   Serial.print("TC1: F = "); 
   Serial.println(corr + TC1.readFahrenheit());
   Serial.print("TC2: F = "); 
   Serial.println(corr + TC2.readFahrenheit());
   Serial.print("TC3: F = "); 
   Serial.println(corr + TC3.readFahrenheit());
   Serial.print("TC4: F = "); 
   Serial.println(corr + TC4.readFahrenheit());
   Serial.print("TC5: F = "); 
   Serial.println(corr + TC5.readFahrenheit());
   Serial.print("TC6: F = "); 
   Serial.println(corr + TC6.readFahrenheit());


   Serial.println("###########################################");
   
   delay(1000);
}

// https://electropeak.com/learn/interfacing-max6675-k-type-thermocouple-module-with-arduino/



//
//String serialReceived;
//char commandChar;
//String returnValue;
//
//String anPins[] = {"0511.1","0522.2","0533.3","0544.4","0555.5","0566.6"};
//
//void setup() {
//    Serial.begin(9600);
//    pinMode(A0,INPUT_PULLUP);
//    pinMode(A1,INPUT_PULLUP);  
//    pinMode(A2,INPUT_PULLUP);  
//    pinMode(A3,INPUT_PULLUP);  
//    pinMode(A4,INPUT_PULLUP);  
//    pinMode(A5,INPUT_PULLUP);    
//}
//
//
//void loop() {
//
//    if(Serial.available() > 0) {
//
//      serialReceived = Serial.readStringUntil('\n');
//      commandChar = serialReceived.charAt(0); //Switch only works with one char
//
//      switch (commandChar) {
//          case 'R':
//            for(int i = 0; i<6; i++) {
//              returnValue += "/";
//              returnValue += anPins[i];
//            }
//            Serial.print(returnValue);
//            break;
////          case '1':
////              returnValue = "TC1";
////              break;
////          case '2':
////              returnValue = "TC2";
////              break;
////          case '3':
////              returnValue = "TC3";
////              break;
////          case '4':
////              returnValue = "TC4";
////              break;
////          case '5':
////              returnValue = "TC5";
////              break;
////          case '6':
////              returnValue = "TC6";
////              break;
//          default:
////              returnValue = "ERR";
//            Serial.println("ERR");
//      }
//
//    //Send the return signal
////    if(returnValue != "") {
////      Serial.println(String("Reading: ") + returnValue);
////    }
//
//  }
//}
