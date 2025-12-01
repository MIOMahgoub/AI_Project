#pragma once
#include <string>

class I2C {
public:
    I2C(int address);
    bool init(const std::string& device = "/dev/i2c-1");
    bool send(char cmd);

private:
    int fd;
    int addr;
};
