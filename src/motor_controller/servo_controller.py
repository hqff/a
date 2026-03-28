"""
Servo Motor Controller
Controls servo motors for pan/tilt via PCA9685 PWM driver (connected to Arduino).
"""

import time
from typing import Dict
from config import SERVO_MOTORS, ARDUINO_COMMANDS
from utils.logger import setup_logger
from utils.helpers import map_value


class ServoController:
    """
    Controller for servo motors used for pan/tilt control.
    Communicates via Arduino which controls PCA9685 PWM driver.
    """
    
    def __init__(self):
        """Initialize servo controller."""
        self.logger = setup_logger('ServoController', 'logs/servo.log')
        
        # Current angles
        self.angles = {
            'SONY_PAN': 0.0,
            'PI_CAM_PAN': 0.0,
            'LED_PAN': 0.0,
            'LED_TILT': 0.0,
            'WIPER': 0.0,
        }
        
        # Reference to stepper controller (which has Arduino serial)
        self.arduino_connection = None
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize servo controller.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing servo controller...")
            
            # Servos are controlled via Arduino with PCA9685
            # The Arduino connection is shared with stepper controller
            # So we just initialize the servo positions
            
            # Set all servos to center position
            for servo_name in self.angles:
                self.set_servo_angle(servo_name, 0.0)
            
            self.initialized = True
            self.logger.info("Servo controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Servo initialization error: {e}", exc_info=True)
            return False
    
    def set_servo_angle(self, servo_name: str, angle: float):
        """
        Set servo to specific angle.
        
        Args:
            servo_name: Name of servo (SONY_PAN, PI_CAM_PAN, etc.)
            angle: Target angle in degrees
        """
        try:
            if servo_name not in SERVO_MOTORS:
                self.logger.error(f"Unknown servo: {servo_name}")
                return
            
            # Constrain angle to limits
            servo_config = SERVO_MOTORS[servo_name]
            angle = max(servo_config['min_angle'], 
                       min(servo_config['max_angle'], angle))
            
            # Convert angle to pulse width
            pulse_width = map_value(
                angle,
                servo_config['min_angle'],
                servo_config['max_angle'],
                servo_config['min_pulse'],
                servo_config['max_pulse']
            )
            
            # Send command via Arduino (would need Arduino connection)
            # For now, just log the action
            self.angles[servo_name] = angle
            self.logger.debug(f"{servo_name} set to {angle}° (pulse: {pulse_width}μs)")
            
            # In actual implementation, send command to Arduino:
            # command = {
            #     'cmd': ARDUINO_COMMANDS['SERVO_MOVE'],
            #     'servo': servo_name,
            #     'angle': angle,
            #     'pulse': int(pulse_width)
            # }
            # self.arduino_connection.send_command(command)
            
        except Exception as e:
            self.logger.error(f"Error setting servo angle: {e}")
    
    def get_servo_angle(self, servo_name: str) -> float:
        """
        Get current servo angle.
        
        Args:
            servo_name: Name of servo
            
        Returns:
            Current angle in degrees
        """
        return self.angles.get(servo_name, 0.0)
    
    def sweep_servo(self, servo_name: str, start_angle: float, end_angle: float, 
                    duration: float = 1.0, steps: int = 20):
        """
        Sweep servo from start to end angle.
        
        Args:
            servo_name: Name of servo
            start_angle: Start angle in degrees
            end_angle: End angle in degrees
            duration: Total sweep duration in seconds
            steps: Number of intermediate steps
        """
        try:
            delay = duration / steps
            
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * (i / steps)
                self.set_servo_angle(servo_name, angle)
                time.sleep(delay)
            
        except Exception as e:
            self.logger.error(f"Error sweeping servo: {e}")
    
    def center_all_servos(self):
        """Center all servos."""
        self.logger.info("Centering all servos...")
        for servo_name in self.angles:
            self.set_servo_angle(servo_name, 0.0)
    
    def shutdown(self):
        """Shutdown servo controller."""
        self.logger.info("Shutting down servo controller...")
        
        # Center all servos before shutdown
        self.center_all_servos()
        
        self.logger.info("Servo controller shut down")
