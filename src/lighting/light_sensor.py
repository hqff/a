"""
Light Sensor Array
Reads ambient light levels from BH1750 sensors.
"""

import time
from typing import List, Dict
try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

from config import I2C_ADDRESSES
from utils.logger import setup_logger


class LightSensorArray:
    """
    Array of BH1750 light sensors for measuring ambient light.
    """
    
    def __init__(self):
        """Initialize light sensor array."""
        self.logger = setup_logger('LightSensors', 'logs/light_sensors.log')
        
        # I2C bus
        self.bus = None
        
        # Sensor readings (lux)
        self.readings = {
            'front': 0.0,
            'top': 0.0,
            'left': 0.0,
            'right': 0.0,
        }
        
        # Active sensors
        self.active_sensors = []
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize light sensors.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing light sensors...")
            
            if not SMBUS_AVAILABLE:
                self.logger.warning("smbus2 not available, using simulation mode")
                self.initialized = True
                return True
            
            # Open I2C bus (bus 1 on Pi 5)
            self.bus = smbus2.SMBus(1)
            
            # Try to initialize each sensor
            sensors_to_init = [
                ('front', I2C_ADDRESSES['BH1750_FRONT']),
                ('top', I2C_ADDRESSES['BH1750_TOP']),
            ]
            
            for name, addr in sensors_to_init:
                try:
                    # Power on sensor
                    self.bus.write_byte(addr, 0x01)
                    time.sleep(0.01)
                    
                    # Set continuous high-res mode
                    self.bus.write_byte(addr, 0x10)
                    time.sleep(0.12)  # Wait for measurement
                    
                    # Test read
                    data = self.bus.read_i2c_block_data(addr, 0x00, 2)
                    lux = (data[0] << 8 | data[1]) / 1.2
                    
                    self.active_sensors.append((name, addr))
                    self.logger.info(f"BH1750 sensor '{name}' initialized (addr 0x{addr:02X}, {lux:.1f} lux)")
                    
                except Exception as e:
                    self.logger.warning(f"Could not initialize sensor '{name}' at 0x{addr:02X}: {e}")
            
            if len(self.active_sensors) == 0:
                self.logger.warning("No light sensors initialized")
            
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Light sensor initialization error: {e}", exc_info=True)
            return False
    
    def read_sensor(self, address: int) -> float:
        """
        Read light level from a sensor.
        
        Args:
            address: I2C address of sensor
            
        Returns:
            Light level in lux
        """
        try:
            if not self.bus:
                return 0.0
            
            # Read 2 bytes from sensor
            data = self.bus.read_i2c_block_data(address, 0x00, 2)
            
            # Convert to lux
            lux = (data[0] << 8 | data[1]) / 1.2
            
            return lux
            
        except Exception as e:
            self.logger.error(f"Error reading sensor at 0x{address:02X}: {e}")
            return 0.0
    
    def update_readings(self):
        """Update all sensor readings."""
        for name, addr in self.active_sensors:
            lux = self.read_sensor(addr)
            self.readings[name] = lux
    
    def get_average_lux(self) -> float:
        """
        Get average lux from all sensors.
        
        Returns:
            Average lux value
        """
        self.update_readings()
        
        active_readings = [lux for lux in self.readings.values() if lux > 0]
        
        if len(active_readings) > 0:
            return sum(active_readings) / len(active_readings)
        
        return 0.0
    
    def get_all_readings(self) -> Dict[str, float]:
        """
        Get all sensor readings.
        
        Returns:
            Dictionary of sensor_name -> lux
        """
        self.update_readings()
        return self.readings.copy()
    
    def shutdown(self):
        """Shutdown light sensors."""
        self.logger.info("Shutting down light sensors...")
        
        # Power down sensors
        for name, addr in self.active_sensors:
            try:
                if self.bus:
                    self.bus.write_byte(addr, 0x00)  # Power down
            except:
                pass
        
        if self.bus:
            self.bus.close()
        
        self.logger.info("Light sensors shut down")
