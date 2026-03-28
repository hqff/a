"""
Logitech Brio 100 Webcam Controller
Controls USB webcams for wide-angle monitoring.
"""

import cv2
import numpy as np
from typing import Optional, Dict
from utils.logger import setup_logger


class WebcamController:
    """
    Controller for USB webcams (Logitech Brio 100).
    These are fixed-position cameras for panoramic view.
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize webcam controller.
        
        Args:
            camera_index: Camera device index (0, 1, 2 for three webcams)
        """
        self.logger = setup_logger(f'Webcam{camera_index}', 'logs/webcams.log')
        self.camera_index = camera_index
        
        # Video capture
        self.capture = None
        
        # Current settings
        self.brightness = 50
        self.contrast = 50
        self.saturation = 50
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the webcam.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info(f"Initializing webcam {self.camera_index}...")
            
            # Open webcam
            # Offset by 2 to skip Pi HQ Camera and Sony (usually on /dev/video0, /dev/video1)
            device_id = self.camera_index + 2
            self.capture = cv2.VideoCapture(device_id)
            
            if not self.capture.isOpened():
                self.logger.error(f"Could not open webcam {device_id}")
                return False
            
            # Configure webcam
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # Set initial properties
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            self.capture.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.capture.set(cv2.CAP_PROP_SATURATION, self.saturation)
            
            # Warm up camera
            for _ in range(10):
                self.capture.read()
            
            self.initialized = True
            self.logger.info(f"Webcam {self.camera_index} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Webcam initialization error: {e}", exc_info=True)
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the webcam.
        
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
    
    def set_brightness(self, brightness: int):
        """
        Set brightness.
        
        Args:
            brightness: Brightness 0-100
        """
        try:
            brightness = max(0, min(100, brightness))
            if self.capture:
                self.capture.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
            self.brightness = brightness
        except Exception as e:
            self.logger.error(f"Error setting brightness: {e}")
    
    def set_contrast(self, contrast: int):
        """
        Set contrast.
        
        Args:
            contrast: Contrast 0-100
        """
        try:
            contrast = max(0, min(100, contrast))
            if self.capture:
                self.capture.set(cv2.CAP_PROP_CONTRAST, contrast)
            self.contrast = contrast
        except Exception as e:
            self.logger.error(f"Error setting contrast: {e}")
    
    def get_info(self) -> Dict:
        """
        Get camera information.
        
        Returns:
            Dictionary with camera info
        """
        return {
            'name': f'Logitech Brio 100 #{self.camera_index + 1}',
            'type': 'USB Webcam',
            'resolution': (1920, 1080),
            'fps': 30,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'saturation': self.saturation,
            'position': ['Front', 'Left', 'Right'][self.camera_index] if self.camera_index < 3 else 'Unknown',
        }
    
    def shutdown(self):
        """Release resources."""
        if self.capture:
            self.capture.release()
        self.logger.info(f"Webcam {self.camera_index} shut down")
