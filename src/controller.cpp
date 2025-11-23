#include "Controller.h"

std::string Controller::decide(const ObstacleInfo& info) {

    if (info.frontBlocked) {
        // front blocked
        if (!info.leftBlocked)
            return "LEFT";        // turn left
        else if (!info.rightBlocked)
            return "RIGHT";       // turn right
        else
            return "STOP";        // trapped
    }

    // front is clear
    if (info.leftBlocked && !info.rightBlocked)
        return "RIGHT";           // avoid left side

    if (info.rightBlocked && !info.leftBlocked)
        return "LEFT";            // avoid right side

    return "FORWARD";             // path is clear
}
