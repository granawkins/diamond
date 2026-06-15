import argparse
import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


DEFAULT_BUS = 1
DEFAULT_ADDRESS = 0x42
DEFAULT_EMPTY_VOLTAGE = 6.0
DEFAULT_FULL_VOLTAGE = 8.4

REG_CONFIG = 0x00
REG_SHUNT_VOLTAGE = 0x01
REG_BUS_VOLTAGE = 0x02
REG_POWER = 0x03
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05

CONFIG_32V_2A = 0x399F
CALIBRATION_VALUE = 4096
CURRENT_LSB_MA = 0.1
POWER_LSB_MW = 2.0


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def battery_percent(voltage, empty_voltage=DEFAULT_EMPTY_VOLTAGE, full_voltage=DEFAULT_FULL_VOLTAGE):
    if full_voltage <= empty_voltage:
        raise ValueError("full_voltage must be greater than empty_voltage")

    return clamp(((voltage - empty_voltage) / (full_voltage - empty_voltage)) * 100)


class WaveshareHat:
    """Reader for Waveshare UPS HAT telemetry exposed through INA219."""

    def __init__(self, bus=DEFAULT_BUS, address=DEFAULT_ADDRESS):
        self.bus_number = bus
        self.address = address
        self.bus = SMBus(bus)
        self.configure()

    def close(self):
        self.bus.close()

    def _write_register(self, register, value):
        self.bus.write_i2c_block_data(
            self.address,
            register,
            [(value >> 8) & 0xFF, value & 0xFF],
        )

    def _read_register(self, register, signed=False):
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        value = (data[0] << 8) | data[1]

        if signed and value & 0x8000:
            value -= 0x10000

        return value

    def configure(self):
        self._write_register(REG_CONFIG, CONFIG_32V_2A)
        self._write_register(REG_CALIBRATION, CALIBRATION_VALUE)
        time.sleep(0.01)

    def bus_voltage(self):
        raw = self._read_register(REG_BUS_VOLTAGE)
        return ((raw >> 3) * 4) / 1000

    def shunt_voltage(self):
        return self._read_register(REG_SHUNT_VOLTAGE, signed=True) * 0.00001

    def current(self):
        self._write_register(REG_CALIBRATION, CALIBRATION_VALUE)
        return self._read_register(REG_CURRENT, signed=True) * CURRENT_LSB_MA / 1000

    def power(self):
        self._write_register(REG_CALIBRATION, CALIBRATION_VALUE)
        return self._read_register(REG_POWER) * POWER_LSB_MW / 1000

    def battery(self, empty_voltage=DEFAULT_EMPTY_VOLTAGE, full_voltage=DEFAULT_FULL_VOLTAGE):
        voltage = self.bus_voltage()
        return {
            "voltage": voltage,
            "percent": battery_percent(voltage, empty_voltage, full_voltage),
            "current": self.current(),
            "power": self.power(),
            "shunt_voltage": self.shunt_voltage(),
        }


def read_battery(
    bus=DEFAULT_BUS,
    address=DEFAULT_ADDRESS,
    empty_voltage=DEFAULT_EMPTY_VOLTAGE,
    full_voltage=DEFAULT_FULL_VOLTAGE,
):
    """Read UPS HAT battery telemetry as a dict."""

    hat = WaveshareHat(bus=bus, address=address)
    try:
        return hat.battery(empty_voltage=empty_voltage, full_voltage=full_voltage)
    finally:
        hat.close()


def format_battery(battery):
    return (
        f"battery={battery['percent']:.0f}% "
        f"voltage={battery['voltage']:.2f}V "
        f"current={battery['current']:.3f}A "
        f"power={battery['power']:.3f}W"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Read Diamond's Waveshare UPS HAT battery telemetry. "
            "Import API: controllers.waveshare_hat.read_battery() returns a dict."
        )
    )
    parser.add_argument("--bus", type=int, default=DEFAULT_BUS)
    parser.add_argument("--address", type=lambda value: int(value, 0), default=DEFAULT_ADDRESS)
    parser.add_argument("--empty-voltage", type=float, default=DEFAULT_EMPTY_VOLTAGE)
    parser.add_argument("--full-voltage", type=float, default=DEFAULT_FULL_VOLTAGE)
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    return parser.parse_args()


def main():
    args = parse_args()
    battery = read_battery(
        bus=args.bus,
        address=args.address,
        empty_voltage=args.empty_voltage,
        full_voltage=args.full_voltage,
    )

    if args.json:
        import json

        print(json.dumps(battery, sort_keys=True))
    else:
        print(format_battery(battery))


if __name__ == "__main__":
    main()

