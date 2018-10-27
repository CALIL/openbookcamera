/**
  BOOK-COVER-SCANNER phy-modu]le

  Copyright (c) 2018 Ryuuji Yoshimoto

  This software is released under the MIT License.
  http://opensource.org/licenses/mit-license.php
*/

#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

const int SENSOR_ACTIVE_PIN = 7;
const int SENSOR_IN_PIN = 8;
const int SPEAKER_PIN = 12;
const int LED1PIN = 9;
const int LED2PIN = 10;
const int LED3PIN = 5;

int mm = 0;
int inByte = 0;
int currentStatus = 0;
int newStatus = 0;
int eventStatus = -1;
unsigned long eventStarted = 0;
unsigned long ignoreMillis = 0;

void setup() {
  pinMode(SPEAKER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED1PIN, OUTPUT);
  pinMode(LED2PIN, OUTPUT);
  pinMode(LED3PIN, OUTPUT);
  pinMode(SENSOR_ACTIVE_PIN, OUTPUT);
  pinMode(SENSOR_IN_PIN, INPUT_PULLUP);
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(LED1PIN, LOW);
  digitalWrite(LED2PIN, LOW);
  digitalWrite(LED3PIN, LOW);
  digitalWrite(SENSOR_ACTIVE_PIN, LOW);
  Serial.begin(115200);
  Wire.begin();
  sensor.init();
  sensor.setTimeout(500);
  sensor.setMeasurementTimingBudget(200000);
  sensor.setSignalRateLimit(0.1);
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodPreRange, 18);
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodFinalRange, 14);
  while (!Serial) {
    ;
  }
}

void ranging() {
  mm = 384 - sensor.readRangeSingleMillimeters();
  if (mm < 0) {
    mm = 0;
  }
  if (sensor.timeoutOccurred()) {
    Serial.print("HEIGHT:TIMEOUT");
  } else {
    Serial.print("HEIGHT:");
    Serial.print(mm);
  }
  Serial.println();
}

void loop() {
  if (Serial.available() > 0) {
    inByte = Serial.read();
    if (inByte == '1') {
      tone(SPEAKER_PIN, 500, 20);
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(LED1PIN, LOW);
      digitalWrite(LED2PIN, HIGH);
      digitalWrite(LED3PIN, LOW);
      digitalWrite(SENSOR_ACTIVE_PIN, LOW);
    }
    if (inByte == '2') {
      tone(SPEAKER_PIN, 600, 130);
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(LED1PIN, HIGH);
      digitalWrite(LED2PIN, LOW);
      digitalWrite(LED3PIN, LOW);
      digitalWrite(SENSOR_ACTIVE_PIN, LOW);
    }
    if (inByte == '3') {
      //tone(SPEAKER_PIN, 600, 130);
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(LED1PIN, HIGH);
      digitalWrite(LED2PIN, HIGH);
      digitalWrite(LED3PIN, HIGH);
      digitalWrite(SENSOR_ACTIVE_PIN, HIGH);
      ignoreMillis = millis();
    }
    if (inByte == '4') {
      tone(SPEAKER_PIN, 300, 100);
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite( LED1PIN, HIGH);
      digitalWrite( LED2PIN, HIGH);
      digitalWrite( LED3PIN, HIGH);
      digitalWrite(SENSOR_ACTIVE_PIN, LOW);
      ranging();
    }
    if (inByte == '0') {
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(LED1PIN, LOW);
      digitalWrite(LED2PIN, LOW);
      digitalWrite(LED3PIN, LOW);
      digitalWrite(SENSOR_ACTIVE_PIN, LOW);
    }
    Serial.println("ACK");
  }
  if (bitRead(PORTD, SENSOR_ACTIVE_PIN) == 1) {
    newStatus = digitalRead(SENSOR_IN_PIN);
    if (currentStatus != newStatus) {
      if (eventStatus == -1 || eventStatus != newStatus) {
        if (newStatus == 0) {
          tone(SPEAKER_PIN, 400, 20);
        }
        eventStatus = newStatus;
        eventStarted = millis();
      } else {
        if (eventStatus == 1 && newStatus == 1) {
          if (millis() - eventStarted > 300) {
            currentStatus = 1;
            eventStatus = -1;
            if (millis() - ignoreMillis > 500) {
              Serial.println("LEAVE");
            } else {
              Serial.println("SKIP");
            }
          }
        } else if (eventStatus == 0 && newStatus == 0) {
          if (millis() - eventStarted > 1500) {
            currentStatus = 0;
            eventStatus = -1;
            if (millis() - ignoreMillis > 2000) {
              Serial.println("ON");
            } else {
              Serial.println("SKIP");
            }
          }
        }
      }
    } else {
      eventStatus = -1;
    }
  }
}
