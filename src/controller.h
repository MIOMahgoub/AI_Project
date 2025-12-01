#pragma once
#include "ObstacleDetector.h"
#include <string>

class Controller {
public:
    std::string decide(const ObstacleInfo& info);
};
