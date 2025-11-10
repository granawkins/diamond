from .INA219 import INA219

class Battery:
    def __init__(self, mode="SIM"):
        self.mode = mode
        if mode == "LIVE":
            self.ina219 = INA219(addr=0x42)
        else:
            self.ina219 = None

    def status(self):
        if self.ina219 is not None:
            bus_voltage = self.ina219.getBusVoltage_V()
            current_ma = self.ina219.getCurrent_mA()
            power_w = self.ina219.getPower_W()

            voltage = bus_voltage
            current_a = current_ma / 1000

            # Two 18650 cells: 6.0V (empty) to 8.4V (full)
            min_voltage = 6.0
            max_voltage = 8.4
            percentage = max(0, min(100, ((voltage - min_voltage) / (max_voltage - min_voltage)) * 100))

            # Negative current = discharging, positive = charging
            if current_a < -0.05:
                charge_status = "discharging"
            elif current_a > 0.05:
                charge_status = "charging"
            else:
                charge_status = "idle"

            return {
                "voltage": round(voltage, 2),
                "current": round(current_a, 3),
                "power": round(power_w, 3),
                "percentage": round(percentage, 1),
                "status": charge_status
            }

        return {
            "voltage": 0,
            "current": 0,
            "power": 0,
            "percentage": 0,
            "status": "offline"
        }
