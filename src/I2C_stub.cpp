#include "I2C.h"
#include <iostream>

// Constructor (Windows stub)
I2C::I2C(int address)
    : fd(-1), addr(address)   // match header variable names EXACTLY
{
    std::cout << "[I2C Stub] Created for address 0x"
        << std::hex << addr << std::dec << "\n";
}

// Init stub (Windows)
bool I2C::init(const std::string& device)
{
    std::cout << "[I2C Stub] init() called. Device = " << device
        << " (Ignored on Windows)\n";

    fd = 1; // mark as 'initialized'
    return true;
}

// Send stub (Windows)
bool I2C::send(char cmd)
{
    if (fd < 0) {
        std::cout << "[I2C Stub] ERROR: init() was not called!\n";
        return false;
    }

    std::cout << "[I2C Stub] Would send command: '"
        << cmd << "' (ASCII " << int(cmd) << ")\n";

    return true;
}
