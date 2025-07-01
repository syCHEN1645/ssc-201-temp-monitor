#include "Thermocouple.h"
#include <Arduino.h>

Thermocouple::Thermocouple(String name): oneWire(nullptr), sensor(nullptr) {
	sensorName = name;
}

Thermocouple::~Thermocouple() {
	delete oneWire;
	delete sensor;
}

void Thermocouple::setupSensor(int pin) {
	oneWire = new OneWire(pin);
	sensor = new DallasTemperature(oneWire);
	sensor->begin();
}

float Thermocouple::getTemperature(int index) {
	// assume that there is only 1 sensor connected to wire
	if (!sensor) {
		Serial.println("sensor is not connected");
		return -127.0;
	}
	sensor->requestTemperatures();
	Serial.println("sensor request temperature");
	return sensor->getTempCByIndex(index);
}