#     Copyright (c) 2018 Jouko Strömmer
#     Copyright (c) 2017 Waveshare
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from PIL import Image

import time

# SPI always goes through spidev (more reliable than gpiozero SPIDevice).
try:
    import spidev
except ImportError:
    spidev = None

# GPIO: prefer gpiozero (lgpio pin factory on modern Raspberry Pi OS),
# fall back to RPi.GPIO when available (works on Zero 2 W / Pi 4, not Pi 5).
_gpiozero_ok = False
_rpi_gpio_ok = False
OutputDevice = None
InputDevice = None
rpiGPIO = None

try:
    from gpiozero import OutputDevice, InputDevice
    _gpiozero_ok = True
except ImportError:
    pass

try:
    import RPi.GPIO as rpiGPIO
    _rpi_gpio_ok = True
except ImportError:
    pass
except RuntimeError as e:
    # RPi.GPIO imported but cannot talk to hardware (e.g. Pi 5 / wrong platform).
    print(str(e))


def gpio_backend_name():
    if _gpiozero_ok:
        return "gpiozero"
    if _rpi_gpio_ok:
        return "RPi.GPIO"
    return None


class SpiDev:
    """Thin wrapper around spidev for Waveshare / IT8951 transfers."""

    def __init__(self, bus=0, device=0):
        if spidev is None:
            raise RuntimeError(
                "spidev is required for SPI e-ink panels. "
                "Install the spidev package and enable SPI (raspi-config)."
            )
        self.spi = spidev.SpiDev(bus, device)

    def writebytes(self, data):
        self.spi.writebytes(data)

    def readbytes(self, n):
        return self.spi.readbytes(n)

    def setSpeed(self, hz):
        self.spi.max_speed_hz = hz

    def setMode(self, mode):
        self.spi.mode = mode

    def setNoCs(self, value):
        self.spi.no_cs = value


class GPIO:
    """GPIO helpers shared by Waveshare drivers.

    Uses gpiozero when available, otherwise RPi.GPIO. Constants mirror
    RPi.GPIO names so driver code stays portable.
    """

    OUT = "OUT"
    IN = "IN"
    BCM = "BCM"
    LOW = 0
    HIGH = 1

    pins = {}
    _backend = None

    @staticmethod
    def _ensure_backend():
        if GPIO._backend:
            return GPIO._backend
        if _gpiozero_ok:
            GPIO._backend = "gpiozero"
            return GPIO._backend
        if _rpi_gpio_ok:
            GPIO._backend = "RPi.GPIO"
            return GPIO._backend
        raise RuntimeError(
            "No GPIO backend available. Install gpiozero (and python3-lgpio "
            "on Raspberry Pi OS) or RPi.GPIO, and run with permission to "
            "access GPIO."
        )

    @staticmethod
    def setmode(value):
        backend = GPIO._ensure_backend()
        if backend == "RPi.GPIO":
            if value == GPIO.BCM:
                rpiGPIO.setmode(rpiGPIO.BCM)
            else:
                rpiGPIO.setmode(value)

    @staticmethod
    def setwarnings(value):
        backend = GPIO._ensure_backend()
        if backend == "RPi.GPIO":
            rpiGPIO.setwarnings(value)

    @staticmethod
    def setup(pin, ioType):
        backend = GPIO._ensure_backend()
        if backend == "gpiozero":
            if ioType == GPIO.OUT:
                GPIO.pins[str(pin)] = OutputDevice(pin)
            else:
                GPIO.pins[str(pin)] = InputDevice(pin)
            return

        GPIO.pins[str(pin)] = False
        if ioType == GPIO.OUT:
            rpiGPIO.setup(pin, rpiGPIO.OUT)
        else:
            rpiGPIO.setup(pin, rpiGPIO.IN)

    @staticmethod
    def input(pinNo):
        pin = GPIO.pins[str(pinNo)]
        if pin is False:
            return rpiGPIO.input(pinNo)
        return pin.value

    @staticmethod
    def output(pinNo, value):
        pin = GPIO.pins[str(pinNo)]
        if pin is False:
            rpiGPIO.output(pinNo, value)
        else:
            pin.on() if value == 1 else pin.off()


class DisplayDriver(ABC):
    """Abstract base class for a display driver - be it Waveshare e-Paper, PaPiRus, OLED..."""

    # override these if needed
    white = 255
    black = 0

    def __init__(self):
        super().__init__()
        self.name = None
        self.width = None
        self.height = None
        self.colors = None
        self.type = None
        self.supports_partial = None
        self.partial_refresh = None
        self.supports_1bpp = None
        self.enable_1bpp = None
        self.align_1bpp_width = None
        self.align_1bpp_height = None
        self.supports_multi_draw = None

    @abstractmethod
    def init(self, **kwargs):
        """Initialize the display"""
        pass

    @abstractmethod
    def draw(self, x, y, image):
        """Draw an image object on the display at (x,y)"""
        pass

    def scrub(self, fillsize=16):
        """Scrub display - only works properly with partial refresh"""
        self.fill(self.black, fillsize=fillsize)
        self.fill(self.white, fillsize=fillsize)

    def fill(self, color, fillsize):
        """Slow fill routine"""
        image = Image.new('1', (fillsize, self.height), color)
        for x in range(0, self.height, fillsize):
            self.draw(x, 0, image)

    def clear(self):
        """Clears the display"""
        image = Image.new('1', (self.height, self.width), self.black)
        self.draw(0, 0, image)
        image = Image.new('1', (self.height, self.width), self.white)
        self.draw(0, 0, image)


