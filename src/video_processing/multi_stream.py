"""
Multi-Stream Video Processor
Processes and combines multiple camera streams.
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Optional
from config import DISPLAY, MULTI_VIEW_LAYOUT, VIDEO_ENCODING
from utils.logger import setup_logger
from utils.helpers import FPSCounter


class MultiStreamProcessor:
    """
    Processes multiple camera streams and creates combined views.
    """
    
    def __init__(self, camera_manager):
        """
        Initialize multi-stream processor.
        
        Args:
            camera_manager: Camera manager instance
        """
        self.logger = setup_logger('MultiStreamProcessor', 'logs/video_processor.log')
        self.camera_manager = camera_manager
        
        # Output frames
        self.main_view = None
        self.multi_view = None
        self.view_lock = threading.Lock()
        
        # Settings
        self.streaming_mode = False
        self.layout = "PICTURE_IN_PICTURE"
        
        # Performance
        self.fps_counter = FPSCounter()
        
        # Status
        self.initialized = False
        self.running = False
    
    def initialize(self) -> bool:
        """
        Initialize video processor.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing video processor...")
            
            self.initialized = True
            self.logger.info("Video processor initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Video processor initialization error: {e}", exc_info=True)
            return False
    
    def run(self, stop_event: threading.Event):
        """
        Main video processing loop.
        
        Args:
            stop_event: Event to signal stop
        """
        self.logger.info("Video processing loop started")
        self.running = True
        
        while not stop_event.is_set() and self.running:
            try:
                # Get frames from all cameras
                frames = self.camera_manager.get_all_frames()
                
                if len(frames) > 0:
                    # Create main view (primary camera)
                    primary_cam = self.camera_manager.get_primary_camera()
                    if primary_cam in frames:
                        main_frame = frames[primary_cam].copy()
                    else:
                        # Use first available camera
                        main_frame = list(frames.values())[0].copy()
                    
                    # Create multi-view
                    multi_frame = self._create_multi_view(frames)
                    
                    # Update output
                    with self.view_lock:
                        self.main_view = main_frame
                        self.multi_view = multi_frame
                    
                    # Update FPS
                    fps = self.fps_counter.tick()
                    if int(time.time()) % 10 == 0:  # Log every 10 seconds
                        self.logger.debug(f"Processing at {fps:.1f} FPS")
                
                time.sleep(0.001)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
        
        self.logger.info("Video processing loop stopped")
    
    def _create_multi_view(self, frames: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Create multi-camera view.
        
        Args:
            frames: Dictionary of camera_id -> frame
            
        Returns:
            Combined view frame
        """
        try:
            if len(frames) == 0:
                return np.zeros((480, 800, 3), dtype=np.uint8)
            
            # Picture-in-picture layout
            if self.layout == "PICTURE_IN_PICTURE":
                return self._create_pip_view(frames)
            
            # Grid layout
            elif self.layout == "GRID_2x2":
                return self._create_grid_view(frames, rows=2, cols=2)
            
            elif self.layout == "GRID_2x3":
                return self._create_grid_view(frames, rows=2, cols=3)
            
            else:
                return self._create_pip_view(frames)
            
        except Exception as e:
            self.logger.error(f"Error creating multi-view: {e}")
            return np.zeros((480, 800, 3), dtype=np.uint8)
    
    def _create_pip_view(self, frames: Dict[str, np.ndarray]) -> np.ndarray:
        """Create picture-in-picture view."""
        # Create output canvas
        output = np.zeros((DISPLAY['HEIGHT'], DISPLAY['WIDTH'], 3), dtype=np.uint8)
        
        # Get primary camera frame
        primary_cam = self.camera_manager.get_primary_camera()
        if primary_cam in frames:
            main_frame = frames[primary_cam]
            
            # Resize to fit display
            main_resized = cv2.resize(main_frame, (DISPLAY['WIDTH'], DISPLAY['HEIGHT']))
            output = main_resized
            
            # Add thumbnails of other cameras
            thumbnail_width = 200
            thumbnail_height = 150
            x_offset = 10
            y_offset = 10
            
            for cam_id, frame in frames.items():
                if cam_id != primary_cam:
                    # Resize to thumbnail
                    thumbnail = cv2.resize(frame, (thumbnail_width, thumbnail_height))
                    
                    # Place on output
                    try:
                        output[y_offset:y_offset+thumbnail_height, 
                              x_offset:x_offset+thumbnail_width] = thumbnail
                        
                        # Draw border
                        cv2.rectangle(output, 
                                    (x_offset, y_offset),
                                    (x_offset+thumbnail_width, y_offset+thumbnail_height),
                                    (0, 255, 0), 2)
                        
                        # Move to next position
                        y_offset += thumbnail_height + 10
                        
                        if y_offset + thumbnail_height > DISPLAY['HEIGHT']:
                            y_offset = 10
                            x_offset += thumbnail_width + 10
                    except:
                        pass
        
        return output
    
    def _create_grid_view(self, frames: Dict[str, np.ndarray], rows: int, cols: int) -> np.ndarray:
        """Create grid view."""
        cell_width = DISPLAY['WIDTH'] // cols
        cell_height = DISPLAY['HEIGHT'] // rows
        
        output = np.zeros((DISPLAY['HEIGHT'], DISPLAY['WIDTH'], 3), dtype=np.uint8)
        
        frame_list = list(frames.values())
        
        idx = 0
        for row in range(rows):
            for col in range(cols):
                if idx < len(frame_list):
                    frame = frame_list[idx]
                    
                    # Resize to cell size
                    resized = cv2.resize(frame, (cell_width, cell_height))
                    
                    # Place in grid
                    y_start = row * cell_height
                    y_end = y_start + cell_height
                    x_start = col * cell_width
                    x_end = x_start + cell_width
                    
                    output[y_start:y_end, x_start:x_end] = resized
                    
                    # Draw grid lines
                    cv2.rectangle(output, (x_start, y_start), (x_end-1, y_end-1), (100, 100, 100), 1)
                    
                    idx += 1
        
        return output
    
    def get_main_view(self) -> Optional[np.ndarray]:
        """Get main camera view."""
        with self.view_lock:
            return self.main_view.copy() if self.main_view is not None else None
    
    def get_multi_view(self) -> Optional[np.ndarray]:
        """Get multi-camera view."""
        with self.view_lock:
            return self.multi_view.copy() if self.multi_view is not None else None
    
    def set_layout(self, layout: str):
        """Set multi-view layout."""
        self.layout = layout
        self.logger.info(f"Layout changed to {layout}")
    
    def set_streaming_mode(self, enabled: bool):
        """Set streaming mode (lower quality for bandwidth)."""
        self.streaming_mode = enabled
        self.logger.info(f"Streaming mode: {'enabled' if enabled else 'disabled'}")
    
    def shutdown(self):
        """Shutdown video processor."""
        self.logger.info("Shutting down video processor...")
        self.running = False
        self.logger.info("Video processor shut down")
