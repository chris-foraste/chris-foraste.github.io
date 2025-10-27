/// @brief This class defines the algorithms to read the distance sensor.

#ifndef Distance_Sensor_H
#define Distance_Sensor_H

class Distance_Sensor {
    private:
        int distancePin;
        int backgroundPin;
        const static int FILTER_LENGTH = 5;
        float buffer[FILTER_LENGTH];

    public:
        Distance_Sensor::Distance_Sensor(int dPin, int bPin); // Set pins
        ~Distance_Sensor(); // Destructor
        void initialize(); // Initialize buffer

        float poll(); // Get reading - actual use
        float pollD(); // For Testing
        float pollB(); // For Testing
};

#endif
