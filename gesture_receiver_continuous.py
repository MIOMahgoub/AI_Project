"""
Network Gesture Receiver - Continuous LIDAR with OLED and Arduino I2C
Receives gesture commands, checks continuous LIDAR, sends via I2C to Arduino
"""

import socket
import sys
import os
import time

try:
    from smbus2 import SMBus
except ImportError:
    print("[ERROR] smbus2 not installed")
    sys.exit(1)

# OLED Display imports
try:
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    import board
    import busio
    OLED_AVAILABLE = True
except ImportError:
    print("[WARNING] OLED libraries not installed")
    OLED_AVAILABLE = False

# Configuration
GESTURE_PORT = 5555
I2C_BUS = 1
I2C_ARDUINO_ADDRESS = 0x08  # Arduino I2C address
LIDAR_STATUS_FILE = "/tmp/lidar_status.txt"

# OLED Configuration
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDRESS = 0x3C


def draw_face(oled, face_type="neutral"):
    """Draw different emotion faces on the OLED display"""
    if not oled:
        return
    
    try:
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
        draw = ImageDraw.Draw(image)
        
        face_x = OLED_WIDTH // 2
        face_y = OLED_HEIGHT // 2 + 5
        face_radius = 25
        eye_y = face_y - 8
        
        # Draw face outline
        draw.ellipse(
            (face_x - face_radius, face_y - face_radius, 
             face_x + face_radius, face_y + face_radius),
            outline=255, fill=0
        )
        
        if face_type == "happy":
            # Happy eyes (^_^)
            draw.line((face_x - 15, eye_y, face_x - 10, eye_y - 3), fill=255, width=2)
            draw.line((face_x - 10, eye_y - 3, face_x - 5, eye_y), fill=255, width=2)
            draw.line((face_x + 5, eye_y, face_x + 10, eye_y - 3), fill=255, width=2)
            draw.line((face_x + 10, eye_y - 3, face_x + 15, eye_y), fill=255, width=2)
            draw.arc((face_x - 12, face_y, face_x + 12, face_y + 15), 
                    start=0, end=180, fill=255, width=2)
            
        elif face_type == "neutral":
            # Neutral eyes (o_o)
            draw.ellipse((face_x - 15, eye_y - 3, face_x - 9, eye_y + 3), outline=255, fill=255)
            draw.ellipse((face_x + 9, eye_y - 3, face_x + 15, eye_y + 3), outline=255, fill=255)
            draw.line((face_x - 10, face_y + 10, face_x + 10, face_y + 10), fill=255, width=2)
            
        elif face_type == "excited":
            # Wide eyes (O_O)
            draw.ellipse((face_x - 17, eye_y - 5, face_x - 7, eye_y + 5), outline=255, fill=0)
            draw.ellipse((face_x - 14, eye_y - 2, face_x - 10, eye_y + 2), outline=255, fill=255)
            draw.ellipse((face_x + 7, eye_y - 5, face_x + 17, eye_y + 5), outline=255, fill=0)
            draw.ellipse((face_x + 10, eye_y - 2, face_x + 14, eye_y + 2), outline=255, fill=255)
            draw.ellipse((face_x - 8, face_y + 5, face_x + 8, face_y + 15), outline=255, fill=0)
            
        elif face_type == "spinning":
            # Dizzy eyes (@_@)
            draw.ellipse((face_x - 16, eye_y - 4, face_x - 8, eye_y + 4), outline=255, fill=0)
            draw.line((face_x - 14, eye_y - 2, face_x - 10, eye_y + 2), fill=255, width=1)
            draw.line((face_x - 10, eye_y - 2, face_x - 14, eye_y + 2), fill=255, width=1)
            draw.ellipse((face_x + 8, eye_y - 4, face_x + 16, eye_y + 4), outline=255, fill=0)
            draw.line((face_x + 10, eye_y - 2, face_x + 14, eye_y + 2), fill=255, width=1)
            draw.line((face_x + 14, eye_y - 2, face_x + 10, eye_y + 2), fill=255, width=1)
            for i in range(-10, 11, 2):
                y_offset = 2 if i % 4 == 0 else -2
                draw.point((face_x + i, face_y + 10 + y_offset), fill=255)
            
        elif face_type == "focused":
            # Focused eyes (>_<)
            draw.line((face_x - 16, eye_y, face_x - 8, eye_y), fill=255, width=2)
            draw.line((face_x - 8, eye_y - 3, face_x - 8, eye_y + 3), fill=255, width=1)
            draw.line((face_x + 8, eye_y, face_x + 16, eye_y), fill=255, width=2)
            draw.line((face_x + 8, eye_y - 3, face_x + 8, eye_y + 3), fill=255, width=1)
            draw.ellipse((face_x - 5, face_y + 8, face_x + 5, face_y + 12), outline=255, fill=255)
        
        oled.image(image)
        oled.show()
        
    except Exception as e:
        print(f"[OLED ERROR] {e}")


