"""
Raspberry Pi HQ Camera Controller
Controls the Pi HQ Camera Module with interchangeable lenses.
"""

import numpy as np
from typing import Optional, Dict
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    
from config import CURRENT_PI_LENS, PI_LENS_OPTIONS
from utils.logger import setup_logger


class PiHQCameraController:
    """
    Controller for Raspberry Pi HQ Camera Module.
    Supports various C/CS mount lenses.
    """
    
    def __init__(self, stepper_controller=None, servo_controller=None):
        """
        Initialize Pi HQ Camera controller.
        
        Args:
            stepper_controller: Stepper motor controller for zoom/focus
            servo_controller: Servo controller for pan
        """
        self.logger = setup_logger('PiHQCamera', 'logs/pi_hq_camera.log')
        self.stepper_controller = stepper_controller
        self.servo_controller = servo_controller
        
        # Camera instance
        self.camera = None
        
        # Current lens
        self.current_lens = CURRENT_PI_LENS
        self.lens_info = PI_LENS_OPTIONS.get(CURRENT_PI_LENS, {})
        
        # Current settings
        self.zoom_level = 0      # Only for zoom lens
        self.focus_distance = 50
        self.pan_angle = 0
        self.iso = 400
        self.brightness = 0.0
        self.exposure_time = 10000  # microseconds
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the camera.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing Pi HQ Camera...")
            
            if not PICAMERA2_AVAILABLE:
                self.logger.error("picamera2 library not available!")
                return False
            
            # Initialize Picamera2
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_still_configuration(
                main={"size": (1920, 1080)},  # Can use full 4056x3040 if needed
                buffer_count=2
            )
            self.camera.configure(config)
            
            # Start camera
            self.camera.start()
            
            # Set initial exposure
            self.camera.set_controls({
                "ExposureTime": self.exposure_time,
                "AnalogueGain": 1.0,
            })
            
            # Initialize motor positions
            if self.servo_controller:
                self.set_pan(0)
            
            self.initialized = True
            self.logger.info(f"Pi HQ Camera initialized with {self.current_lens} lens")
            return True
            
        except Exception as e:
            self.logger.error(f"Pi HQ Camera initialization error: {e}", exc_info=True)
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the camera.
        
        Returns:
            Frame as numpy array or None
        """
        if not self.initialized or self.camera is None:
            return None
        
        try:
            # Capture frame
            frame = self.camera.capture_array()
            
            # Convert from RGB to BGR for OpenCV compatibility
            if len(frame.shape) == 3:
                frame = frame[:, :, ::-1]
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error capturing frame: {e}")
            return None
    
    def set_zoom(self, zoom_percent: int):
        """
        Set zoom level (only for zoom lens).
        
        Args:
            zoom_percent: Zoom level 0-100%
        """
        if "ZOOM" not in self.current_lens:
            self.logger.debug("Current lens does not support zoom")
            return
        
        if not self.stepper_controller:
            return
        
        try:
            zoom_percent = max(0, min(100, zoom_percent))
            steps = int((zoom_percent / 100.0) * 2000)
            
            if self.stepper_controller:
                self.stepper_controller.move_motor('PI_CAM_ZOOM', steps)
            
            self.zoom_level = zoom_percent
            self.logger.debug(f"Zoom set to {zoom_percent}%")
            
        except Exception as e:
            self.logger.error(f"Error setting zoom: {e}")
    
    def set_focus(self, focus_percent: int):
        """
        Set focus distance.
        
        Args:
            focus_percent: Focus distance 0-100%
        """
        if not self.stepper_controller:
            return
        
        try:
            focus_percent = max(0, min(100, focus_percent))
            steps = int((focus_percent / 100.0) * 2000)
            
            if self.stepper_controller:
                self.stepper_controller.move_motor('PI_CAM_FOCUS', steps)
            
            self.focus_distance = focus_percent
            self.logger.debug(f"Focus set to {focus_percent}%")
            
        except Exception as e:
            self.logger.error(f"Error setting focus: {e}")
    
    def set_pan(self, angle: float):
        """
        Set pan angle.
        
        Args:
            angle: Pan angle in degrees (-90 to 90)
        """
        if not self.servo_controller:
            return
        
        try:
            angle = max(-90, min(90, angle))
            
            if self.servo_controller:
                self.servo_controller.set_servo_angle('PI_CAM_PAN', angle)
            
            self.pan_angle = angle
            self.logger.debug(f"Pan set to {angle} degrees")
            
        except Exception as e:
            self.logger.error(f"Error setting pan: {e}")
    
    def set_iso(self, iso: int):
        """
        Set ISO (analogue gain).
        
        Args:
            iso: ISO value (100-3200)
        """
        try:
            # Convert ISO to analogue gain
            # ISO 100 = gain 1.0, ISO 800 = gain 8.0
            gain = iso / 100.0
            gain = max(1.0, min(32.0, gain))
            
            if self.camera:
                self.camera.set_controls({"AnalogueGain": gain})
            
            self.iso = iso
            self.logger.debug(f"ISO set to {iso} (gain {gain})")
            
        except Exception as e:
            self.logger.error(f"Error setting ISO: {e}")
    
    def set_exposure_time(self, microseconds: int):
        """
        Set exposure time.
        
        Args:
            microseconds: Exposure time in microseconds
        """
        try:
            if self.camera:
                self.camera.set_controls({"ExposureTime": microseconds})
            
            self.exposure_time = microseconds
            self.logger.debug(f"Exposure time set to {microseconds}μs")
            
        except Exception as e:
            self.logger.error(f"Error setting exposure time: {e}")
    
    def get_info(self) -> Dict:
        """
        Get camera information.
        
        Returns:
            Dictionary with camera info
        """
        lens_info = PI_LENS_OPTIONS.get(self.current_lens, {})
        
        info = {
            'name': 'Raspberry Pi HQ Camera',
            'type': 'CSI Camera Module',
            'resolution': (1920, 1080),  # Current resolution
            'max_resolution': (4056, 3040),
            'fps': 30,
            'zoom_level': self.zoom_level if "ZOOM" in self.current_lens else None,
            'focus_distance': self.focus_distance,
            'pan_angle': self.pan_angle,
            'iso': self.iso,
            'brightness': self.brightness,
            'exposure_time': self.exposure_time,
            'lens_type': self.current_lens,
        }
        
        # Add lens-specific info
        if 'focal_length' in lens_info:
            info['focal_length'] = lens_info['focal_length']
        if 'focal_length_min' in lens_info:
            info['focal_length_min'] = lens_info['focal_length_min']
            info['focal_length_max'] = lens_info['focal_length_max']
        if 'mount' in lens_info:
            info['lens_mount'] = lens_info['mount']
        
        return info
    
    def shutdown(self):
        """Release resources."""
        if self.camera:
            self.camera.stop()
            self.camera.close()
        self.logger.info("Pi HQ Camera shut down")
