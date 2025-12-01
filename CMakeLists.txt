cmake_minimum_required(VERSION 3.10)
project(AI_Project)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Project sources
set(COMMON_SOURCES
    src/main.cpp
    src/lidar.cpp
    src/controller.cpp
    src/ObstacleDetector.cpp
)

# Path to SDK
set(RPLIDAR_SDK_DIR ${CMAKE_SOURCE_DIR}/lib/rplidar_sdk/sdk)

# Include SDK headers
include_directories(${RPLIDAR_SDK_DIR}/include)
include_directories(${RPLIDAR_SDK_DIR}/src)

include_directories(${CMAKE_SOURCE_DIR}/include)


# ---- WINDOWS BUILD ----
if (WIN32)
    list(APPEND COMMON_SOURCES src/I2C_stub.cpp)
    message(STATUS "Building on Windows: compiling SDK source files")

    # Main SDK sources
    file(GLOB RPLIDAR_SDK_SRC
        "${RPLIDAR_SDK_DIR}/src/*.cpp"
    )

    # Windows-specific HAL/OS layer
    file(GLOB RPLIDAR_SDK_WIN_SRC
        "${RPLIDAR_SDK_DIR}/src/arch/win32/*.cpp"
    )

    # HAL folder (threads, locks, events, timers)
    file(GLOB RPLIDAR_SDK_HAL_SRC
        "${RPLIDAR_SDK_DIR}/src/hal/*.cpp"
    )

    # NEW SDK Data Unpacker system
    file(GLOB RPLIDAR_SDK_UNPACKER_SRC
        "${RPLIDAR_SDK_DIR}/src/dataunpacker/*.cpp"
    )
    file(GLOB RPLIDAR_SDK_UNPACKER_INTERNAL_SRC
        "${RPLIDAR_SDK_DIR}/src/dataunpacker/unpacker/*.cpp"
    )

    add_executable(robot_lidar
	${COMMON_SOURCES}
        ${RPLIDAR_SDK_SRC}
        ${RPLIDAR_SDK_WIN_SRC}
        ${RPLIDAR_SDK_HAL_SRC}
        ${RPLIDAR_SDK_UNPACKER_SRC}
        ${RPLIDAR_SDK_UNPACKER_INTERNAL_SRC}
    )

    # Unit test for ObstacleDetector (does NOT use SDK)
    add_executable(test_obstacle_detector
        src/test_obstacle_detector.cpp
        src/ObstacleDetector.cpp
    )

    target_include_directories(test_obstacle_detector PRIVATE
        ${CMAKE_SOURCE_DIR}/include
    )
endif()



# ---- LINUX / PI ZERO BUILD ----
if (UNIX AND NOT WIN32)
    # Serial communication removed - obstacle detection only

    message(STATUS "Building on Linux/Pi: linking against librplidar_sdk.a")

    add_executable(robot_lidar
	${COMMON_SOURCES}
    )

    target_link_libraries(robot_lidar
    ${CMAKE_SOURCE_DIR}/lib/rplidar_sdk/output/Linux/Release/libsl_lidar_sdk.a
    pthread
)
endif()
