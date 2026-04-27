"""
LED Light Controller
Controls Zifon T6C LED and IR LED array.
"""

import time
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

from config import GPIO_PINS, LIGHTING
from utils.logger import setup_logger
from utils.helpers import constrain


class LEDController:
    """
    Controller for LED lighting system.
    Controls Zifon T6C videolight and IR LED array.
    """
    
    def __init__(self, light_sensors=None):
        """
        Initialize LED controller.
        
        Args:
            light_sensors: Light sensor array for auto-adjustment
        """
        self.logger = setup_logger('LEDController', 'logs/led.log')
        self.light_sensors = light_sensors
        
        # Current settings
        self.main_led_brightness = LIGHTING['ZIFON_T6C']['default_brightness']
        self.main_led_enabled = False
        self.ir_leds_enabled = False
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize LED controller.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing LED controller...")
            
            if not GPIO_AVAILABLE:
                self.logger.warning("RPi.GPIO not available, using simulation mode")
                self.initialized = True
                return True
            
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup relay outputs
            GPIO.setup(GPIO_PINS['RELAY_MAIN_LED'], GPIO.OUT)
            GPIO.setup(GPIO_PINS['RELAY_IR_LED'], GPIO.OUT)
            
            # Initially off
            GPIO.output(GPIO_PINS['RELAY_MAIN_LED'], GPIO.LOW)
            GPIO.output(GPIO_PINS['RELAY_IR_LED'], GPIO.LOW)
            
            self.initialized = True
            self.logger.info("LED controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"LED initialization error: {e}", exc_info=True)
            return False
    
    def enable_main_led(self, enable: bool):
        """
        Enable or disable main LED.
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            if GPIO_AVAILABLE:
                GPIO.output(GPIO_PINS['RELAY_MAIN_LED'], 
                           GPIO.HIGH if enable else GPIO.LOW)
            
            self.main_led_enabled = enable
            self.logger.info(f"Main LED {'enabled' if enable else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error controlling main LED: {e}")
    
    def enable_ir_leds(self, enable: bool):
        """
        Enable or disable IR LEDs.
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            if GPIO_AVAILABLE:
                GPIO.output(GPIO_PINS['RELAY_IR_LED'], 
                           GPIO.HIGH if enable else GPIO.LOW)
            
            self.ir_leds_enabled = enable
            self.logger.info(f"IR LEDs {'enabled' if enable else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"Error controlling IR LEDs: {e}")
    
    def set_brightness(self, brightness: int):
        """
        Set main LED brightness.
        
        Args:
            brightness: Brightness 0-100%
        """
        try:
            brightness = constrain(brightness, 0, 100)
            self.main_led_brightness = brightness
            
            # Enable/disable based on brightness
            if brightness > 0:
                self.enable_main_led(True)
                # PWM control would go here if supported
                self.logger.debug(f"Main LED brightness set to {brightness}%")
            else:
                self.enable_main_led(False)
            
        except Exception as e:
            self.logger.error(f"Error setting brightness: {e}")
    
    def auto_adjust_lighting(self):
        """Automatically adjust lighting based on ambient light."""
        if not self.light_sensors:
            return
        
        try:
            avg_lux = self.light_sensors.get_average_lux()
            
            # Determine required brightness
            if avg_lux < 1:  # Very dark
                self.set_brightness(100)
                self.enable_ir_leds(True)
            elif avg_lux < 10:  # Dark
                self.set_brightness(80)
                self.enable_ir_leds(True)
            elif avg_lux < 100:  # Dim
                self.set_brightness(50)
                self.enable_ir_leds(False)
            elif avg_lux < 1000:  # Normal
                self.set_brightness(20)
                self.enable_ir_leds(False)
            else:  # Bright
                self.set_brightness(0)
                self.enable_ir_leds(False)
            
        except Exception as e:
            self.logger.error(f"Error in auto-adjust: {e}")
    
    def shutdown(self):
        """Shutdown LED controller."""
        self.logger.info("Shutting down LED controller...")
        
        # Turn off all LEDs
        self.enable_main_led(False)
        self.enable_ir_leds(False)
        
        if GPIO_AVAILABLE:
            GPIO.cleanup([GPIO_PINS['RELAY_MAIN_LED'], GPIO_PINS['RELAY_IR_LED']])
        
        self.logger.info("LED controller shut down")
