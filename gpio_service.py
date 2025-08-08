#!/usr/bin/env python3
"""
GPIO Service - Fixed for inverted button logic
"""

import time
import logging
import requests
from functions.config_loader import get_config
import sys
import lgpio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TunedTapDetector:
    def __init__(self):
        self.config = get_config()
        self.pin = int(self.config['GPIO_PIN'])
        self.gpio_handle = None
        
        # Timing thresholds tuned for actual behavior
        self.MAX_TAP_DURATION = 2.0  # Allow up to 2 seconds for a tap
        self.DOUBLE_TAP_WINDOW = 0.8  # Time between tap starts for double tap
        self.LONG_TAP_DURATION = self.config.get('GPIO_LONG_TAP_DURATION', 3.0)  # Long tap threshold
        self.DEBOUNCE_TIME = 0.05
        
        # State tracking - INVERTED LOGIC
        # On this hardware: 0 = not pressed, 1 = pressed
        self.last_state = 0  
        self.press_times = []  # Track press start times
        self.current_press_start = None  # Track current press start time
        self.long_tap_detected = False  # Flag to prevent multiple detections
        
    def init_gpio(self):
        self.gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.gpio_handle, self.pin, lgpio.SET_PULL_UP)
        logger.info(f"GPIO initialized on pin {self.pin}")
        
    def send_event(self, event_type):
        """Send event to Flask app"""
        endpoint_key = f'GPIO_{event_type.upper()}_ENDPOINT'
        if endpoint_key not in self.config:
            logger.error(f"No endpoint configured for {event_type}")
            return
            
        url = f"{self.config['GPIO_FLASK_URL']}{self.config[endpoint_key]}"
        try:
            response = requests.post(url, timeout=2)
            logger.info(f"{event_type} sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send {event_type}: {e}")
    
    def run(self):
        """Main detection loop - with INVERTED button logic"""
        self.init_gpio()
        
        logger.info("Starting tap detection with INVERTED button logic...")
        logger.info(f"Max tap duration: {self.MAX_TAP_DURATION}s")
        logger.info(f"Double tap window: {self.DOUBLE_TAP_WINDOW}s")
        logger.info(f"Long tap duration: {self.LONG_TAP_DURATION}s")
        logger.info("Button logic: 0=not pressed, 1=pressed")
        
        last_change_time = 0
        
        try:
            while True:
                state = lgpio.gpio_read(self.gpio_handle, self.pin)
                now = time.time()
                
                # State change with debounce
                if state != self.last_state and (now - last_change_time) > self.DEBOUNCE_TIME:
                    last_change_time = now
                    
                    # Button pressed (0->1 with INVERTED logic)
                    if self.last_state == 0 and state == 1:
                        logger.debug(f"PRESS detected at {now:.3f}")
                        
                        # Track current press
                        self.current_press_start = now
                        self.long_tap_detected = False
                        
                        # Add this press time
                        self.press_times.append(now)
                        
                        # Keep only recent presses
                        self.press_times = [t for t in self.press_times if now - t < 3.0]
                        
                        # Check for double tap pattern
                        if len(self.press_times) >= 2:
                            # Time between last two presses
                            gap = self.press_times[-1] - self.press_times[-2]
                            logger.debug(f"Gap between presses: {gap:.3f}s")
                            
                            if gap < self.DOUBLE_TAP_WINDOW:
                                logger.info("DOUBLE TAP detected!")
                                self.send_event("double_tap")
                                # Clear press times to avoid multiple detections
                                self.press_times = []
                                self.current_press_start = None
                    
                    # Button released (1->0 with INVERTED logic)
                    elif self.last_state == 1 and state == 0:
                        if self.current_press_start:
                            duration = now - self.current_press_start
                            logger.debug(f"RELEASE detected at {now:.3f}, duration: {duration:.3f}s")
                            
                            # Only process as single tap if:
                            # 1. It wasn't a long tap
                            # 2. Duration is less than max tap duration
                            # 3. We have exactly one press in the buffer
                            if not self.long_tap_detected and duration < self.MAX_TAP_DURATION and len(self.press_times) == 1:
                                # Schedule single tap check
                                single_tap_check_time = now
                            
                            # Always reset the current press start
                            self.current_press_start = None
                    
                    self.last_state = state
                
                # Check for long tap while button is pressed
                if self.current_press_start and not self.long_tap_detected:
                    press_duration = now - self.current_press_start
                    if press_duration >= self.LONG_TAP_DURATION:
                        logger.info("LONG TAP detected!")
                        self.send_event("long_tap")
                        self.long_tap_detected = True
                        # Clear press times to prevent other tap detections
                        self.press_times = []
                
                # Check for single tap timeout
                # If we have one press and enough time has passed without another press
                if len(self.press_times) == 1 and not self.current_press_start and not self.long_tap_detected:
                    time_since_press = now - self.press_times[0]
                    if time_since_press > self.DOUBLE_TAP_WINDOW:
                        logger.info("SINGLE TAP detected!")
                        self.send_event("single_tap")
                        self.press_times = []
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Stopped")
        finally:
            if self.gpio_handle:
                lgpio.gpiochip_close(self.gpio_handle)

def main():
    import time
    
    # Wait for system startup
    startup_delay = float(get_config()['GPIO_STARTUP_DELAY'])
    logger.info(f"Waiting {startup_delay}s for startup...")
    time.sleep(startup_delay)
    
    if "--debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)
        
    detector = TunedTapDetector()
    detector.run()

if __name__ == "__main__":
    main()
