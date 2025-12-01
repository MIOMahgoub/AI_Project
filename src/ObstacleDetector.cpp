#include "ObstacleDetector.h"
#include <cmath>
#include <limits>

ObstacleInfo ObstacleDetector::analyze(const std::vector<LidarPoint>& points) {
    ObstacleInfo info;
    info.frontBlocked = false;
    info.leftBlocked = false;
    info.rightBlocked = false;

    info.nearestFrontDist = std::numeric_limits<float>::max();
    info.nearestLeftDist = std::numeric_limits<float>::max();
    info.nearestRightDist = std::numeric_limits<float>::max();

    for (const auto& p : points) {
        float angle = p.angle_deg;
        float dist = p.dist_mm;

        if (dist <= 0) continue;  // invalid reading

        // Normalize angle to 0–360
        while (angle < 0) angle += 360;
        while (angle >= 360) angle -= 360;

        // FRONT: 350–360 and 0–10 degrees
        if (angle <= 10 || angle >= 350) {
            if (dist < info.nearestFrontDist)
                info.nearestFrontDist = dist;
        }

        // LEFT: 80–100 degrees
        if (angle >= 80 && angle <= 100) {
            if (dist < info.nearestLeftDist)
                info.nearestLeftDist = dist;
        }

        // RIGHT: 260–280 degrees
        if (angle >= 260 && angle <= 280) {
            if (dist < info.nearestRightDist)
                info.nearestRightDist = dist;
        }
    }

    info.frontBlocked = (info.nearestFrontDist < frontThreshold);
    info.leftBlocked = (info.nearestLeftDist < sideThreshold);
    info.rightBlocked = (info.nearestRightDist < sideThreshold);

    return info;
}
