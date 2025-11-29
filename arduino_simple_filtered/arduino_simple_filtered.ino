#include <Wire.h>

// Motor A Right wheel
const int IN1 = 7;
const int IN2 = 6;
// Motor B Left wheel
const int IN3 = 5;
const int IN4 = 4;

// Shared between ISR (receiveEvent) and loop()
volatile char lastCmd = 'S';
volatile bool newCmdAvailable = false;

void setup() {
  Serial.begin(9600);

  Wire.begin(0x08);          // I2C slave address
  Wire.onReceive(receiveEvent);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stop();

  Serial.println("Arduino I2C Slave Ready at 0x08");
  Serial.println("Waiting for commands: F=Forward, B=Backward, L=Left, R=Right, S=Stop");
}

// ⚠️ KEEP THIS SHORT – NO delay(), MINIMAL Serial
void receiveEvent(int numBytes) {
  while (Wire.available()) {
    char cmd = Wire.read();
    lastCmd = cmd;
    newCmdAvailable = true;
  }
}

void loop() {
  if (newCmdAvailable) {
    // Copy to local to avoid issues if it changes mid-use
    noInterrupts();
    char cmd = lastCmd;
    newCmdAvailable = false;
    interrupts();

    Serial.print("Received command: ");
    Serial.println(cmd);

    switch (cmd) {
      case 'F':
        Serial.println("→ Moving FORWARD");
        forward(1000);   // shorter duration is usually nicer
        break;

      case 'B':
        Serial.println("→ Moving BACKWARD");
        backward(1000);
        break;

      case 'L':
        Serial.println("→ Turning LEFT");
        left(1000);
        break;

      case 'R':
        Serial.println("→ Turning RIGHT");
        right(1000);
        break;

      case 'S':
        Serial.println("→ STOPPING");
        stop();
        break;

      default:
        Serial.print("→ Unknown command: ");
        Serial.println(cmd);
        stop();
        break;
    }
  }

  // You can add other robot logic here later if needed
}

// === MOTOR FUNCTIONS ===

void forward(int delayspeed) {
  // A: forward, B: forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  delay(delayspeed);
  stop();
}

void backward(int delayspeed) {
  // A: backward, B: backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  delay(delayspeed);
  stop();
}

void right(int delayspeed) {
  // spin right: A forward, B backward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  delay(delayspeed);
  stop();
}

void left(int delayspeed) {
  // spin left: A backward, B forward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  delay(delayspeed);
  stop();
}

void stop() {
  // For most H-bridge drivers, HIGH/HIGH = brake, LOW/LOW = coast
  // If this doesn't behave as expected, try LOW/LOW instead.
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

