String serialReceived;
char commandChar;
String returnValue;

String anPins[] = {"0511.1","0522.2","0533.3","0544.4","0555.5","0566.6"};

void setup() {
    Serial.begin(9600);
    pinMode(A0,INPUT_PULLUP);
    pinMode(A1,INPUT_PULLUP);  
    pinMode(A2,INPUT_PULLUP);  
    pinMode(A3,INPUT_PULLUP);  
    pinMode(A4,INPUT_PULLUP);  
    pinMode(A5,INPUT_PULLUP);    
}


void loop() {

    if(Serial.available() > 0) {

      serialReceived = Serial.readStringUntil('\n');
      commandChar = serialReceived.charAt(0); //Switch only works with one char

      switch (commandChar) {
          case 'R':
            for(int i = 0; i<6; i++) {
              returnValue += "/";
              returnValue += anPins[i];
            }
            Serial.print(returnValue);
            break;
//          case '1':
//              returnValue = "TC1";
//              break;
//          case '2':
//              returnValue = "TC2";
//              break;
//          case '3':
//              returnValue = "TC3";
//              break;
//          case '4':
//              returnValue = "TC4";
//              break;
//          case '5':
//              returnValue = "TC5";
//              break;
//          case '6':
//              returnValue = "TC6";
//              break;
          default:
//              returnValue = "ERR";
            Serial.println("ERR");
      }

    //Send the return signal
//    if(returnValue != "") {
//      Serial.println(String("Reading: ") + returnValue);
//    }

  }
}
