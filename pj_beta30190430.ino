

int sensorValue1 = 0;
int light_sensor = 1;
char rx_byte = 0;
int counter = 0;
bool PUMP_ON = false;
bool automode = true;
bool stat_light = false;
#include "DHT.h"
#define dhtPin 11      //讀取DHT11 Data
#define dhtType DHT11 //選用DHT11   
DHT dht(dhtPin, dhtType); // Initialize DHT sensor
void setup() {
    delay(3000);
    pinMode(8, OUTPUT);
    pinMode(10, OUTPUT);
    Serial.begin(9600);
    dht.begin();//啟動DHT
    digitalWrite(8,HIGH); // 直流水泵馬達關閉

}
void onLED() {
    digitalWrite(10, HIGH);
}

void offLED() {
    digitalWrite(10, LOW);
}

void led_switch(){
      if(stat_light) {
        offLED();    
      }else{
        onLED();
      }
    stat_light = !stat_light;
    Serial.print("LED: ");
    Serial.println(stat_light);
}


void readhumi() {
    sensorValue1 = analogRead(A0); // 讀取盆栽土壤水份數據
    Serial.println(sensorValue1);
}

void offpump() {
    PUMP_ON = false;
    digitalWrite(8, LOW); //直流水泵馬達關閉
}

void onpump() {
    PUMP_ON = true;
    //Serial.println(PUMP_ON,DEC);
    digitalWrite(8, HIGH); //直流水泵馬達開啟
}

void readlight(){
    int lightLevel = analogRead(light_sensor);
    float voltage = lightLevel; //* (5.0 / 1024.0);
    Serial.print("Light = ");
    Serial.println(voltage);
}

void pump_control(bool inBool) {
    if (PUMP_ON != inBool) {
        if(PUMP_ON == true) {
            offpump();
        } else {
            onpump();
        }
    }
}

void pump_switch(){
      if(PUMP_ON) {
        offpump();    
      }else{
        onpump();
      }
    Serial.print("PUMP: ");
    Serial.println(PUMP_ON);
}

void readdht(){
  float h = dht.readHumidity();//讀取濕度
  float t = dht.readTemperature();//讀取攝氏溫度
  float f = dht.readTemperature(true);//讀取華氏溫度
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("無法從DHT傳感器讀取！");
    return;
  }
  Serial.print("濕度: ");
  Serial.print(h);
  Serial.print("%\t");
  Serial.print("攝氏溫度: ");
  Serial.print(t);
  Serial.print("*C\t");
  Serial.print("華氏溫度: ");
  Serial.print(f);
  Serial.print("*F\n");
}

void automodectrl(){
      if(automode) {
        if(analogRead(0) > 800) // 判斷土壤濕度是否太乾
        {
            pump_control(true);
        }
        else {
            pump_control(false);
        }
    }
}
void loop() {

    if (Serial.available() > 0) {    // is a character available?
        rx_byte = Serial.read();       // get the character
        // check if a number was received
        if ((rx_byte >= '0') && (rx_byte <= '9')) {
            Serial.print("收到指令 : ");
            Serial.println(rx_byte);

            switch(rx_byte) {
            case '0':
                led_switch();
                break;
            case '1':
                pump_switch();
                break;
            case '2':
                automode = !automode;
                Serial.print("Automode: ");
                Serial.println(automode);               
                break;
             case '3':
                readlight();
                break;
             case '4':
                readdht();
                break;
            }
            //delay(500);
            rx_byte = 0;
        }

    } // end: if (Serial.available() > 0)

    Serial.print("Humi = ");
    readhumi();
      
    if (counter==30){
      readlight();

      readdht();
      counter = 0;
    }

    automodectrl();
    counter++;
    delay(1000); //等候1秒後再提取數據
}
