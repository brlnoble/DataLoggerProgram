#include "max6675.h" // max6675.h file is part of the library that you should download from Robojax.com

int soPin1 = 6;// SO = Serial Out for 1
int soPin2 = 7;// SO = Serial Out for 1
int soPin3 = 8;// SO = Serial Out for 1
int soPin4 = 9;// SO = Serial Out for 1
int soPin5 = 10;// SO = Serial Out for 1
int soPin6 = 11;// SO = Serial Out for 1

int csPin123 = 2;// CS = chip select CS pin for 1 2 3
int ckPin123 = 3;// SCK = Serial Clock pin for 1 2 3

int csPin456 = 4;// CS = chip select CS pin for 4 5 6
int ckPin456 = 5;// SCK = Serial Clock pin for 4 5 6

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
