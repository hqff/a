"""
Configuration file for Multi-Camera Gimbal System
Raspberry Pi 5 - Ubuntu
"""

import os
from typing import Dict, List, Tuple

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

# System paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
VIDEO_DIR = os.path.join(BASE_DIR, "recordings")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Create directories if they don't exist
for directory in [LOG_DIR, VIDEO_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================

# Camera types
CAMERA_TYPES = {
    "SONY_PJ670": "sony_pj670",
    "PI_HQ_CAM": "pi_hq_camera",
    "WEBCAM_1": "logitech_brio_1",
    "WEBCAM_2": "logitech_brio_2",
    "WEBCAM_3": "logitech_brio_3",
}

# Camera resolutions
CAMERA_RESOLUTIONS = {
    "SONY_PJ670": (1920, 1080),      # 1080p
    "PI_HQ_CAM": (4056, 3040),       # 12.3MP (can be downscaled)
    "WEBCAM": (1920, 1080),          # 1080p
}

# Camera frame rates
CAMERA_FPS = {
    "SONY_PJ670": 30,
    "PI_HQ_CAM": 30,
    "WEBCAM": 30,
}

# Pi HQ Camera lens options
PI_LENS_OPTIONS = {
    "16MM_TELEPHOTO": {"focal_length": 16, "mount": "C"},
    "6MM_WIDE": {"focal_length": 6, "mount": "CS"},
    "35MM_STANDARD": {"focal_length": 35, "mount": "C"},
    "8_50MM_ZOOM": {"focal_length_min": 8, "focal_length_max": 50, "mount": "C"},
}

# Default lens selection (change based on what's installed)
CURRENT_PI_LENS = "8_50MM_ZOOM"

# ============================================================================
# GPIO PIN CONFIGURATION (Raspberry Pi 5)
# ============================================================================

GPIO_PINS = {
    # I2C for light sensors (hardware I2C)
    "I2C_SDA": 2,
    "I2C_SCL": 3,
    
    # UART for Arduino communication
    "UART_TX": 14,
    "UART_RX": 15,
    
    # Digital outputs for relay control
    "RELAY_MAIN_LED": 17,      # Zifon T6C control
    "RELAY_IR_LED": 27,        # IR LED array control
    "RELAY_SERVO_POWER": 22,   # Servo power control
    
    # SimpleBGC gimbal control
    "GIMBAL_ENABLE": 23,       # Enable gimbal controller
    
    # Servo controls (via software PWM or PCA9685)
    "WIPER_SERVO": 24,         # Rain wiper servo
    
    # SPI for NRF24L01 RF module
    "SPI_MOSI": 10,
    "SPI_MISO": 9,
    "SPI_SCLK": 11,
    "SPI_CE0": 8,
    "SPI_CE1": 7,
    
    # Other digital I/O
    "EMERGENCY_STOP": 25,      # Emergency stop button
    "STATUS_LED": 4,           # System status LED
}

# ============================================================================
# I2C DEVICE ADDRESSES
# ============================================================================

I2C_ADDRESSES = {
    "BH1750_FRONT": 0x23,      # Light sensor front (ADDR -> GND)
    "BH1750_TOP": 0x5C,        # Light sensor top (ADDR -> VCC)
    "BH1750_LEFT": 0x23,       # On separate I2C bus if available
    "BH1750_RIGHT": 0x5C,      # On separate I2C bus if available
    "PCA9685": 0x40,           # PWM servo driver (on Arduino I2C)
}

# ============================================================================
# MOTOR CONFIGURATION
# ============================================================================

# Gimbal motors (SimpleBGC controller)
GIMBAL_MOTORS = {
    "PITCH": {"min_angle": -90, "max_angle": 90},
    "ROLL": {"min_angle": -45, "max_angle": 45},
    "YAW": {"min_angle": -180, "max_angle": 180},
}

# Stepper motors (via Arduino)
STEPPER_MOTORS = {
    "SONY_ZOOM": {"steps_per_rev": 200, "microstepping": 16, "max_speed": 1000},
    "SONY_FOCUS": {"steps_per_rev": 200, "microstepping": 16, "max_speed": 800},
    "PI_CAM_ZOOM": {"steps_per_rev": 200, "microstepping": 16, "max_speed": 600},
    "PI_CAM_FOCUS": {"steps_per_rev": 200, "microstepping": 16, "max_speed": 600},
}

# Servo motors (via PCA9685)
SERVO_MOTORS = {
    "SONY_PAN": {"min_pulse": 500, "max_pulse": 2500, "min_angle": -90, "max_angle": 90},
    "PI_CAM_PAN": {"min_pulse": 500, "max_pulse": 2500, "min_angle": -90, "max_angle": 90},
    "LED_PAN": {"min_pulse": 500, "max_pulse": 2500, "min_angle": -180, "max_angle": 180},
    "LED_TILT": {"min_pulse": 500, "max_pulse": 2500, "min_angle": -45, "max_angle": 45},
    "WIPER": {"min_pulse": 500, "max_pulse": 2500, "min_angle": 0, "max_angle": 120},
}

# ============================================================================
# LIGHTING CONFIGURATION
# ============================================================================

LIGHTING = {
    "ZIFON_T6C": {
        "max_brightness": 100,      # Percentage
        "default_brightness": 50,
        "auto_adjust": True,
    },
    "IR_LED_ARRAY": {
        "power": 9,                  # Watts (3x 3W)
        "voltage": 5,                # Volts
        "wavelength": 850,           # nm (or 940nm)
        "auto_enable_lux": 50,       # Enable below this lux level
    },
}

# Light sensor thresholds (lux)
LIGHT_THRESHOLDS = {
    "VERY_BRIGHT": 10000,    # Direct sunlight
    "BRIGHT": 1000,          # Overcast day
    "NORMAL": 100,           # Well-lit room
    "DIM": 10,               # Twilight
    "DARK": 1,               # Night
    "VERY_DARK": 0.1,        # Complete darkness
}

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

VIDEO_ENCODING = {
    "CODEC": "h264",
    "BITRATE": "5M",             # 5 Mbps for high quality
    "PROFILE": "high",
    "PRESET": "medium",
    "PIX_FMT": "yuv420p",
}

# Multi-view layout
MULTI_VIEW_LAYOUT = {
    "GRID_2x2": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "GRID_2x3": [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)],
    "PICTURE_IN_PICTURE": "main_with_thumbnails",
}

