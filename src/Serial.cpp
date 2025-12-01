#include "Serial.h"
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <iostream>

Serial::Serial() : fd(-1) {}

bool Serial::init(const std::string& device, int baud) {
    fd = open(device.c_str(), O_RDWR | O_NOCTTY);
    if (fd < 0) {
        std::cerr << "Serial: Cannot open " << device << "\n";
        return false;
    }
    
    struct termios options;
    tcgetattr(fd, &options);
    
    // Set baud rate
    speed_t baudRate = B9600;
    if (baud == 115200) baudRate = B115200;
    else if (baud == 57600) baudRate = B57600;
    else if (baud == 38400) baudRate = B38400;
    else if (baud == 19200) baudRate = B19200;
    
    cfsetispeed(&options, baudRate);
    cfsetospeed(&options, baudRate);
    
    // 8N1 mode
    options.c_cflag &= ~PARENB;  // No parity
    options.c_cflag &= ~CSTOPB;  // 1 stop bit
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;      // 8 data bits
    options.c_cflag |= CREAD | CLOCAL;
    
    // Raw mode
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY);
    options.c_oflag &= ~OPOST;
    
    tcsetattr(fd, TCSANOW, &options);
    
    std::cout << "Serial port " << device << " opened at " << baud << " baud\n";
    return true;
}

bool Serial::send(char cmd) {
    if (fd < 0) {
        std::cerr << "Serial write failed: port not open\n";
        return false;
    }
    
    if (write(fd, &cmd, 1) != 1) {
        std::cerr << "Serial write failed\n";
        return false;
    }
    return true;
}

void Serial::close() {
    if (fd >= 0) {
        ::close(fd);
        fd = -1;
    }
}
