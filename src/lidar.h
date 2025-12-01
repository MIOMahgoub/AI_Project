#ifndef LIDAR_H
#define LIDAR_H

#include <vector>
#include <string>
#include "sl_lidar.h"
#include "sl_lidar_driver.h"

struct LidarPoint {
    float angle_deg;
    float dist_mm;
    int quality;
};

class Lidar {
public:
    Lidar();
    ~Lidar();

    bool init(const std::string& port, int baudrate = 115200);
    bool start();
    bool grabScan(std::vector<LidarPoint>& points);
    void stop();

private:
    sl::ILidarDriver* driver;
    sl::IChannel* channel;
    bool isRunning;
};

#endif