# ============================================================================
# TRANSMISSION CONFIGURATION
# ============================================================================

# Network streaming
NETWORK_STREAM = {
    "RTSP_PORT": 8554,
    "HTTP_PORT": 8080,
    "WEBSOCKET_PORT": 8765,
}

# RF transmission (NRF24L01+)
RF_CONFIG = {
    "CHANNEL": 76,               # 2.476 GHz
    "DATA_RATE": "250KBPS",      # Lower rate = longer range
    "PA_LEVEL": "PA_MAX",        # Max power with PA+LNA module
    "PAYLOAD_SIZE": 32,          # Bytes per packet
}

# Frequency hopping for anti-jamming
FREQUENCY_HOPPING = {
    "ENABLED": True,
    "CHANNELS": [40, 50, 60, 70, 76, 80, 90, 100, 110, 120],  # 2.4GHz channels
    "HOP_INTERVAL": 0.5,         # Seconds
    "JAMMING_THRESHOLD": -70,    # dBm RSSI threshold
}

# 4G/5G streaming
CELLULAR_STREAM = {
    "ENABLED": True,
    "STREAM_URL": "rtmp://stream.example.com/live",  # Configure your server
    "BACKUP_URL": "rtmp://backup.example.com/live",
    "MAX_BITRATE": "2M",         # Lower for cellular
}

# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================

# 5" touchscreen display
DISPLAY = {
    "WIDTH": 800,
    "HEIGHT": 480,
    "FPS": 30,
    "FULLSCREEN": True,
}

# UI elements
UI_CONFIG = {
    "FONT_SIZE_TITLE": 24,
    "FONT_SIZE_NORMAL": 16,
    "FONT_SIZE_SMALL": 12,
    "COLOR_PRIMARY": (0, 120, 215),      # Blue
    "COLOR_SECONDARY": (128, 128, 128),  # Gray
    "COLOR_SUCCESS": (0, 200, 0),        # Green
    "COLOR_WARNING": (255, 165, 0),      # Orange
    "COLOR_ERROR": (255, 0, 0),          # Red
    "COLOR_TEXT": (255, 255, 255),       # White
    "COLOR_BACKGROUND": (0, 0, 0),       # Black
}

