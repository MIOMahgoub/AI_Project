#include "I2C.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <iostream>

I2C::I2C(int address) : addr(address), fd(-1) {}

bool I2C::init(const std::string& device) {
    fd = open(device.c_str(), O_RDWR);
    if (fd < 0) {
        std::cerr << "I2C: Cannot open " << device << "\n";
        return false;
    }

    if (ioctl(fd, I2C_SLAVE, addr) < 0) {
        std::cerr << "I2C: Failed to set slave address\n";
        return false;
    }

    return true;
}

bool I2C::send(char cmd) {
    if (fd < 0) return false;

    if (write(fd, &cmd, 1) != 1) {
        std::cerr << "I2C write failed\n";
        return false;
    }
    return true;
}
