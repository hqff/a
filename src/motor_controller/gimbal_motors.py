"""
Gimbal Motor Controller
Controls the 3-axis brushless gimbal via SimpleBGC controller.
"""

import serial
import struct
import threading
import time
from typing import Dict, Tuple
from config import GIMBAL_MOTORS, ARDUINO_SERIAL
from utils.logger import setup_logger


class GimbalController:
    """
    Controller for 3-axis brushless gimbal using SimpleBGC protocol.
    Controls pitch, roll, and yaw motors for camera stabilization.
    """
    
    def __init__(self):
        """Initialize gimbal controller."""
        self.logger = setup_logger('GimbalController', 'logs/gimbal.log')
        
        # Serial connection to SimpleBGC
        self.serial_port = None
        
        # Current angles
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        # Target angles
        self.target_pitch = 0.0
        self.target_roll = 0.0
        self.target_yaw = 0.0
        
        # Status
        self.initialized = False
        self.enabled = False
        self.running = False
    
    def initialize(self) -> bool:
        """
        Initialize gimbal controller.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing gimbal controller...")
            
            # Open serial connection to SimpleBGC
            # SimpleBGC typically uses 115200 baud
            try:
                self.serial_port = serial.Serial(
                    '/dev/ttyUSB0',  # Or /dev/ttyAMA0 for GPIO UART
                    baudrate=115200,
                    timeout=1.0
                )
                self.logger.info("Connected to SimpleBGC controller")
            except Exception as e:
                self.logger.error(f"Could not connect to SimpleBGC: {e}")
                return False
            
            # Send initialization commands
            time.sleep(0.5)
            
            # Enable motors
            self.enable_motors(True)
            
            self.initialized = True
            self.logger.info("Gimbal controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Gimbal initialization error: {e}", exc_info=True)
            return False
    
    def enable_motors(self, enable: bool):
        """
        Enable or disable gimbal motors.
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            if not self.serial_port:
                return
            
            # SimpleBGC command to enable/disable motors
            cmd_id = ord('M')  # Motors ON/OFF command
            data = struct.pack('B', 1 if enable else 0)
            
            self._send_command(cmd_id, data)
            
            self.enabled = enable
            self.logger.info(f"Motors {'enabled' if enable else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error enabling motors: {e}")
    
    def set_angle(self, pitch: float = None, roll: float = None, yaw: float = None, 
                  speed: int = 30):
        """
        Set gimbal angles.
        
        Args:
            pitch: Pitch angle in degrees (None to keep current)
            roll: Roll angle in degrees (None to keep current)
            yaw: Yaw angle in degrees (None to keep current)
            speed: Movement speed (0-255)
        """
        try:
            if pitch is not None:
                self.target_pitch = max(
                    GIMBAL_MOTORS['PITCH']['min_angle'],
                    min(GIMBAL_MOTORS['PITCH']['max_angle'], pitch)
                )
            
            if roll is not None:
                self.target_roll = max(
                    GIMBAL_MOTORS['ROLL']['min_angle'],
                    min(GIMBAL_MOTORS['ROLL']['max_angle'], roll)
                )
            
            if yaw is not None:
                self.target_yaw = max(
                    GIMBAL_MOTORS['YAW']['min_angle'],
                    min(GIMBAL_MOTORS['YAW']['max_angle'], yaw)
                )
            
            # Send control command to SimpleBGC
            if self.serial_port and self.enabled:
                self._send_control_command(
                    self.target_pitch,
                    self.target_roll,
                    self.target_yaw,
                    speed
                )
            
        except Exception as e:
            self.logger.error(f"Error setting angle: {e}")
    
    def get_angles(self) -> Tuple[float, float, float]:
        """
        Get current gimbal angles.
        
        Returns:
            Tuple of (pitch, roll, yaw) in degrees
        """
        return (self.pitch, self.roll, self.yaw)
    
    def run(self, stop_event: threading.Event):
        """
        Main gimbal control loop.
        
        Args:
            stop_event: Event to signal stop
        """
        self.logger.info("Gimbal control loop started")
        self.running = True
        
        while not stop_event.is_set() and self.running:
            try:
                # Read status from SimpleBGC
                if self.serial_port:
                    self._read_realtime_data()
                
                time.sleep(0.02)  # 50Hz update rate
                
            except Exception as e:
                self.logger.error(f"Error in gimbal loop: {e}")
                time.sleep(0.1)
        
        self.logger.info("Gimbal control loop stopped")
    
    def _send_command(self, cmd_id: int, data: bytes):
        """Send command to SimpleBGC."""
        if not self.serial_port:
            return
        
        # SimpleBGC protocol: > cmd_id size data checksum
        header = b'>'
        size = len(data)
        checksum = (cmd_id + size + sum(data)) % 256
        
        packet = header + struct.pack('BB', cmd_id, size) + data + struct.pack('B', checksum)
        self.serial_port.write(packet)
    
    def _send_control_command(self, pitch: float, roll: float, yaw: float, speed: int):
        """Send control command to SimpleBGC."""
        # Convert degrees to SimpleBGC units (0.02197265625 degrees per unit)
        pitch_units = int(pitch / 0.02197265625)
        roll_units = int(roll / 0.02197265625)
        yaw_units = int(yaw / 0.02197265625)
        
        # Command 67 ('C') - Control
        cmd_id = ord('C')
        data = struct.pack('<hhh', roll_units, pitch_units, yaw_units)
        
        self._send_command(cmd_id, data)
    
    def _read_realtime_data(self):
        """Read real-time data from SimpleBGC."""
        # This would parse incoming data packets
        # Simplified version
        pass
    
    def shutdown(self):
        """Shutdown gimbal controller."""
        self.logger.info("Shutting down gimbal controller...")
        self.running = False
        
        # Disable motors
        self.enable_motors(False)
        
        # Close serial port
        if self.serial_port:
            self.serial_port.close()
        
        self.logger.info("Gimbal controller shut down")