# Overlay info to display
OVERLAY_INFO = [
    "camera_name",
    "resolution",
    "fps",
    "iso",
    "brightness",
    "zoom_level",
    "focus_distance",
    "lens_type",
    "battery_level",
    "recording_time",
]

# ============================================================================
# AUTO-ADJUSTMENT PARAMETERS
# ============================================================================

# ISO adjustment based on light levels
ISO_AUTO_ADJUST = {
    "VERY_BRIGHT": 100,
    "BRIGHT": 200,
    "NORMAL": 400,
    "DIM": 800,
    "DARK": 1600,
    "VERY_DARK": 3200,
}

# LED brightness adjustment based on light levels
LED_AUTO_ADJUST = {
    "VERY_BRIGHT": 0,      # No LED needed
    "BRIGHT": 0,
    "NORMAL": 20,
    "DIM": 50,
    "DARK": 80,
    "VERY_DARK": 100,
}

# ============================================================================
# SYSTEM MODES
# ============================================================================

OPERATING_MODES = {
    "AUTO": "auto",              # Full auto mode
    "MANUAL": "manual",          # Manual control via touchscreen
    "NIGHT": "night",            # Optimized for night (IR LEDs, high ISO)
    "STREAMING": "streaming",    # Optimized for streaming (lower res, bitrate)
    "RECORDING": "recording",    # Optimized for high-quality recording
}

DEFAULT_MODE = "AUTO"

# ============================================================================
# SAFETY AND LIMITS
# ============================================================================

SAFETY_LIMITS = {
    "MAX_TEMPERATURE": 85,       # Celsius (Pi 5 throttles at 85°C)
    "MIN_BATTERY_VOLTAGE": 12.0, # Volts (4S LiPo low voltage)
    "MAX_CURRENT": 8.0,          # Amps
    "EMERGENCY_STOP_ENABLED": True,
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING = {
    "LEVEL": "INFO",             # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "FILE": os.path.join(LOG_DIR, "gimbal_system.log"),
    "MAX_BYTES": 10485760,       # 10 MB
    "BACKUP_COUNT": 5,
}

# ============================================================================
# CALIBRATION DATA (to be populated during calibration)
# ============================================================================

CALIBRATION = {
    "GIMBAL_PITCH_OFFSET": 0,
    "GIMBAL_ROLL_OFFSET": 0,
    "GIMBAL_YAW_OFFSET": 0,
    "SONY_ZOOM_MIN_STEPS": 0,
    "SONY_ZOOM_MAX_STEPS": 5000,
    "SONY_FOCUS_MIN_STEPS": 0,
    "SONY_FOCUS_MAX_STEPS": 3000,
    "PI_CAM_ZOOM_MIN_STEPS": 0,
    "PI_CAM_ZOOM_MAX_STEPS": 2000,
    "LIGHT_SENSOR_CALIBRATION": {
        "BH1750_FRONT": 1.0,
        "BH1750_TOP": 1.0,
    },
}

# ============================================================================
# ARDUINO COMMUNICATION PROTOCOL
# ============================================================================

ARDUINO_SERIAL = {
    "PORT": "/dev/ttyACM0",      # May be /dev/ttyUSB0
    "BAUDRATE": 115200,
    "TIMEOUT": 1.0,
}

# Command protocol (JSON-based)
ARDUINO_COMMANDS = {
    "STEPPER_MOVE": "SM",
    "STEPPER_STOP": "SS",
    "SERVO_MOVE": "SV",
    "GET_STATUS": "GS",
    "SET_SPEED": "SP",
    "CALIBRATE": "CAL",
}

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE = {
    "USE_THREADING": True,
    "USE_GPU_ACCELERATION": True,    # If available
    "BUFFER_SIZE": 10,               # Frame buffer
    "PROCESS_EVERY_N_FRAMES": 1,     # Process every frame
}

# ============================================================================
# DEBUG AND DEVELOPMENT
# ============================================================================

DEBUG = {
    "ENABLED": False,
    "SHOW_FPS": True,
    "SHOW_LATENCY": True,
    "SAVE_DEBUG_IMAGES": False,
    "SIMULATE_HARDWARE": False,      # For testing without actual hardware
}
