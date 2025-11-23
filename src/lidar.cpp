#include "lidar.h"
#include <iostream>

using namespace sl;

Lidar::Lidar() {
    driver = nullptr;
    channel = nullptr;
    isRunning = false;
}

Lidar::~Lidar() {
    stop();
    if (driver) {
        delete driver;
        driver = nullptr;
    }
}

bool Lidar::init(const std::string& port, int baudrate) {
    std::cout << "Initializing RPLIDAR on port " << port << "...\n";

    driver = *createLidarDriver();
    if (!driver) {
        std::cerr << "Failed to create driver.\n";
        return false;
    }

    channel = *createSerialPortChannel(port.c_str(), baudrate);
    sl_result ans = driver->connect(channel);

    if (!SL_IS_OK(ans)) {
        std::cerr << "Failed to connect to LIDAR.\n";
        return false;
    }

    // Device info
    sl_lidar_response_device_info_t info;
    ans = driver->getDeviceInfo(info);
    if (!SL_IS_OK(ans)) {
        std::cerr << "Failed to get device info.\n";
        return false;
    }

    std::cout << "LIDAR connected.\n";
    std::cout << "Firmware: " << (info.firmware_version >> 8) << "."
        << (info.firmware_version & 0xFF) << "\n";

    return true;
}

bool Lidar::start() {
    if (!driver) return false;

    // Start motor
    sl_result m = driver->setMotorSpeed();
    if (!SL_IS_OK(m)) {
        std::cerr << "Failed to start motor.\n";
        return false;
    }

    std::cout << "Motor started.\n";

    // Start scanning
    sl_result s = driver->startScan(0, 1);
    if (!SL_IS_OK(s)) {
        std::cerr << "Failed to start scan.\n";
        return false;
    }

    std::cout << "Scanning started.\n";
    isRunning = true;
    return true;
}

bool Lidar::grabScan(std::vector<LidarPoint>& points) {
    if (!isRunning) return false;

    sl_lidar_response_measurement_node_hq_t nodes[8192];
    size_t count = sizeof(nodes) / sizeof(nodes[0]);

    sl_result ans = driver->grabScanDataHq(nodes, count);
    if (!SL_IS_OK(ans)) return false;

    driver->ascendScanData(nodes, count);

    points.clear();
    points.reserve(count);

    for (size_t i = 0; i < count; i++) {
        LidarPoint p;
        p.angle_deg = (nodes[i].angle_z_q14 * 90.f) / 16384.f;
        p.dist_mm = nodes[i].dist_mm_q2 / 4.0f;
        p.quality = nodes[i].quality >> SL_LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT;

        points.push_back(p);
    }

    return true;
}

void Lidar::stop() {
    if (driver) {
        driver->stop();
        driver->setMotorSpeed(0);
        isRunning = false;
    }
}
