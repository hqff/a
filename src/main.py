#!/usr/bin/env python3
"""
Main Controller for Multi-Camera Gimbal System
Raspberry Pi 5 - Ubuntu

This is the main entry point for the gimbal system.
It initializes all subsystems and manages the main control loop.
"""

import sys
import time
import signal
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import threading

# Import configuration
from config import *

# Import subsystem modules (to be implemented)
from camera_controller.camera_manager import CameraManager
from motor_controller.gimbal_motors import GimbalController
from motor_controller.stepper_motors import StepperController
from motor_controller.servo_controller import ServoController
from lighting.led_controller import LEDController
from lighting.light_sensor import LightSensorArray
from video_processing.multi_stream import MultiStreamProcessor
from ui.display_manager import DisplayManager
from transmission.frequency_hopper import FrequencyHopper
from utils.logger import setup_logger
from utils.helpers import SystemMonitor


class MultiCameraGimbalSystem:
    """
    Main system controller for the multi-camera gimbal.
    Coordinates all subsystems and manages the main control loop.
    """
    
    def __init__(self):
        """Initialize the gimbal system."""
        self.logger = setup_logger('GimbalSystem', LOGGING['FILE'])
        self.logger.info("=" * 70)
        self.logger.info("Multi-Camera Gimbal System Initializing...")
        self.logger.info("=" * 70)
        
        # System state
        self.running = False
        self.mode = DEFAULT_MODE
        self.emergency_stop = False
        
        # Subsystem instances
        self.camera_manager: Optional[CameraManager] = None
        self.gimbal_controller: Optional[GimbalController] = None
        self.stepper_controller: Optional[StepperController] = None
        self.servo_controller: Optional[ServoController] = None
        self.led_controller: Optional[LEDController] = None
        self.light_sensors: Optional[LightSensorArray] = None
        self.stream_processor: Optional[MultiStreamProcessor] = None
        self.display_manager: Optional[DisplayManager] = None
        self.frequency_hopper: Optional[FrequencyHopper] = None
        self.system_monitor: Optional[SystemMonitor] = None
        
        # Threading
        self.threads = []
        self.stop_event = threading.Event()
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.warning(f"Received signal {signum}. Initiating shutdown...")
        self.shutdown()
        sys.exit(0)
    
    def initialize_subsystems(self) -> bool:
        """
        Initialize all subsystems.
        
        Returns:
            bool: True if all subsystems initialized successfully
        """
        try:
            self.logger.info("Initializing subsystems...")
            
            # 1. Initialize system monitor
            self.logger.info("Initializing system monitor...")
            self.system_monitor = SystemMonitor()
            self.system_monitor.start()
            
            # 2. Initialize light sensors (needed for auto-adjustments)
            self.logger.info("Initializing light sensors...")
            self.light_sensors = LightSensorArray()
            if not self.light_sensors.initialize():
                self.logger.warning("Light sensors initialization failed, continuing anyway")
            
            # 3. Initialize LED controller
            self.logger.info("Initializing LED controller...")
            self.led_controller = LEDController(self.light_sensors)
            if not self.led_controller.initialize():
                self.logger.warning("LED controller initialization failed")
            
            # 4. Initialize gimbal controller
            self.logger.info("Initializing gimbal controller...")
            self.gimbal_controller = GimbalController()
            if not self.gimbal_controller.initialize():
                self.logger.error("Gimbal controller initialization failed!")
                return False
            
            # 5. Initialize stepper motor controller
            self.logger.info("Initializing stepper motor controller...")
            self.stepper_controller = StepperController()
            if not self.stepper_controller.initialize():
                self.logger.warning("Stepper controller initialization failed")
            
            # 6. Initialize servo controller
            self.logger.info("Initializing servo controller...")
            self.servo_controller = ServoController()
            if not self.servo_controller.initialize():
                self.logger.warning("Servo controller initialization failed")
            
            # 7. Initialize camera manager
            self.logger.info("Initializing camera manager...")
            self.camera_manager = CameraManager(
                light_sensors=self.light_sensors,
                stepper_controller=self.stepper_controller,
                servo_controller=self.servo_controller
            )
            if not self.camera_manager.initialize():
                self.logger.error("Camera manager initialization failed!")
                return False
            
            # 8. Initialize video stream processor
            self.logger.info("Initializing video stream processor...")
            self.stream_processor = MultiStreamProcessor(self.camera_manager)
            if not self.stream_processor.initialize():
                self.logger.error("Stream processor initialization failed!")
                return False
            
            # 9. Initialize frequency hopper (for anti-jamming)
            if FREQUENCY_HOPPING['ENABLED']:
                self.logger.info("Initializing frequency hopper...")
                self.frequency_hopper = FrequencyHopper()
                if not self.frequency_hopper.initialize():
                    self.logger.warning("Frequency hopper initialization failed")
            
            # 10. Initialize display manager (must be last)
            self.logger.info("Initializing display manager...")
            self.display_manager = DisplayManager(
                camera_manager=self.camera_manager,
                stream_processor=self.stream_processor,
                system_monitor=self.system_monitor
            )
            if not self.display_manager.initialize():
                self.logger.warning("Display manager initialization failed")
            
            self.logger.info("All subsystems initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during subsystem initialization: {e}", exc_info=True)
            return False
    
    def start(self) -> bool:
        """
        Start the gimbal system.
        
        Returns:
            bool: True if started successfully
        """
        try:
            self.logger.info("Starting Multi-Camera Gimbal System...")
            
            if not self.initialize_subsystems():
                self.logger.error("Failed to initialize subsystems!")
                return False
            
            # Start subsystem threads
            self.running = True
            
            # Start camera capture threads
            if self.camera_manager:
                self.threads.append(threading.Thread(
                    target=self.camera_manager.run,
                    args=(self.stop_event,),
                    daemon=True
                ))
            
            # Start video processing thread
            if self.stream_processor:
                self.threads.append(threading.Thread(
                    target=self.stream_processor.run,
                    args=(self.stop_event,),
                    daemon=True
                ))
            
            # Start gimbal stabilization thread
            if self.gimbal_controller:
                self.threads.append(threading.Thread(
                    target=self.gimbal_controller.run,
                    args=(self.stop_event,),
                    daemon=True
                ))
            
            # Start auto-adjustment thread
            self.threads.append(threading.Thread(
                target=self._auto_adjustment_loop,
                daemon=True
            ))
            
            # Start all threads
            for thread in self.threads:
                thread.start()
            
            self.logger.info("System started successfully!")
            self.logger.info(f"Operating mode: {self.mode}")
            
            # Run main control loop
            self._main_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}", exc_info=True)
            return False
    
    def _main_loop(self):
        """
        Main control loop.
        Handles display updates and user input.
        """
        self.logger.info("Entering main control loop...")
        
        try:
            while self.running and not self.emergency_stop:
                # Update display
                if self.display_manager:
                    self.display_manager.update()
                
                # Check for user input
                self._handle_user_input()
                
                # Monitor system health
                if self.system_monitor:
                    health = self.system_monitor.get_health_status()
                    if health['temperature'] > SAFETY_LIMITS['MAX_TEMPERATURE']:
                        self.logger.error("CRITICAL: Temperature too high!")
                        self.emergency_stop = True
                    
                    if health['battery_voltage'] < SAFETY_LIMITS['MIN_BATTERY_VOLTAGE']:
                        self.logger.error("CRITICAL: Battery voltage too low!")
                        self.emergency_stop = True
                
                # Small delay to prevent CPU spinning
                time.sleep(0.01)  # 100 FPS max
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def _auto_adjustment_loop(self):
        """
        Automatic adjustment loop.
        Continuously adjusts camera settings and lighting based on environment.
        """
        self.logger.info("Auto-adjustment loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                if self.mode == "AUTO" or self.mode == "NIGHT":
                    # Read light levels
                    if self.light_sensors:
                        avg_lux = self.light_sensors.get_average_lux()
                        light_level = self._classify_light_level(avg_lux)
                        
                        # Adjust ISO
                        target_iso = ISO_AUTO_ADJUST.get(light_level, 400)
                        if self.camera_manager:
                            self.camera_manager.set_all_iso(target_iso)
                        
                        # Adjust LED brightness
                        target_brightness = LED_AUTO_ADJUST.get(light_level, 50)
                        if self.led_controller:
                            self.led_controller.set_brightness(target_brightness)
                        
                        # Enable IR LEDs in dark conditions
                        if light_level in ["DARK", "VERY_DARK"] or self.mode == "NIGHT":
                            if self.led_controller:
                                self.led_controller.enable_ir_leds(True)
                        else:
                            if self.led_controller:
                                self.led_controller.enable_ir_leds(False)
                
                # Sleep for adjustment interval
                time.sleep(1.0)  # Adjust every second
                
            except Exception as e:
                self.logger.error(f"Error in auto-adjustment loop: {e}", exc_info=True)
                time.sleep(1.0)
    
    def _classify_light_level(self, lux: float) -> str:
        """Classify light level based on lux reading."""
        if lux >= LIGHT_THRESHOLDS['VERY_BRIGHT']:
            return 'VERY_BRIGHT'
        elif lux >= LIGHT_THRESHOLDS['BRIGHT']:
            return 'BRIGHT'
        elif lux >= LIGHT_THRESHOLDS['NORMAL']:
            return 'NORMAL'
        elif lux >= LIGHT_THRESHOLDS['DIM']:
            return 'DIM'
        elif lux >= LIGHT_THRESHOLDS['DARK']:
            return 'DARK'
        else:
            return 'VERY_DARK'
    
    def _handle_user_input(self):
        """Handle user input from touchscreen or other sources."""
        if self.display_manager:
            events = self.display_manager.get_events()
            for event in events:
                if event['type'] == 'mode_change':
                    self.set_mode(event['mode'])
                elif event['type'] == 'camera_select':
                    self.camera_manager.set_primary_camera(event['camera_id'])
                elif event['type'] == 'emergency_stop':
                    self.emergency_stop = True
    
    def set_mode(self, mode: str):
        """
        Set operating mode.
        
        Args:
            mode: Operating mode (AUTO, MANUAL, NIGHT, STREAMING, RECORDING)
        """
        if mode in OPERATING_MODES.values():
            self.logger.info(f"Changing mode from {self.mode} to {mode}")
            self.mode = mode
            
            # Apply mode-specific settings
            if mode == "NIGHT":
                # Enable IR LEDs, high ISO
                if self.led_controller:
                    self.led_controller.enable_ir_leds(True)
                if self.camera_manager:
                    self.camera_manager.set_all_iso(3200)
            
            elif mode == "STREAMING":
                # Lower resolution/bitrate for streaming
                if self.stream_processor:
                    self.stream_processor.set_streaming_mode(True)
            
            elif mode == "RECORDING":
                # Maximum quality
                if self.stream_processor:
                    self.stream_processor.set_streaming_mode(False)
        else:
            self.logger.warning(f"Invalid mode: {mode}")
    
    def shutdown(self):
        """Graceful shutdown of all subsystems."""
        if not self.running:
            return
        
        self.logger.info("=" * 70)
        self.logger.info("Shutting down Multi-Camera Gimbal System...")
        self.logger.info("=" * 70)
        
        self.running = False
        self.stop_event.set()
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2.0)
        
        # Shutdown subsystems in reverse order
        if self.display_manager:
            self.logger.info("Shutting down display manager...")
            self.display_manager.shutdown()
        
        if self.frequency_hopper:
            self.logger.info("Shutting down frequency hopper...")
            self.frequency_hopper.shutdown()
        
        if self.stream_processor:
            self.logger.info("Shutting down stream processor...")
            self.stream_processor.shutdown()
        
        if self.camera_manager:
            self.logger.info("Shutting down camera manager...")
            self.camera_manager.shutdown()
        
        if self.servo_controller:
            self.logger.info("Shutting down servo controller...")
            self.servo_controller.shutdown()
        
        if self.stepper_controller:
            self.logger.info("Shutting down stepper controller...")
            self.stepper_controller.shutdown()
        
        if self.gimbal_controller:
            self.logger.info("Shutting down gimbal controller...")
            self.gimbal_controller.shutdown()
        
        if self.led_controller:
            self.logger.info("Shutting down LED controller...")
            self.led_controller.shutdown()
        
        if self.light_sensors:
            self.logger.info("Shutting down light sensors...")
            self.light_sensors.shutdown()
        
        if self.system_monitor:
            self.logger.info("Shutting down system monitor...")
            self.system_monitor.shutdown()
        
        self.logger.info("Shutdown complete. Goodbye!")


def main():
    """Main entry point."""
    print("=" * 70)
    print("Multi-Camera Gimbal System")
    print("Raspberry Pi 5 - Ubuntu")
    print("=" * 70)
    print()
    
    try:
        # Create and start the system
        system = MultiCameraGimbalSystem()
        system.start()
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
