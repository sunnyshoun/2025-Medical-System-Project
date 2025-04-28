#include <AccelStepper.h>
#include <SoftwareSerial.h>

#define MotorInterfaceType 4
#define RX_PIN 6
#define TX_PIN 7

AccelStepper stepperLeft(MotorInterfaceType, 2, 4, 3, 5);
AccelStepper stepperRight(MotorInterfaceType, 8, 10, 9, 11);
SoftwareSerial rpiSerial(RX_PIN, TX_PIN);

const float MAX_SPEED = 700.0;
const float ACCELERATION = 450.0;
const float WHEEL_CIRCUMFERENCE = 205.0;

typedef struct MoveData{
  bool check;
  bool direction;
  int distance_mm;
} MoveData;

void moveDistance(bool direction, int distance_mm) {
  float stepsPerMM = 2038.0 / WHEEL_CIRCUMFERENCE;
  long stepsToMove = round(distance_mm * stepsPerMM);

  stepsToMove *= direction ? 1 : -1;
  stepperLeft.move(stepsToMove);
  stepperRight.move(-stepsToMove);
  while (stepperLeft.distanceToGo() != 0 || stepperRight.distanceToGo() != 0) {
    stepperLeft.run();
    stepperRight.run();
  }
}

char readCharWithTimeout(uint64_t timeout = 100){
  uint64_t startTime = millis();
  while (millis() - startTime < timeout) {
    if (rpiSerial.available()) {
      return rpiSerial.read();;
    }
  }
  return '\0';
}

MoveData readMoveData() {
  char c;
  MoveData moveData = {false, false, 0};
  
  if (readCharWithTimeout() != 'm') { //check start with 'm'
    return moveData;
  }

  c = readCharWithTimeout();
  if(c == '0' || c == '1'){
    moveData.direction = (c == '1');
  }
  else{
    return moveData;
  }

  if (readCharWithTimeout() != ',') { //check ','
    return moveData;
  }

  String distanceStr = "";
  while ((c = readCharWithTimeout()) != '\n' && c != '\0') {
    if(c < '0' || c > '9') return moveData;
    distanceStr += c;
  }

  moveData.distance_mm = distanceStr.toInt();
  moveData.check = true;
  return moveData;
}

void setup() {
  stepperLeft.setMaxSpeed(MAX_SPEED);
  stepperLeft.setAcceleration(ACCELERATION);
  stepperRight.setMaxSpeed(MAX_SPEED);
  stepperRight.setAcceleration(ACCELERATION);

  rpiSerial.begin(9600);
}

void loop() {
  if (rpiSerial.available()) {
    MoveData moveData = readMoveData();
    if(moveData.check){
      rpiSerial.println("ok");
      moveDistance(moveData.direction, moveData.distance_mm);
      rpiSerial.println("done");
    }
    else{
      rpiSerial.println("error");
    }
  }
}