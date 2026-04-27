"""
Sony PJ670 Handycam Controller
Controls the Sony PJ670 via HDMI capture and mechanical control.
"""

import cv2
import numpy as np
from typing import Optional, Dict
from utils.logger import setup_logger


class SonyPJ670Controller:
    """
    Controller for Sony PJ670 Handycam.
    
    Note: The PJ670 doesn't have direct USB control, so we use:
    - HDMI capture card for video input
    - Stepper motors for mechanical zoom/focus control
    - Servo for pan control
    - Optional LANC protocol for advanced control
    """
    
    def __init__(self, stepper_controller=None, servo_controller=None):
        """
        Initialize Sony PJ670 controller.
        
        Args:
            stepper_controller: Stepper motor controller for zoom/focus
            servo_controller: Servo controller for pan
        """
        self.logger = setup_logger('SonyPJ670', 'logs/sony_pj670.log')
        self.stepper_controller = stepper_controller
        self.servo_controller = servo_controller
        
        # Video capture (HDMI capture card)
        self.capture = None
        self.video_device = None
        
        # Current settings
        self.zoom_level = 0      # 0-100%
        self.focus_distance = 50  # 0-100%
        self.pan_angle = 0       # -90 to 90 degrees
        self.iso = 400
        self.brightness = 50
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the camera.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing Sony PJ670...")
            
            # Find HDMI capture device
            # Usually /dev/video0 or /dev/video1
            for device_id in range(10):
                try:
                    cap = cv2.VideoCapture(device_id)
                    if cap.isOpened():
                        # Check if it's the right device (1080p capable)
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        
                        if width >= 1920 and height >= 1080:
                            self.capture = cap
                            self.video_device = device_id
                            self.logger.info(f"Found Sony PJ670 on /dev/video{device_id}")
                            break
                    cap.release()
                except:
                    continue
            
            if self.capture is None:
                self.logger.error("Could not find Sony PJ670 HDMI capture device")
                return False
            
            # Configure capture
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            # Initialize motor positions
            if self.stepper_controller:
                # Home position for zoom and focus
                pass  # Implement homing sequence
            
            if self.servo_controller:
                # Center pan servo
                self.set_pan(0)
            
            self.initialized = True
            self.logger.info("Sony PJ670 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Sony PJ670 initialization error: {e}", exc_info=True)
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the camera.
        
        Returns:
            Frame as numpy array or None
        """
        if not self.initialized or self.capture is None:
            return None
        
        try:
            ret, frame = self.capture.read()
            if ret:
                return frame
            return None
        except Exception as e:
            self.logger.error(f"Error capturing frame: {e}")
            return None
    
    def set_zoom(self, zoom_percent: int):
        """
        Set zoom level.
        
        Args:
            zoom_percent: Zoom level 0-100%
        """
        if not self.stepper_controller:
            return
        
        try:
            zoom_percent = max(0, min(100, zoom_percent))
            # Calculate steps needed
            # This would need calibration
            steps = int((zoom_percent / 100.0) * 5000)  # Assuming 5000 steps full range
            
            if self.stepper_controller:
                self.stepper_controller.move_motor('SONY_ZOOM', steps)
            
            self.zoom_level = zoom_percent
            self.logger.debug(f"Zoom set to {zoom_percent}%")
            
        except Exception as e:
            self.logger.error(f"Error setting zoom: {e}")
    
    def set_focus(self, focus_percent: int):
        """
        Set focus distance.
        
        Args:
            focus_percent: Focus distance 0-100% (0=near, 100=far)
        """
        if not self.stepper_controller:
            return
        
        try:
            focus_percent = max(0, min(100, focus_percent))
            steps = int((focus_percent / 100.0) * 3000)  # Assuming 3000 steps full range
            
            if self.stepper_controller:
                self.stepper_controller.move_motor('SONY_FOCUS', steps)
            
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
                self.servo_controller.set_servo_angle('SONY_PAN', angle)
            
            self.pan_angle = angle
            self.logger.debug(f"Pan set to {angle} degrees")
            
        except Exception as e:
            self.logger.error(f"Error setting pan: {e}")
    
    def set_iso(self, iso: int):
        """
        Set ISO (not directly supported, logged for reference).
        
        Args:
            iso: ISO value
        """
        self.iso = iso
        self.logger.debug(f"ISO set to {iso} (manual adjustment required on camera)")
    
    def get_info(self) -> Dict:
        """
        Get camera information.
        
        Returns:
            Dictionary with camera info
        """
        return {
            'name': 'Sony PJ670',
            'type': 'Handycam',
            'resolution': (1920, 1080),
            'fps': 30,
            'zoom_level': self.zoom_level,
            'focus_distance': self.focus_distance,
            'pan_angle': self.pan_angle,
            'iso': self.iso,
            'brightness': self.brightness,
            'lens_type': 'Built-in Zeiss',
        }
    
    def shutdown(self):
        """Release resources."""
        if self.capture:
            self.capture.release()
        self.logger.info("Sony PJ670 shut down")
