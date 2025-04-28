#include <SoftwareSerial.h>

#define RX_PIN 6
#define TX_PIN 7

SoftwareSerial mySerial(RX_PIN, TX_PIN);

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
}

void loop() {
  // 如果 Serial 有資料，轉發到 mySerial
  if (Serial.available()) {
    char c = Serial.read();
    mySerial.write(c);
  }

  // 如果 mySerial 有資料，轉發到 Serial
  if (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c);
  }
}
