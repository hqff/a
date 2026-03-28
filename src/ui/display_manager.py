"""
Display Manager
Manages the 5" touchscreen display and user interface.
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Optional
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from config import DISPLAY, UI_CONFIG, OVERLAY_INFO, CAMERA_TYPES
from utils.logger import setup_logger


class DisplayManager:
    """
    Manages the touchscreen display and user interface.
    """
    
    def __init__(self, camera_manager, stream_processor, system_monitor):
        """
        Initialize display manager.
        
        Args:
            camera_manager: Camera manager instance
            stream_processor: Stream processor instance
            system_monitor: System monitor instance
        """
        self.logger = setup_logger('DisplayManager', 'logs/display.log')
        self.camera_manager = camera_manager
        self.stream_processor = stream_processor
        self.system_monitor = system_monitor
        
        # Pygame display
        self.screen = None
        self.clock = None
        
        # UI state
        self.show_multi_view = False
        self.show_overlay = True
        self.selected_camera = None
        
        # Events
        self.events = []
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize display.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing display manager...")
            
            if not PYGAME_AVAILABLE:
                self.logger.warning("pygame not available, display disabled")
                self.initialized = True
                return True
            
            # Initialize pygame
            pygame.init()
            
            # Create display
            if DISPLAY['FULLSCREEN']:
                self.screen = pygame.display.set_mode(
                    (DISPLAY['WIDTH'], DISPLAY['HEIGHT']),
                    pygame.FULLSCREEN
                )
            else:
                self.screen = pygame.display.set_mode(
                    (DISPLAY['WIDTH'], DISPLAY['HEIGHT'])
                )
            
            pygame.display.set_caption("Multi-Camera Gimbal System")
            
            # Create clock for FPS control
            self.clock = pygame.time.Clock()
            
            # Hide mouse cursor in fullscreen
            if DISPLAY['FULLSCREEN']:
                pygame.mouse.set_visible(False)
            
            self.initialized = True
            self.logger.info("Display manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Display initialization error: {e}", exc_info=True)
            return False
    
    def update(self):
        """Update display with latest frames."""
        if not self.initialized or not PYGAME_AVAILABLE:
            return
        
        try:
            # Handle events
            self._handle_events()
            
            # Get frame to display
            if self.show_multi_view:
                frame = self.stream_processor.get_multi_view()
            else:
                frame = self.stream_processor.get_main_view()
            
            if frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Add overlay if enabled
                if self.show_overlay:
                    frame_rgb = self._add_overlay(frame_rgb)
                
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(
                    np.transpose(frame_rgb, (1, 0, 2))
                )
                
                # Display
                self.screen.blit(frame_surface, (0, 0))
                pygame.display.flip()
            
            # Control FPS
            self.clock.tick(DISPLAY['FPS'])
            
        except Exception as e:
            self.logger.error(f"Error updating display: {e}")
    
    def _handle_events(self):
        """Handle pygame events."""
        self.events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.events.append({'type': 'emergency_stop'})
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.events.append({'type': 'emergency_stop'})
                elif event.key == pygame.K_m:
                    self.show_multi_view = not self.show_multi_view
                elif event.key == pygame.K_o:
                    self.show_overlay = not self.show_overlay
                elif event.key == pygame.K_1:
                    self.events.append({'type': 'mode_change', 'mode': 'AUTO'})
                elif event.key == pygame.K_2:
                    self.events.append({'type': 'mode_change', 'mode': 'MANUAL'})
                elif event.key == pygame.K_3:
                    self.events.append({'type': 'mode_change', 'mode': 'NIGHT'})
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle touch/click
                x, y = event.pos
                self._handle_touch(x, y)
    
    def _handle_touch(self, x: int, y: int):
        """Handle touch/click event."""
        # If in multi-view, detect which camera was clicked
        # Simplified implementation
        pass
    
    def _add_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Add information overlay to frame."""
        try:
            # Get system info
            health = self.system_monitor.get_health_status()
            primary_cam = self.camera_manager.get_primary_camera()
            cam_info = self.camera_manager.get_camera_info(primary_cam)
            
            # Create overlay
            overlay = frame.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            color = UI_CONFIG['COLOR_TEXT']
            
            # Top-left: Camera info
            y_offset = 30
            lines = [
                f"Camera: {cam_info.get('name', 'Unknown')}",
                f"Resolution: {cam_info.get('resolution', 'N/A')}",
                f"FPS: {cam_info.get('fps', 0)}",
            ]
            
            if 'iso' in cam_info:
                lines.append(f"ISO: {cam_info['iso']}")
            if 'zoom_level' in cam_info and cam_info['zoom_level'] is not None:
                lines.append(f"Zoom: {cam_info['zoom_level']}%")
            if 'lens_type' in cam_info:
                lines.append(f"Lens: {cam_info['lens_type']}")
            
            for line in lines:
                cv2.putText(overlay, line, (10, y_offset), font, font_scale, color, thickness)
                y_offset += 25
            
            # Top-right: System info
            y_offset = 30
            x_offset = DISPLAY['WIDTH'] - 200
            
            sys_lines = [
                f"Temp: {health['temperature']:.1f}C",
                f"Battery: {health['battery_voltage']:.1f}V",
                f"Uptime: {health['uptime']/60:.1f}min",
            ]
            
            for line in sys_lines:
                cv2.putText(overlay, line, (x_offset, y_offset), font, font_scale, color, thickness)
                y_offset += 25
            
            # Bottom: Controls hint
            hint = "M: Multi-view | O: Overlay | ESC: Exit"
            cv2.putText(overlay, hint, (10, DISPLAY['HEIGHT'] - 10), 
                       font, font_scale, UI_CONFIG['COLOR_SECONDARY'], thickness)
            
            return overlay
            
        except Exception as e:
            self.logger.error(f"Error adding overlay: {e}")
            return frame
    
    def get_events(self) -> List[Dict]:
        """Get UI events."""
        events = self.events.copy()
        self.events = []
        return events
    
    def shutdown(self):
        """Shutdown display manager."""
        self.logger.info("Shutting down display manager...")
        
        if PYGAME_AVAILABLE:
            pygame.quit()
        
        self.logger.info("Display manager shut down")
