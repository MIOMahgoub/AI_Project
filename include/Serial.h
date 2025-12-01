#pragma once
#include <string>

class Serial {
public:
    Serial();
    bool init(const std::string& device = "/dev/ttyUSB1", int baud = 9600);
    bool send(char cmd);
    void close();
    
private:
    int fd;
};
