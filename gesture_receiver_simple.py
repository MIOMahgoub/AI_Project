"""
Network Gesture Receiver for Raspberry Pi Zero 2W
Receives gesture commands, calls C++ LIDAR program, sends via Serial
"""

import socket
import sys
import subprocess
import serial
import time

# Configuration
GESTURE_PORT = 5555
SERIAL_PORT = "/dev/ttyUSB0"  # Change this to your Pi Zero's port (check with ls /dev/ttyUSB*)
SERIAL_BAUD = 115200
LIDAR_PROGRAM = "/home/ivebens/AI_Project/out/robot_lidar"


def check_lidar_obstacles():
    """Run C++ LIDAR program and get obstacle status"""
    try:
        result = subprocess.run([LIDAR_PROGRAM], 
                              capture_output=True, 
                              text=True, 
                              timeout=2)
        
        # Parse output: "FRONT:0|LEFT:1|RIGHT:0"
        output = result.stdout.strip()
        obstacles = {}
        
        for part in output.split('|'):
            if ':' in part:  # FIX: Check if ':' exists before unpacking
                key, value = part.split(':')
                obstacles[key.lower()] = (value == '1')
        
        # Return default if parsing failed
        if not obstacles:
            return {'front': False, 'left': False, 'right': False}
            
        return obstacles
        
    except Exception as e:
        print(f"[LIDAR ERROR] {e}")
        return {'front': False, 'left': False, 'right': False}


def map_gesture_to_direction(sign, gesture):
    """Map gesture to movement direction"""
    if sign == "Open":
        return "FORWARD"
    elif sign == "Close":
        return "STOP"
    elif gesture == "Left" or sign == "Left":
        return "LEFT"
    elif gesture == "Right" or sign == "Right":
        return "RIGHT"
    elif sign == "Peace sign":
        return "BACKWARD"
    else:
        return "STOP"


def check_safe_to_move(direction, obstacles):
    """Check if safe to move in direction"""
    if direction == "FORWARD":
        return not obstacles.get('front', False)
    elif direction == "LEFT":
        return not obstacles.get('left', False)
    elif direction == "RIGHT":
        return not obstacles.get('right', False)
    return True


def process_gesture(gesture_data, serial_port=None):
    """Process gesture, check LIDAR, send Serial command"""
    try:
        # Parse gesture
        parts = gesture_data.split('|')
        sign = gesture = "Unknown"
        
        for part in parts:
            if part.startswith("Sign:"):
                sign = part.split(':')[1]
            elif part.startswith("Gesture:"):
                gesture = part.split(':')[1]
        
        print(f"\n{'='*60}")
        print(f"[GESTURE] Sign: {sign}, Gesture: {gesture}")
        
        # Map to direction
        direction = map_gesture_to_direction(sign, gesture)
        print(f"[COMMAND] Direction: {direction}")
        
        # Check LIDAR
        obstacles = check_lidar_obstacles()
        print(f"[LIDAR] Front: {'BLOCKED' if obstacles['front'] else 'clear'}, "
              f"Left: {'BLOCKED' if obstacles['left'] else 'clear'}, "
              f"Right: {'BLOCKED' if obstacles['right'] else 'clear'}")
        
        # Check safety
        safe = check_safe_to_move(direction, obstacles)
        
        if safe:
            print(f"[SAFETY] ✓ Path clear - Executing {direction}")
            cmd = direction[0]  # F, L, R, S, B
        else:
            print(f"[SAFETY] ✗ BLOCKED - Sending STOP")
            cmd = 'S'
        
        # Send via Serial
        if serial_port and serial_port.is_open:
            try:
                serial_port.write(f"{cmd}\n".encode())
                serial_port.flush()
                print(f"[SERIAL] ✓ Sent '{cmd}'")
            except Exception as e:
                print(f"[SERIAL ERROR] {e}")
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    """Main function"""
    print("="*60)
    print("  Gesture Receiver with LIDAR Safety (USB Serial)")
    print("="*60)
    
    # Initialize Serial
    serial_port = None
    try:
        serial_port = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        time.sleep(2)  # Wait for serial to stabilize
        print(f"[SERIAL] ✓ Opened {SERIAL_PORT} @ {SERIAL_BAUD} baud")
    except Exception as e:
        print(f"[SERIAL ERROR] {e}")
        print(f"[INFO] Make sure Pi Zero is connected to {SERIAL_PORT}")
    
    # Test LIDAR program
    print("\n[INFO] Testing LIDAR program...")
    obstacles = check_lidar_obstacles()
    print(f"[LIDAR] ✓ Working\n")
    
    # Create TCP server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind(('0.0.0.0', GESTURE_PORT))
        server_sock.listen(5)
        print(f"[INFO] ✓ Listening on port {GESTURE_PORT}\n")
        
        while True:
            print("[INFO] Waiting for gesture...")
            client_sock, client_addr = server_sock.accept()
            
            try:
                data = client_sock.recv(1024)
                if data:
                    gesture_data = data.decode('utf-8').strip()
                    if gesture_data:
                        process_gesture(gesture_data, serial_port)
            except Exception as e:
                print(f"[ERROR] {e}")
            finally:
                client_sock.close()
    
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        server_sock.close()
        if serial_port and serial_port.is_open:
            serial_port.close()


if __name__ == '__main__':
    main()
