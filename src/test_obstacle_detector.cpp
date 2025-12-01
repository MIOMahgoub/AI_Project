#include <iostream>
#include <vector>
#include "ObstacleDetector.h"
#include "lidar.h"   // for LidarPoint struct

int main() {
    ObstacleDetector detector;

    // Simulated LIDAR data ------------------------------
    std::vector<LidarPoint> points;

    // Simulate a clear front, blocked left, clear right
    for (int i = 0; i < 360; i++) {
        LidarPoint p;
        p.angle_deg = i;
        p.quality = 47;

        if (i > 300 || i < 60)         // front region
            p.dist_mm = 1500;          // clear
        else if (i > 60 && i < 120)    // left region
            p.dist_mm = 200;           // obstacle very close
        else                           // right region
            p.dist_mm = 1500;          // clear

        points.push_back(p);
    }

    // Run test
    ObstacleInfo info = detector.analyze(points);

    std::cout << "Front Blocked: " << info.frontBlocked
        << "  Dist: " << info.nearestFrontDist << " mm\n";
    std::cout << "Left Blocked:  " << info.leftBlocked
        << "  Dist: " << info.nearestLeftDist << " mm\n";
    std::cout << "Right Blocked: " << info.rightBlocked
        << "  Dist: " << info.nearestRightDist << " mm\n";

    return 0;
}
