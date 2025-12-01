
 ![IMG_3044](https://github.com/user-attachments/assets/6e15b28c-9418-4c8f-82c2-ccc5eabb7464)

 # Hand Control “HC” Car

 This is the Repository for Group 21. Our Group consists of: 

- Gabriel Villanueva
- Ivebens Eliacin
- Jose Caraballo
- Jose Olascoaga
- Muhammad Mahgoub

## Project Overview: 
  The overall objective of our project was to create a robotic car that was entirely controlled by the user's hands. This was completely done by using 
  a pre-trained dataset found in the GitHub repo named ![hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe). With this repo, we
  use a Raspberry Pi 5 that was able to run the model, detect the user's hand gestures, and send commands over to the robotic car that had a Raspberry Pi Zero 2W. The Pi Zero would 
  then send movement commands based on the information that was collected from the lidar. If the lidar detected a blocked path that was being gestured to, the gesture command is 
  overridden with a stop command. The Arduino Uno is communicated these commands via I2C and drives the motors.
  
<img width="703" height="595" alt="Hand-Control System" src="https://github.com/user-attachments/assets/d9f18dfc-82c6-41c1-9156-7611b4ea8557" />

## Hardware
 - RaspberryPi Zero 2W
 - Slamtec RPLidar A1M8
 - RaspberryPi 5
 - Arduino Uno
 - Logitech C92S Pro Camera
 - Custom Robot Car

## Setup
 - The files in the arduino_simple_filtered folder are utilized with the Arduino Uno on the robot
 - The files in the hand-gesture-recognition-mediapipe folder are utilized with the RaspberryPi 5 based station and Logitech C92S Pro Camera Setup
 - The files in the src folder work with the include, lib/rplidar_sdk, and out folders to be implemented into the RaspberryPi Zero 2W on the robot
 -- The src folder files need to be build the process robot_lidar utilizing CMake from the CMakeLists.txt file

## Dependencies
### RaspberryPi Zero 2W
 - RaspberryPi OS
 - CMake Build Tools 3.10+
 - Make
 - g++
 - I2C Support
 - I2C-tools
 - RPLidar SDK

### RaspberryPi 5
 - RaspBerryPi OS
 - Python 3.9+
 - MediaPipe
 - Numpy
 - TensorFlow
 - Keras
 - SciKit Learn
 - MatPlot Library

### Arduino Uno
 - Arduino IDE

## Running The System
 - Power up robot and RaspberryPi 5 stations
 - Start gesture detection on RaspberryPi 5 via app.py
 - Start gesture_receiver_continuous.py on the RaspberryPi Zero 2W on robot
 - Start the robot_lidar process on the RaspberryPi Zero 2W on the robot
 - Set robot in position to receive and act on commands
 - Begin Gestures to command

<img width="572" height="480" alt="SystemActivity" src="https://github.com/user-attachments/assets/2ea246db-64b2-4b0b-a995-4d0a54d35b4c" />

## Gesture Commands
 - MOVE LEFT: Point left with right hand. Keep index finger and thumb out, remaining fingers clenched, palm facing you.
 - MOVE RIGHT: Point right with right hand. Keep index finger and thumb out, remaining fingers clenched, palm facing the camera.
 - STOP: Make fist and hold knuckles up to the sky, palm facing the camera.
 - MOVE BACKWARD: Make a peace sign by point to the sky with index finger and middle finger while maintaining a V shaped gap between them, clench remaining fingers and thumb, palm facing camera.
 - MOVE FORWARD: Open palm, fingers pointing up to the sky, palm facining camera. 
