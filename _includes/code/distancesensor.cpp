#include "Distance_Sensor.h"
#include "Arduino.h"

// Sets the pins of the distance sensor
Distance_Sensor::Distance_Sensor(int dPin, int bPin){
    this->distancePin = dPin;
    this->backgroundPin = bPin;
}

// destructor
Distance_Sensor::~Distance_Sensor() {}

// Initializes the distance sensor buffer
void Distance_Sensor::initialize() {
  for(int i = 0; i < FILTER_LENGTH; i++){
    this->buffer[i] = ((analogRead(this->distancePin) - analogRead(this->backgroundPin)) * 5.0 / 1023.0);
    delay(10);
  }
}

// Gets a voltage differential from the distance sensor
// Higher Value = Closer to object
float Distance_Sensor::poll(){
  float total_reading = buffer[FILTER_LENGTH - 1];

  for(int i = FILTER_LENGTH - 2; i >= 0; i--){
    total_reading += buffer[i];
    buffer[i + 1] = buffer[i];
  }

  buffer[0] = ((analogRead(this->backgroundPin) - analogRead(distancePin)) * 5.0 / 1023.0);
  total_reading += buffer[0];

  return total_reading / FILTER_LENGTH;
}

float Distance_Sensor::pollD(){
  return analogRead(this->distancePin) * 5.0 / 1023.0;
}

float Distance_Sensor::pollB(){
  return analogRead(this->backgroundPin) * 5.0 / 1023.0;
}