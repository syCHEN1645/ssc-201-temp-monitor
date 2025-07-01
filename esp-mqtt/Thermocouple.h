#ifndef THERMOCOUPLE_H
#define THERMOCOUPLE_H

#include <OneWire.h>
#include <DallasTemperature.h>

class Thermocouple {
public:
  String sensorName;
  Thermocouple(String name);
  ~Thermocouple();
  void setupSensor(int pin);
  float getTemperature(int index=0);

private:
  OneWire* oneWire;
	DallasTemperature* sensor;
};

#endif