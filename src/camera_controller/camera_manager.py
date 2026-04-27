"""
Camera Manager - Manages all cameras in the system.
"""

import threading
from typing import Dict, List, Optional
import time
import numpy as np

from config import CAMERA_TYPES
from camera_controller.sony_pj670 import SonyPJ670Controller
from camera_controller.pi_hq_camera import PiHQCameraController
from camera_controller.webcam_controller import WebcamController
from utils.logger import setup_logger


class CameraManager:
    """
    Manages all cameras in the multi-camera system.
    Coordinates camera capture, settings, and control.
    """
    
    def __init__(self, light_sensors=None, stepper_controller=None, servo_controller=None):
        """
        Initialize camera manager.
        
        Args:
            light_sensors: Light sensor array for auto-exposure
            stepper_controller: Stepper motor controller for zoom/focus
            servo_controller: Servo controller for pan control
        """
        self.logger = setup_logger('CameraManager', 'logs/camera_manager.log')
        self.light_sensors = light_sensors
        self.stepper_controller = stepper_controller
        self.servo_controller = servo_controller
        
        # Camera instances
        self.cameras: Dict[str, any] = {}
        self.primary_camera = CAMERA_TYPES['SONY_PJ670']
        
        # Frame buffers
        self.frames: Dict[str, np.ndarray] = {}
        self.frame_locks: Dict[str, threading.Lock] = {}
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize all cameras.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing cameras...")
            
            # Initialize Sony PJ670
            try:
                self.logger.info("Initializing Sony PJ670...")
                sony = SonyPJ670Controller(self.stepper_controller, self.servo_controller)
                if sony.initialize():
                    self.cameras[CAMERA_TYPES['SONY_PJ670']] = sony
                    self.frame_locks[CAMERA_TYPES['SONY_PJ670']] = threading.Lock()
                    self.logger.info("Sony PJ670 initialized")
                else:
                    self.logger.warning("Sony PJ670 initialization failed")
            except Exception as e:
                self.logger.error(f"Sony PJ670 error: {e}")
            
            # Initialize Pi HQ Camera
            try:
                self.logger.info("Initializing Pi HQ Camera...")
                pi_cam = PiHQCameraController(self.stepper_controller, self.servo_controller)
                if pi_cam.initialize():
                    self.cameras[CAMERA_TYPES['PI_HQ_CAM']] = pi_cam
                    self.frame_locks[CAMERA_TYPES['PI_HQ_CAM']] = threading.Lock()
                    self.logger.info("Pi HQ Camera initialized")
                else:
                    self.logger.warning("Pi HQ Camera initialization failed")
            except Exception as e:
                self.logger.error(f"Pi HQ Camera error: {e}")
            
            # Initialize webcams
            for i, cam_type in enumerate([CAMERA_TYPES['WEBCAM_1'], 
                                          CAMERA_TYPES['WEBCAM_2'],
                                          CAMERA_TYPES['WEBCAM_3']]):
                try:
                    self.logger.info(f"Initializing {cam_type}...")
                    webcam = WebcamController(camera_index=i)
                    if webcam.initialize():
                        self.cameras[cam_type] = webcam
                        self.frame_locks[cam_type] = threading.Lock()
                        self.logger.info(f"{cam_type} initialized")
                    else:
                        self.logger.warning(f"{cam_type} initialization failed")
                except Exception as e:
                    self.logger.error(f"{cam_type} error: {e}")
            
            self.initialized = len(self.cameras) > 0
            self.logger.info(f"Camera manager initialized with {len(self.cameras)} cameras")
            
            return self.initialized
            
        except Exception as e:
            self.logger.error(f"Camera manager initialization error: {e}", exc_info=True)
            return False
    
    def run(self, stop_event: threading.Event):
        """
        Main camera capture loop.
        
        Args:
            stop_event: Event to signal stop
        """
        self.logger.info("Camera capture loop started")
        
        while not stop_event.is_set():
            try:
                # Capture from all cameras
                for cam_id, camera in self.cameras.items():
                    try:
                        frame = camera.capture_frame()
                        if frame is not None:
                            with self.frame_locks[cam_id]:
                                self.frames[cam_id] = frame
                    except Exception as e:
                        self.logger.error(f"Error capturing from {cam_id}: {e}")
                
                # Small delay
                time.sleep(0.001)
                
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
        
        self.logger.info("Camera capture loop stopped")
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get latest frame from a camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Frame as numpy array or None
        """
        if camera_id in self.frames:
            with self.frame_locks[camera_id]:
                return self.frames[camera_id].copy() if camera_id in self.frames else None
        return None
    
    def get_all_frames(self) -> Dict[str, np.ndarray]:
        """
        Get latest frames from all cameras.
        
        Returns:
            Dictionary of camera_id -> frame
        """
        all_frames = {}
        for cam_id in self.cameras.keys():
            frame = self.get_frame(cam_id)
            if frame is not None:
                all_frames[cam_id] = frame
        return all_frames
    
    def set_primary_camera(self, camera_id: str):
        """Set the primary camera for display."""
        if camera_id in self.cameras:
            self.primary_camera = camera_id
            self.logger.info(f"Primary camera set to {camera_id}")
    
    def get_primary_camera(self) -> str:
        """Get the primary camera ID."""
        return self.primary_camera
    
    def set_all_iso(self, iso: int):
        """Set ISO for all cameras that support it."""
        for cam_id, camera in self.cameras.items():
            try:
                if hasattr(camera, 'set_iso'):
                    camera.set_iso(iso)
            except Exception as e:
                self.logger.error(f"Error setting ISO for {cam_id}: {e}")
    
    def get_camera_info(self, camera_id: str) -> Dict:
        """
        Get camera information and current settings.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Dictionary with camera info
        """
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            if hasattr(camera, 'get_info'):
                return camera.get_info()
        return {}
    
    def shutdown(self):
        """Shutdown all cameras."""
        self.logger.info("Shutting down camera manager...")
        for cam_id, camera in self.cameras.items():
            try:
                if hasattr(camera, 'shutdown'):
                    camera.shutdown()
                self.logger.info(f"{cam_id} shut down")
            except Exception as e:
                self.logger.error(f"Error shutting down {cam_id}: {e}")
        self.cameras.clear()
        self.logger.info("Camera manager shut down")
