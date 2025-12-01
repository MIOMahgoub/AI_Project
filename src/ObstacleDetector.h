#pragma once
#include <vector>
#include "lidar.h"

struct ObstacleInfo {
    bool frontBlocked;
    bool leftBlocked;
    bool rightBlocked;
    float nearestFrontDist;
    float nearestLeftDist;
    float nearestRightDist;
};

class ObstacleDetector {
public:
    // distance thresholds in millimeters
    float frontThreshold = 500.0f;   // 50 cm
    float sideThreshold = 400.0f;   // 40 cm

    ObstacleInfo analyze(const std::vector<LidarPoint>& points);
};
