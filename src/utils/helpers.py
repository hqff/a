"""
Helper utilities for system monitoring and common functions.
"""

import time
import threading
from typing import Dict
try:
    import gpiozero
except ImportError:
    gpiozero = None

from utils.logger import setup_logger


class SystemMonitor:
    """Monitor system health (temperature, voltage, etc.)."""
    
    def __init__(self):
        self.logger = setup_logger('SystemMonitor', 'logs/system_monitor.log')
        self.running = False
        self.thread = None
        
        # Health metrics
        self.temperature = 0.0
        self.battery_voltage = 14.8
        self.current_draw = 0.0
        self.uptime = 0.0
        self.start_time = time.time()
        
        # CPU temperature monitor
        self.cpu_temp = None
        if gpiozero:
            try:
                self.cpu_temp = gpiozero.CPUTemperature()
            except Exception as e:
                self.logger.warning(f"Could not initialize CPU temperature monitor: {e}")
    
    def start(self):
        """Start monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("System monitor started")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Update temperature
                if self.cpu_temp:
                    self.temperature = self.cpu_temp.temperature
                
                # Update uptime
                self.uptime = time.time() - self.start_time
                
                # Log status periodically (every 60 seconds)
                if int(self.uptime) % 60 == 0:
                    self.logger.info(
                        f"Status: Temp={self.temperature:.1f}°C, "
                        f"Battery={self.battery_voltage:.1f}V, "
                        f"Uptime={self.uptime/60:.1f}min"
                    )
                
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(1.0)
    
    def get_health_status(self) -> Dict:
        """
        Get current health status.
        
        Returns:
            Dictionary with health metrics
        """
        return {
            'temperature': self.temperature,
            'battery_voltage': self.battery_voltage,
            'current_draw': self.current_draw,
            'uptime': self.uptime,
        }
    
    def shutdown(self):
        """Stop monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.info("System monitor stopped")


def map_value(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    Map a value from one range to another.
    
    Args:
        value: Input value
        in_min: Input range minimum
        in_max: Input range maximum
        out_min: Output range minimum
        out_max: Output range maximum
        
    Returns:
        Mapped value
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def constrain(value: float, min_val: float, max_val: float) -> float:
    """
    Constrain value to a range.
    
    Args:
        value: Input value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Constrained value
    """
    return max(min_val, min(max_val, value))


class FPSCounter:
    """Count frames per second."""
    
    def __init__(self, avg_over: int = 30):
        """
        Initialize FPS counter.
        
        Args:
            avg_over: Number of frames to average over
        """
        self.avg_over = avg_over
        self.frame_times = []
        self.last_time = time.time()
    
    def tick(self) -> float:
        """
        Record a frame and return current FPS.
        
        Returns:
            Current FPS
        """
        current_time = time.time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time
        
        # Keep only recent frames
        if len(self.frame_times) > self.avg_over:
            self.frame_times.pop(0)
        
        # Calculate FPS
        if len(self.frame_times) > 0:
            avg_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_time if avg_time > 0 else 0.0
        return 0.0
