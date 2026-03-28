"""
Stepper Motor Controller
Controls stepper motors for camera zoom and focus via Arduino.
"""

import serial
import json
import threading
import time
from typing import Dict
from config import STEPPER_MOTORS, ARDUINO_SERIAL, ARDUINO_COMMANDS
from utils.logger import setup_logger


class StepperController:
    """
    Controller for stepper motors used for zoom and focus control.
    Communicates with Arduino Mega via serial.
    """
    
    def __init__(self):
        """Initialize stepper controller."""
        self.logger = setup_logger('StepperController', 'logs/stepper.log')
        
        # Serial connection to Arduino
        self.serial_port = None
        
        # Current positions
        self.positions = {
            'SONY_ZOOM': 0,
            'SONY_FOCUS': 0,
            'PI_CAM_ZOOM': 0,
            'PI_CAM_FOCUS': 0,
        }
        
        # Lock for serial communication
        self.serial_lock = threading.Lock()
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize stepper controller.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing stepper controller...")
            
            # Open serial connection to Arduino
            try:
                self.serial_port = serial.Serial(
                    ARDUINO_SERIAL['PORT'],
                    baudrate=ARDUINO_SERIAL['BAUDRATE'],
                    timeout=ARDUINO_SERIAL['TIMEOUT']
                )
                time.sleep(2.0)  # Wait for Arduino to reset
                self.logger.info("Connected to Arduino Mega")
            except Exception as e:
                self.logger.error(f"Could not connect to Arduino: {e}")
                return False
            
            # Calibrate motors (home position)
            self.calibrate_all()
            
            self.initialized = True
            self.logger.info("Stepper controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Stepper initialization error: {e}", exc_info=True)
            return False
    
    def move_motor(self, motor_name: str, position: int):
        """
        Move motor to absolute position.
        
        Args:
            motor_name: Name of motor (SONY_ZOOM, SONY_FOCUS, etc.)
            position: Target position in steps
        """
        try:
            if motor_name not in STEPPER_MOTORS:
                self.logger.error(f"Unknown motor: {motor_name}")
                return
            
            # Send command to Arduino
            command = {
                'cmd': ARDUINO_COMMANDS['STEPPER_MOVE'],
                'motor': motor_name,
                'position': position
            }
            
            response = self._send_command(command)
            
            if response and response.get('status') == 'ok':
                self.positions[motor_name] = position
                self.logger.debug(f"{motor_name} moved to position {position}")
            else:
                self.logger.error(f"Failed to move {motor_name}")
            
        except Exception as e:
            self.logger.error(f"Error moving motor: {e}")
    
    def move_motor_relative(self, motor_name: str, steps: int):
        """
        Move motor by relative number of steps.
        
        Args:
            motor_name: Name of motor
            steps: Number of steps (positive or negative)
        """
        current_pos = self.positions.get(motor_name, 0)
        new_pos = current_pos + steps
        self.move_motor(motor_name, new_pos)
    
    def stop_motor(self, motor_name: str):
        """
        Stop motor immediately.
        
        Args:
            motor_name: Name of motor
        """
        try:
            command = {
                'cmd': ARDUINO_COMMANDS['STEPPER_STOP'],
                'motor': motor_name
            }
            
            self._send_command(command)
            self.logger.debug(f"{motor_name} stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping motor: {e}")
    
    def calibrate_all(self):
        """Calibrate all motors to home position."""
        self.logger.info("Calibrating stepper motors...")
        
        try:
            command = {
                'cmd': ARDUINO_COMMANDS['CALIBRATE'],
                'motors': 'ALL'
            }
            
            response = self._send_command(command, timeout=10.0)
            
            if response and response.get('status') == 'ok':
                # Reset all positions to 0
                for motor in self.positions:
                    self.positions[motor] = 0
                self.logger.info("Calibration complete")
            else:
                self.logger.warning("Calibration may have failed")
            
        except Exception as e:
            self.logger.error(f"Calibration error: {e}")
    
    def get_position(self, motor_name: str) -> int:
        """
        Get current motor position.
        
        Args:
            motor_name: Name of motor
            
        Returns:
            Current position in steps
        """
        return self.positions.get(motor_name, 0)
    
    def _send_command(self, command: Dict, timeout: float = 2.0) -> Dict:
        """
        Send command to Arduino and wait for response.
        
        Args:
            command: Command dictionary
            timeout: Response timeout in seconds
            
        Returns:
            Response dictionary or None
        """
        with self.serial_lock:
            try:
                if not self.serial_port:
                    return None
                
                # Send command as JSON
                cmd_json = json.dumps(command) + '\n'
                self.serial_port.write(cmd_json.encode())
                
                # Wait for response
                start_time = time.time()
                while (time.time() - start_time) < timeout:
                    if self.serial_port.in_waiting > 0:
                        response_line = self.serial_port.readline().decode().strip()
                        try:
                            response = json.loads(response_line)
                            return response
                        except json.JSONDecodeError:
                            self.logger.warning(f"Invalid JSON response: {response_line}")
                    time.sleep(0.01)
                
                self.logger.warning("Command timeout")
                return None
                
            except Exception as e:
                self.logger.error(f"Error sending command: {e}")
                return None
    
    def shutdown(self):
        """Shutdown stepper controller."""
        self.logger.info("Shutting down stepper controller...")
        
        # Stop all motors
        for motor in self.positions:
            self.stop_motor(motor)
        
        # Close serial port
        if self.serial_port:
            self.serial_port.close()
        
        self.logger.info("Stepper controller shut down")
