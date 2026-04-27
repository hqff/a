"""
Frequency Hopper
Implements frequency hopping for anti-jamming RF transmission.
"""

import time
import threading
import random
from typing import List
try:
    from RF24 import RF24, RF24_PA_MAX, RF24_250KBPS
    RF24_AVAILABLE = True
except ImportError:
    RF24_AVAILABLE = False

from config import RF_CONFIG, FREQUENCY_HOPPING
from utils.logger import setup_logger


class FrequencyHopper:
    """
    Frequency hopping controller for anti-jamming RF transmission.
    Uses NRF24L01+ module with channel hopping.
    """
    
    def __init__(self):
        """Initialize frequency hopper."""
        self.logger = setup_logger('FrequencyHopper', 'logs/frequency_hopper.log')
        
        # RF module
        self.radio = None
        
        # Frequency hopping
        self.channels = FREQUENCY_HOPPING['CHANNELS'].copy()
        self.current_channel_idx = 0
        self.hop_interval = FREQUENCY_HOPPING['HOP_INTERVAL']
        
        # Jamming detection
        self.rssi_threshold = FREQUENCY_HOPPING['JAMMING_THRESHOLD']
        self.jamming_detected = False
        
        # Threading
        self.running = False
        self.hop_thread = None
        
        # Status
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize frequency hopper.
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Initializing frequency hopper...")
            
            if not RF24_AVAILABLE:
                self.logger.warning("RF24 library not available, using simulation mode")
                self.initialized = True
                return True
            
            # Initialize NRF24L01+ radio
            # CE pin = GPIO 8, CSN pin = GPIO 7 (via SPI)
            self.radio = RF24(8, 7)
            
            if not self.radio.begin():
                self.logger.error("Failed to initialize NRF24L01+ radio")
                return False
            
            # Configure radio
            self.radio.setPALevel(RF24_PA_MAX)  # Max power
            self.radio.setDataRate(RF24_250KBPS)  # 250kbps for longer range
            self.radio.setPayloadSize(RF_CONFIG['PAYLOAD_SIZE'])
            self.radio.setAutoAck(True)
            self.radio.enableDynamicPayloads()
            
            # Set initial channel
            self.radio.setChannel(self.channels[0])
            
            # Open pipes for TX/RX
            self.radio.openWritingPipe(b'1Node')
            self.radio.openReadingPipe(1, b'2Node')
            
            # Start listening
            self.radio.startListening()
            
            # Start hopping thread
            self.running = True
            self.hop_thread = threading.Thread(target=self._hop_loop, daemon=True)
            self.hop_thread.start()
            
            self.initialized = True
            self.logger.info("Frequency hopper initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Frequency hopper initialization error: {e}", exc_info=True)
            return False
    
    def _hop_loop(self):
        """Frequency hopping loop."""
        self.logger.info("Frequency hopping loop started")
        
        while self.running:
            try:
                # Check for jamming
                if self._detect_jamming():
                    if not self.jamming_detected:
                        self.logger.warning("Jamming detected! Increasing hop rate")
                        self.jamming_detected = True
                        self.hop_interval = FREQUENCY_HOPPING['HOP_INTERVAL'] / 2  # Faster hopping
                else:
                    if self.jamming_detected:
                        self.logger.info("Jamming cleared, resuming normal hopping")
                        self.jamming_detected = False
                        self.hop_interval = FREQUENCY_HOPPING['HOP_INTERVAL']
                
                # Sleep for hop interval
                time.sleep(self.hop_interval)
                
                # Hop to next channel
                self._hop_to_next_channel()
                
            except Exception as e:
                self.logger.error(f"Error in hop loop: {e}")
                time.sleep(1.0)
        
        self.logger.info("Frequency hopping loop stopped")
    
    def _hop_to_next_channel(self):
        """Hop to next channel in sequence."""
        if not self.radio:
            return
        
        # Move to next channel
        self.current_channel_idx = (self.current_channel_idx + 1) % len(self.channels)
        new_channel = self.channels[self.current_channel_idx]
        
        # Set channel
        self.radio.setChannel(new_channel)
        
        self.logger.debug(f"Hopped to channel {new_channel}")
    
    def _detect_jamming(self) -> bool:
        """
        Detect jamming by checking RSSI.
        
        Returns:
            bool: True if jamming detected
        """
        if not self.radio:
            return False
        
        try:
            # Check if carrier is detected (jamming indicator)
            carrier_detected = self.radio.testCarrier()
            
            # In real implementation, would also check RSSI
            # and packet loss rate
            
            return carrier_detected
            
        except Exception as e:
            self.logger.error(f"Error detecting jamming: {e}")
            return False
    
    def send_data(self, data: bytes) -> bool:
        """
        Send data over RF.
        
        Args:
            data: Data to send
            
        Returns:
            bool: True if successful
        """
        if not self.radio:
            return False
        
        try:
            self.radio.stopListening()
            success = self.radio.write(data)
            self.radio.startListening()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
            return False
    
    def receive_data(self) -> bytes:
        """
        Receive data over RF.
        
        Returns:
            Received data or None
        """
        if not self.radio:
            return None
        
        try:
            if self.radio.available():
                payload = self.radio.read(RF_CONFIG['PAYLOAD_SIZE'])
                return bytes(payload)
            return None
            
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    def get_status(self) -> dict:
        """Get current status."""
        return {
            'current_channel': self.channels[self.current_channel_idx],
            'jamming_detected': self.jamming_detected,
            'hop_interval': self.hop_interval,
        }
    
    def shutdown(self):
        """Shutdown frequency hopper."""
        self.logger.info("Shutting down frequency hopper...")
        
        self.running = False
        
        if self.hop_thread:
            self.hop_thread.join(timeout=2.0)
        
        if self.radio:
            self.radio.powerDown()
        
        self.logger.info("Frequency hopper shut down")
