
//define analog pins for code clarity
#define TC1 A5
#define TC2 A4
#define TC3 A3
#define TC4 A2
#define TC5 A1
#define TC6 A0

int r1[] = {0,0,0,0,0,0};
int tcList[] = {TC1,TC2,TC3,TC4,TC5,TC6};
int sample = 25
String printString = "";
  
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  //setup the pins to default high
  pinMode(TC1, INPUT_PULLUP);
  pinMode(TC2, INPUT_PULLUP);
  pinMode(TC3, INPUT_PULLUP);
  pinMode(TC4, INPUT_PULLUP);
  pinMode(TC5, INPUT_PULLUP);
  pinMode(TC6, INPUT_PULLUP);

 //for monitoring the inputs
 Serial.begin(9600);

 //thermocouple voltage is very low, reference will be about 100mV
 analogReference(EXTERNAL);
}


void loop() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)

  //Loop through each thermocouple
  for(int i=0; i<6; i++) {
    r1[i] = 0 //reset reading

    //Sample input to average
    for(int j=0;j<sample;j++) {
      r1[i] += analogRead(tcList[i]);
      delay(50);
    }
    
    r1[i] /= sample; //average reading
    printString = String("TC") + (i+1) + ": " + r1[i];
    Serial.println(printString); //print reading
  }
  Serial.println("=================================");
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(2000);                       // wait for a second
}




/*~~~~~REFERENCES~~~~~
 * https://pythonforundergradengineers.com/python-arduino-potentiometer.html
 * https://www.arduino.cc/en/Reference/AnalogReference&
 * https://www.pyromation.com/downloads/data/emfk_f.pdf
 * 
 * /
 */
