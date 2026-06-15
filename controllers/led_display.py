import argparse
import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


DEFAULT_BUS = 1
DEFAULT_ADDRESS = 0x27
DEFAULT_COLUMNS = 16
DEFAULT_BACKLIGHT = True

BACKLIGHT = 0x08
ENABLE = 0x04
REGISTER_SELECT = 0x01


class LedDisplay:
    """HD44780 character LCD connected through a PCF8574 I2C backpack."""

    def __init__(
        self,
        bus=DEFAULT_BUS,
        address=DEFAULT_ADDRESS,
        columns=DEFAULT_COLUMNS,
        backlight=DEFAULT_BACKLIGHT,
    ):
        self.bus_number = bus
        self.address = address
        self.columns = columns
        self.backlight = backlight
        self.bus = SMBus(bus)
        self.initialize()

    def close(self):
        self.bus.close()

    def _backlight_bit(self):
        return BACKLIGHT if self.backlight else 0

    def _write_raw(self, value):
        self.bus.write_byte(self.address, value | self._backlight_bit())
        time.sleep(0.0002)

    def _pulse(self, value):
        self._write_raw(value | ENABLE)
        time.sleep(0.001)
        self._write_raw(value & ~ENABLE)
        time.sleep(0.001)

    def _write_nibble(self, value, mode=0):
        self._pulse(((value & 0x0F) << 4) | mode)

    def _write_byte(self, value, mode=0):
        self._write_nibble(value >> 4, mode)
        self._write_nibble(value, mode)
        time.sleep(0.003)

    def command(self, value):
        self._write_byte(value, 0)

    def character(self, value):
        self._write_byte(ord(value), REGISTER_SELECT)

    def initialize(self):
        self._write_raw(0)
        time.sleep(0.05)

        for _ in range(3):
            self._write_nibble(0x03)
            time.sleep(0.01)

        self._write_nibble(0x02)
        time.sleep(0.01)

        self.command(0x28)
        self.command(0x08)
        self.clear()
        self.command(0x06)
        self.command(0x0C)

    def clear(self):
        self.command(0x01)
        time.sleep(0.01)

    def set_backlight(self, enabled):
        self.backlight = bool(enabled)
        self._write_raw(0)

    def write_line(self, line, text):
        if line not in (0, 1):
            raise ValueError("line must be 0 or 1")

        self.command(0x80 if line == 0 else 0xC0)
        padded = str(text)[: self.columns].ljust(self.columns)

        for character in padded:
            self.character(character)

    def write(self, line1="", line2=""):
        self.write_line(0, line1)
        self.write_line(1, line2)


def write_display(
    line1="",
    line2="",
    bus=DEFAULT_BUS,
    address=DEFAULT_ADDRESS,
    columns=DEFAULT_COLUMNS,
    backlight=DEFAULT_BACKLIGHT,
    clear=True,
):
    """Write two text lines to Diamond's 16x2 I2C LCD."""

    display = LedDisplay(bus=bus, address=address, columns=columns, backlight=backlight)
    try:
        if clear:
            display.clear()
        display.write(line1, line2)
    finally:
        display.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Write text to Diamond's HD44780-compatible I2C LCD. "
            "Import API: controllers.led_display.write_display(line1, line2)."
        )
    )
    parser.add_argument("line1", nargs="?", default="Diamond Rover")
    parser.add_argument("line2", nargs="?", default="LCD ready")
    parser.add_argument("--bus", type=int, default=DEFAULT_BUS)
    parser.add_argument("--address", type=lambda value: int(value, 0), default=DEFAULT_ADDRESS)
    parser.add_argument("--columns", type=int, default=DEFAULT_COLUMNS)
    parser.add_argument("--no-backlight", action="store_true")
    parser.add_argument("--no-clear", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    write_display(
        args.line1,
        args.line2,
        bus=args.bus,
        address=args.address,
        columns=args.columns,
        backlight=not args.no_backlight,
        clear=not args.no_clear,
    )


if __name__ == "__main__":
    main()

