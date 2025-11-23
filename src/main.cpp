#include <iostream>
#include <chrono>
#include <thread>
#include "lidar.h"
#include "ObstacleDetector.h"
#include "controller.h"
#include "I2C.h"

int main() {
    Lidar lidar;
    ObstacleDetector detector;
    Controller controller;

    // Initialize RPLIDAR (USB serial is usually /dev/ttyUSB0)
    if (!lidar.init("/dev/ttyUSB0")) {
        std::cerr << "ERROR: Unable to init LIDAR.\n";
        return -1;
    }

    if (!lidar.start()) {
        std::cerr << "ERROR: Unable to start scanning.\n";
        return -1;
    }

    std::cout << "Lidar + I2C Controller running...\n";

    // Initialize I2C (Arduino address will be 0x08)
    I2C bus(0x08);
    if (!bus.init()) {
        std::cerr << "ERROR: Cannot init I2C bus.\n";
        return -1;
    }

    while (true) {
        std::vector<LidarPoint> points;

        if (lidar.grabScan(points)) {
            ObstacleInfo info = detector.analyze(points);
            std::string cmd = controller.decide(info);

            // Send a single-character command to Arduino
            bus.send(cmd[0]);

            // Optional minimal logging
            std::cout << "Sent: " << cmd[0]
                << " (F/R/L/S/B)\n";
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(60));
    }

    lidar.stop();
    return 0;
}
