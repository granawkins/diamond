"""
Battery monitoring using INA219 current/voltage sensor.
Reads battery voltage, current, and power over I2C.
"""
import time
import board
import busio
from adafruit_ina219 import INA219

class BatteryMonitor:
    def __init__(self, i2c=None):
        """
        Initialize INA219 battery monitor.
        
        Args:
            i2c: Optional I2C bus object. If None, creates new one.
        """
        if i2c is None:
            i2c = busio.I2C(board.SCL, board.SDA)
        
        self.ina219 = INA219(i2c)
        
    def get_voltage(self):
        """Get battery voltage in volts."""
        return self.ina219.bus_voltage + self.ina219.shunt_voltage
    
    def get_current(self):
        """Get current draw in milliamps."""
        return self.ina219.current
    
    def get_power(self):
        """Get power consumption in milliwatts."""
        return self.ina219.power
    
    def get_battery_status(self):
        """
        Get complete battery status.
        
        Returns:
            dict: Battery voltage, current, power, and estimated percentage
        """
        voltage = self.get_voltage()
        current = self.get_current()
        power = self.get_power()
        
        # For 3S Li-ion: 12.6V full, 9.0V empty (3 cells × 4.2V/3.0V)
        percentage = self._estimate_percentage(voltage)
        
        return {
            'voltage': voltage,
            'current': current,
            'power': power,
            'percentage': percentage
        }
    
    def _estimate_percentage(self, voltage):
        """
        Estimate battery percentage from voltage.
        Based on typical 3S Li-ion discharge curve.
        """
        # 3S Li-ion voltage ranges
        FULL_VOLTAGE = 12.6  # 3 × 4.2V
        EMPTY_VOLTAGE = 9.0  # 3 × 3.0V
        
        if voltage >= FULL_VOLTAGE:
            return 100
        elif voltage <= EMPTY_VOLTAGE:
            return 0
        else:
            # Linear approximation (actual curve is non-linear)
            percentage = ((voltage - EMPTY_VOLTAGE) / 
                         (FULL_VOLTAGE - EMPTY_VOLTAGE)) * 100
            return round(percentage, 1)
    
    def print_status(self):
        """Print current battery status to console."""
        status = self.get_battery_status()
        print(f"Battery Status:")
        print(f"  Voltage: {status['voltage']:.2f}V")
        print(f"  Current: {status['current']:.1f}mA")
        print(f"  Power: {status['power']:.1f}mW")
        print(f"  Charge: {status['percentage']:.1f}%")


if __name__ == "__main__":
    # Test battery monitoring
    monitor = BatteryMonitor()
    
    print("Battery Monitor Test")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            monitor.print_status()
            print()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting...")