def display_gesture_info(oled, hand, sign, gesture):
    """Display gesture information with a face on OLED"""
    if not oled:
        return
    
    face_map = {
        "Peace sign": "happy",
        "Close": "neutral",
        "Open": "focused",
        "Left": "spinning",
        "Right": "spinning",
        "OK": "excited"
    }
    
    face_type = face_map.get(sign, "neutral")
    if gesture in face_map:
        face_type = face_map[gesture]
    
    draw_face(oled, face_type)


def initialize_oled():
    """Initialize the OLED display"""
    if not OLED_AVAILABLE:
        return None
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDRESS)
        oled.fill(0)
        oled.show()
        print(f"[OLED] ✓ Initialized at 0x{OLED_ADDRESS:02X}")
        return oled
    except Exception as e:
        print(f"[OLED ERROR] {e}")
        return None


def check_lidar_obstacles():
    """Read obstacle status from continuous LIDAR process"""
    try:
        if not os.path.exists(LIDAR_STATUS_FILE):
            return {'front': False, 'left': False, 'right': False}
            
        with open(LIDAR_STATUS_FILE, 'r') as f:
            output = f.read().strip()
        
        obstacles = {}
        for part in output.split('|'):
            if ':' in part:
                key, value = part.split(':')
                obstacles[key.lower()] = (value == '1')
        
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


def process_gesture(gesture_data, i2c_bus=None, oled=None):
    """Process gesture, check LIDAR, send I2C command"""
    try:
        parts = gesture_data.split('|')
        hand = sign = gesture = "Unknown"
        
        for part in parts:
            if part.startswith("Hand:"):
                hand = part.split(':')[1]
            elif part.startswith("Sign:"):
                sign = part.split(':')[1]
            elif part.startswith("Gesture:"):
                gesture = part.split(':')[1]
        
        print(f"\n{'='*60}")
        print(f"[GESTURE] Hand: {hand}, Sign: {sign}, Gesture: {gesture}")
        
        # Update OLED with face
        if oled:
            display_gesture_info(oled, hand, sign, gesture)
        
        direction = map_gesture_to_direction(sign, gesture)
        print(f"[COMMAND] Direction: {direction}")
        
        # Check LIDAR
        obstacles = check_lidar_obstacles()
        print(f"[LIDAR] Front: {'BLOCKED' if obstacles['front'] else 'clear'}, "
              f"Left: {'BLOCKED' if obstacles['left'] else 'clear'}, "
              f"Right: {'BLOCKED' if obstacles['right'] else 'clear'}")
        
        safe = check_safe_to_move(direction, obstacles)
        
        if safe:
            print(f"[SAFETY] ✓ Path clear - Executing {direction}")
            cmd = direction[0]  # F, L, R, S, B
        else:
            print(f"[SAFETY] ✗ BLOCKED - Sending STOP")
            cmd = 'S'
        
        # Send via I2C to Arduino
        if i2c_bus:
            try:
                i2c_bus.write_byte_data(I2C_ARDUINO_ADDRESS, 0x00, ord(cmd))
                print(f"[I2C] ✓ Sent '{cmd}' to Arduino at 0x{I2C_ARDUINO_ADDRESS:02X}")
            except OSError as e:
                print(f"[I2C ERROR] {e}")
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    """Main function"""
    print("="*60)
    print("  Gesture Receiver - Continuous LIDAR + OLED + Arduino I2C")
    print("="*60)
    
    # Initialize OLED
    oled = initialize_oled()
    
    # Initialize I2C for Arduino
    i2c_bus = None
    try:
        i2c_bus = SMBus(I2C_BUS)
        print(f"[I2C] ✓ Opened /dev/i2c-{I2C_BUS}")
        print(f"[I2C] Arduino at address 0x{I2C_ARDUINO_ADDRESS:02X}")
    except Exception as e:
        print(f"[I2C ERROR] {e}")
    
    print(f"\n[INFO] Reading LIDAR from {LIDAR_STATUS_FILE}")
    print("[INFO] Make sure LIDAR is running: sudo ~/AI_Project/out/robot_lidar &\n")
    
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
                        process_gesture(gesture_data, i2c_bus, oled)
            except Exception as e:
                print(f"[ERROR] {e}")
            finally:
                client_sock.close()
    
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        if oled:
            draw_face(oled, "neutral")
            time.sleep(0.5)
            oled.fill(0)
            oled.show()
    finally:
        server_sock.close()
        if i2c_bus:
            i2c_bus.close()


if __name__ == '__main__':
    main()