class SpecialDriver(DisplayDriver):
    """Drivers that don't control hardware"""
    default_width = 640
    default_height = 384

    def __init__(self, name, width, height):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height
        self.type = 'Dummy display driver'

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def draw(self, x, y, image):
        pass

    def scrub(self, fillsize=16):
        pass


class Dummy(SpecialDriver):
    """Dummy display driver - does not do anything"""

    def __init__(self):
        super().__init__(name='No-op driver', width=self.default_width, height=self.default_height)

    def init(self, **kwargs):
        pass

    def draw(self, x, y, image):
        pass


class Bitmap(SpecialDriver):
    """Output a bitmap for each frame - overwrite old ones"""

    def __init__(self, maxfiles=5, file_format="png"):
        super().__init__(name="Bitmap output driver", width=self.default_width, height=self.default_height, )
        self.maxfiles = maxfiles
        self.current_frame = 0
        self.frame_buffer = None
        self.file_format = file_format

    def init(self, **kwargs):
        self.frame_buffer = Image.new('1', (self.width, self.height), 255)
        self.current_frame = 0

    def draw(self, x, y, image):
        self.frame_buffer.paste(image, box=(x, y))
        self.frame_buffer.save("bitmap_frame_{}.{}".format(self.current_frame, self.file_format))
        self.current_frame = (self.current_frame + 1) % self.maxfiles


class WaveshareEPD(DisplayDriver):
    """Base class for Waveshare displays with common code for all - the 'epdif.py'
    - 1.54" , 1.54" B , 1.54" C
    - 2.13" , 2.13" B
    - 2.7"  , 2.7" B
    - 2.9"  , 2.9" B
    - 4.2"  , 4.2" B
    - 7.5"  , 7.5" B
    """

    # Common commands
    GET_STATUS = 0x71

    # These pins are common across all models
    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24

    # Some models implement rotation in their code
    ROTATE_0 = 0x00
    ROTATE_90 = 0x01
    ROTATE_180 = 0x02
    ROTATE_270 = 0x03

    # SPI methods

    @staticmethod
    def epd_digital_write(pin, value):
        GPIO.output(pin, value)

    @staticmethod
    def epd_digital_read(pin):
        return GPIO.input(pin)

    @staticmethod
    def epd_delay_ms(delaytime):
        time.sleep(float(delaytime) / 1000.0)

    def spi_transfer(self, data):
        self.SPI.writebytes(data)

    def epd_init(self, includeDcPin=True):
        backend = GPIO._ensure_backend()
        print("GPIO backend: {} (SPI via spidev)".format(backend))

        # SpiDev init must come first, otherwise CS_PIN read conflicts
        # will sometimes occur during startup.
        self.SPI = SpiDev()
        self.SPI.setSpeed(2000000)
        self.SPI.setMode(0b00)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        if includeDcPin:
            GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BUSY_PIN, GPIO.IN)
        return 0

    # Basic functionality

    def __init__(self, name, width, height):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height
        self.type = 'Waveshare e-Paper'

    def digital_write(self, pin, value):
        self.epd_digital_write(pin, value)

    def digital_read(self, pin):
        return self.epd_digital_read(pin)

    def delay_ms(self, delaytime):
        self.epd_delay_ms(delaytime)

    def send_command(self, command):
        self.digital_write(self.DC_PIN, GPIO.LOW)
        # the parameter type is list but not int
        # so use [command] instead of command
        self.spi_transfer([command])

    def send_data(self, data):
        self.digital_write(self.DC_PIN, GPIO.HIGH)
        # the parameter type is list but not int
        # so use [data] instead of data
        self.spi_transfer([data])

    def send_data_multi(self, dataArray):
        self.digital_write(self.DC_PIN, GPIO.HIGH)
        max_transfer_size = 4096
        for i in range(0, len(dataArray), max_transfer_size):
            self.spi_transfer(dataArray[i: i + max_transfer_size])

    def reset(self):
        self.digital_write(self.RST_PIN, GPIO.LOW)
        self.delay_ms(200)
        self.digital_write(self.RST_PIN, GPIO.HIGH)
        self.delay_ms(200)

    def init(self, **kwargs):
        pass

    def draw(self, x, y, image):
        pass
