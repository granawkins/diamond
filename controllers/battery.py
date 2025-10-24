from .INA219 import INA219

ina219 = INA219(addr=0x42)

def status():
    bus_voltage = ina219.getBusVoltage_V()
    current_ma = ina219.getCurrent_mA()
    power_w = ina219.getPower_W()

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
        "available": True,
        "voltage": round(voltage, 2),
        "current": round(current_a, 3),
        "power": round(power_w, 3),
        "percentage": round(percentage, 1),
        "status": charge_status
    }
