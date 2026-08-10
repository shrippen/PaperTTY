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
"""EXPERIMENTAL drivers for newer Waveshare panels.

Ported from the vendor library at
https://github.com/waveshareteam/e-Paper (RaspberryPi_JetsonNano/python).

These drivers were added with AI assistance ("vibe coded") and have **not**
been tested on real hardware. Expect breakage. Prefer the older drivers in
`drivers_partial.py` / `drivers_full.py` / … when a matching revision exists.

The controllers used by these panels expect a full frame on every update, even
when doing a partial (fast) refresh, whereas PaperTTY hands `draw()` arbitrary
sub-regions of the screen. `WaveshareBuffered` bridges the two by keeping a
full-screen image around: `draw()` pastes the region into it and the panel
specific code pushes out the whole buffer.

Panels with a red or yellow channel are driven as black and white only - the
colour RAM is filled with a constant.
"""

from abc import abstractmethod

from PIL import Image

from papertty.drivers.drivers_base import GPIO, WaveshareEPD

# All classes in this module are untested AI-assisted ports.
EXPERIMENTAL = True


class WaveshareBuffered(WaveshareEPD):
    """EXPERIMENTAL common base for the panels in this module.

    Subclasses implement `init`, `display_full` and (when the panel supports a
    fast refresh) `display_partial`; everything to do with keeping track of the
    frame is handled here.
    """

    experimental = True

    # BUSY pin level that means "the panel is busy"
    busy_value = 1
    # how long to sleep between BUSY polls
    busy_poll_ms = 10
    # reset pulse timings
    reset_high_ms = 200
    reset_low_ms = 2

    def __init__(self, name, width, height):
        super().__init__(name=name, width=width, height=height)
        self.colors = 2
        self.supports_partial = False
        self.partial_refresh = False
        self.supports_1bpp = False
        self.enable_1bpp = False
        self.align_1bpp_width = False
        self.align_1bpp_height = False
        self.supports_multi_draw = False
        self.frame_buffer = None
        # partial refresh is only valid once the panel has a reference frame
        self.base_image_written = False
        print(
            "!! EXPERIMENTAL DRIVER ({}) — vibe-coded / untested on hardware; "
            "use at your own risk !!".format(type(self).__name__)
        )

    # --- low level ---------------------------------------------------------

    def reset(self):
        self.digital_write(self.RST_PIN, GPIO.HIGH)
        self.delay_ms(self.reset_high_ms)
        self.digital_write(self.RST_PIN, GPIO.LOW)
        self.delay_ms(self.reset_low_ms)
        self.digital_write(self.RST_PIN, GPIO.HIGH)
        self.delay_ms(self.reset_high_ms)

    def wait_until_idle(self):
        while self.digital_read(self.BUSY_PIN) == self.busy_value:
            self.delay_ms(self.busy_poll_ms)

    # --- frame buffer ------------------------------------------------------

    @property
    def line_width(self):
        """Bytes per row of panel RAM"""
        return self.width // 8

    @property
    def buffer_size(self):
        return self.line_width * self.height

    def new_frame_buffer(self, color=255):
        self.frame_buffer = Image.new('1', (self.width, self.height), color)

    def update_frame_buffer(self, x, y, image):
        if self.frame_buffer is None:
            self.new_frame_buffer()
        self.frame_buffer.paste(image if image.mode == '1' else image.convert('1'), (x, y))

    def frame_bytes(self, invert=False):
        """The frame buffer packed for the panel: one bit per pixel, 1 = white.

        Set `invert` for the controllers that expect 1 = black.
        """
        if self.frame_buffer is None:
            self.new_frame_buffer()
        buf = bytearray(self.frame_buffer.tobytes('raw'))
        if invert:
            for i in range(len(buf)):
                buf[i] ^= 0xFF
        return buf

    def filled_bytes(self, value):
        return bytearray([value]) * self.buffer_size

    # --- driver interface --------------------------------------------------

    @abstractmethod
    def init(self, partial=True, **kwargs):
        pass

    @abstractmethod
    def display_full(self):
        """Push the frame buffer out with a full refresh"""
        pass

    def display_base(self):
        """Push the frame buffer out and store it as the partial refresh reference"""
        self.display_full()

    def display_partial(self):
        """Push the frame buffer out with a fast refresh"""
        self.display_full()

    def draw(self, x, y, image):
        self.update_frame_buffer(x, y, image)
        if not (self.supports_partial and self.partial_refresh):
            self.display_full()
        elif self.base_image_written:
            self.display_partial()
        else:
            # a fast refresh only makes sense once the panel has a frame to
            # diff against, so the first update is a full one
            self.display_base()
            self.base_image_written = True

    def clear(self):
        self.new_frame_buffer(self.white)
        self.display_full()
        self.base_image_written = False

    def scrub(self, fillsize=16):
        """Flush the panel by driving it fully black and then fully white.

        These controllers redraw the whole screen anyway, so the stripe size
        used by the partial refresh drivers is ignored.
        """
        for color in (self.black, self.white):
            self.new_frame_buffer(color)
            self.display_full()
        self.base_image_written = False


class WaveshareSSD16xx(WaveshareBuffered):
    """Base for the SSD1675 / SSD1680 / SSD1683 controllers.

    The frame goes into RAM 0x24 (and 0x26, which holds the previous frame that
    a partial refresh diffs against) and an update is triggered with 0x22/0x20.
    """

    DRIVER_OUTPUT_CONTROL = 0x01
    GATE_VOLTAGE = 0x03
    SOURCE_VOLTAGE = 0x04
    BOOSTER_SOFT_START = 0x0C
    DEEP_SLEEP = 0x10
    DATA_ENTRY_MODE = 0x11
    SW_RESET = 0x12
    TEMPERATURE_SENSOR_WRITE = 0x1A
    TEMPERATURE_SENSOR_CONTROL = 0x18
    MASTER_ACTIVATION = 0x20
    DISPLAY_UPDATE_CONTROL_1 = 0x21
    DISPLAY_UPDATE_CONTROL_2 = 0x22
    WRITE_RAM = 0x24
    WRITE_RAM_RED = 0x26
    WRITE_LUT_REGISTER = 0x32
    DISPLAY_OPTION = 0x37
    WRITE_VCOM_REGISTER = 0x2C
    BORDER_WAVEFORM_CONTROL = 0x3C
    WRITE_OTP_SELECTION = 0x3F
    SET_RAM_X_START_END = 0x44
    SET_RAM_Y_START_END = 0x45
    SET_RAM_X_COUNTER = 0x4E
    SET_RAM_Y_COUNTER = 0x4F

    # arguments to 0x22 that select the waveform used by the update
    update_full = 0xF7
    update_partial = 0xFF

    reset_high_ms = 20

    # The vendor code strobes CS around every transfer on these panels.
    def send_command(self, command):
        self.digital_write(self.CS_PIN, GPIO.LOW)
        super().send_command(command)
        self.digital_write(self.CS_PIN, GPIO.HIGH)

    def send_data(self, data):
        self.digital_write(self.CS_PIN, GPIO.LOW)
        super().send_data(data)
        self.digital_write(self.CS_PIN, GPIO.HIGH)

    def send_data_multi(self, dataArray):
        self.digital_write(self.CS_PIN, GPIO.LOW)
        super().send_data_multi(dataArray)
        self.digital_write(self.CS_PIN, GPIO.HIGH)

    def turn_on_display(self, mode):
        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(mode)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

    def set_window(self, x_start, y_start, x_end, y_end):
        self.send_command(self.SET_RAM_X_START_END)
        # x is addressed in bytes, so the low 3 bits are ignored
        self.send_data_multi([(x_start >> 3) & 0xFF, (x_end >> 3) & 0xFF])
        self.send_command(self.SET_RAM_Y_START_END)
        self.send_data_multi([y_start & 0xFF, (y_start >> 8) & 0xFF,
                              y_end & 0xFF, (y_end >> 8) & 0xFF])

    def set_cursor(self, x, y):
        self.send_command(self.SET_RAM_X_COUNTER)
        self.send_data(x & 0xFF)
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([y & 0xFF, (y >> 8) & 0xFF])

    def set_lut(self, lut):
        """Load a 159 byte waveform table and the voltages that go with it"""
        self.send_command(self.WRITE_LUT_REGISTER)
        self.send_data_multi(list(lut[:153]))
        self.wait_until_idle()
        self.send_command(self.WRITE_OTP_SELECTION)
        self.send_data(lut[153])
        self.send_command(self.GATE_VOLTAGE)
        self.send_data(lut[154])
        self.send_command(self.SOURCE_VOLTAGE)
        self.send_data_multi([lut[155], lut[156], lut[157]])
        self.send_command(self.WRITE_VCOM_REGISTER)
        self.send_data(lut[158])

    def display_full(self):
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_full)

    def display_base(self):
        buf = self.frame_bytes()
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(buf)
        self.send_command(self.WRITE_RAM_RED)
        self.send_data_multi(buf)
        self.turn_on_display(self.update_full)

    def sleep(self):
        self.send_command(self.DEEP_SLEEP)
        self.send_data(0x01)


class WaveshareUC81xx(WaveshareBuffered):
    """Base for the UC8151 / UC8176 / UC8179 controllers.

    The frame is split over two RAM banks (0x10 holds the previous frame or the
    red channel, 0x13 the new one) and 0x12 triggers the refresh.
    """

    PANEL_SETTING = 0x00
    POWER_SETTING = 0x01
    POWER_OFF = 0x02
    POWER_ON = 0x04
    BOOSTER_SOFT_START = 0x06
    DEEP_SLEEP = 0x07
    DATA_START_TRANSMISSION_1 = 0x10
    DISPLAY_REFRESH = 0x12
    DATA_START_TRANSMISSION_2 = 0x13
    PLL_CONTROL = 0x30
    VCOM_AND_DATA_INTERVAL_SETTING = 0x50
    TCON_SETTING = 0x60
    RESOLUTION_SETTING = 0x61
    VCM_DC_SETTING = 0x82
    PARTIAL_IN = 0x91
    PARTIAL_OUT = 0x92
    PARTIAL_WINDOW = 0x90

    # these panels pull BUSY low while busy
    busy_value = 0
    # some revisions only update BUSY after being polled with 0x71
    poll_status = False
    # how long to wait after kicking off a refresh
    refresh_delay_ms = 100

    def wait_until_idle(self):
        if self.poll_status:
            self.send_command(self.GET_STATUS)
        while self.digital_read(self.BUSY_PIN) == self.busy_value:
            if self.poll_status:
                self.send_command(self.GET_STATUS)
            self.delay_ms(self.busy_poll_ms)

    def turn_on_display(self):
        self.send_command(self.DISPLAY_REFRESH)
        self.delay_ms(self.refresh_delay_ms)
        self.wait_until_idle()

    def sleep(self):
        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0xF7)
        self.send_command(self.POWER_OFF)
        self.wait_until_idle()
        self.send_command(self.DEEP_SLEEP)
        self.send_data(0xA5)


class EPD1in54v2(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 1.54" V2 - monochrome"""

    WF_FULL = [
        0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x8, 0x1, 0x0, 0x8, 0x1, 0x0, 0x2,
        0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
        0x22, 0x17, 0x41, 0x0, 0x32, 0x20
    ]

    WF_PARTIAL = [
        0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0xF, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
        0x02, 0x17, 0x41, 0xB0, 0x32, 0x28,
    ]

    update_full = 0xC7
    update_partial = 0xCF
    reset_high_ms = 200
    reset_low_ms = 5
    busy_poll_ms = 20

    def __init__(self):
        super().__init__(name='1.54" BW V2', width=200, height=200)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xC7, 0x00, 0x01])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x01)

        # gate scan is reversed above, so the RAM is filled bottom up
        self.set_window(0, self.height - 1, self.width - 1, 0)

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x01)

        self.send_command(self.TEMPERATURE_SENSOR_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xB1)
        self.send_command(self.MASTER_ACTIVATION)

        self.set_cursor(0, self.height - 1)
        self.wait_until_idle()

        self.set_lut(self.WF_FULL)
        return 0

    def enter_partial_mode(self):
        """Swap in the fast waveform - the panel keeps its RAM contents"""
        self.reset()
        self.wait_until_idle()

        self.set_lut(self.WF_PARTIAL)

        self.send_command(self.DISPLAY_OPTION)
        self.send_data_multi([0x00, 0x00, 0x00, 0x00, 0x00,
                              0x40, 0x00, 0x00, 0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC0)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

    def display_base(self):
        if self.partial_refresh:
            self.enter_partial_mode()
        super().display_base()

    def display_partial(self):
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD2in13v3(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.13" BW V3 - monochrome"""

    lut_full_update = [
        0x80, 0x4A, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x4A, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x80, 0x4A, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x4A, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0xF, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0xF, 0x0, 0x0, 0xF, 0x0, 0x0, 0x2,
        0xF, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
        0x22, 0x17, 0x41, 0x0, 0x32, 0x36,
    ]

    lut_partial_update = [
        0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x14, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
        0x22, 0x17, 0x41, 0x00, 0x32, 0x36,
    ]

    update_full = 0xC7
    update_partial = 0x0F

    def __init__(self):
        # the actual pixel width is 122, but 128 is the 'logical' width
        super().__init__(name='2.13" BW V3', width=128, height=250)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xF9, 0x00, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x05)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x00, 0x80])

        self.send_command(self.TEMPERATURE_SENSOR_CONTROL)
        self.send_data(0x80)

        self.wait_until_idle()

        self.set_lut(self.lut_full_update)
        return 0

    def display_partial(self):
        # a short reset pulse without the usual settling delays
        self.digital_write(self.RST_PIN, GPIO.LOW)
        self.delay_ms(1)
        self.digital_write(self.RST_PIN, GPIO.HIGH)

        self.set_lut(self.lut_partial_update)

        self.send_command(self.DISPLAY_OPTION)
        self.send_data_multi([0x00, 0x00, 0x00, 0x00, 0x00,
                              0x40, 0x00, 0x00, 0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC0)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD2in13v4(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.13" BW V4 - monochrome"""

    update_full = 0xF7
    update_partial = 0xFF

    def __init__(self):
        # the actual pixel width is 122, but 128 is the 'logical' width
        super().__init__(name='2.13" BW V4', width=128, height=250)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xF9, 0x00, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x05)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x00, 0x80])

        self.send_command(self.TEMPERATURE_SENSOR_CONTROL)
        self.send_data(0x80)

        self.wait_until_idle()
        return 0

    def display_partial(self):
        self.digital_write(self.RST_PIN, GPIO.LOW)
        self.delay_ms(1)
        self.digital_write(self.RST_PIN, GPIO.HIGH)

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xF9, 0x00, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD2in9v2(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.9" BW V2 - monochrome"""

    WS_20_30 = [
        0x80, 0x66, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0x0, 0x0, 0x0,
        0x10, 0x66, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0,
        0x80, 0x66, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0x0, 0x0, 0x0,
        0x10, 0x66, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x14, 0x8, 0x0, 0x0, 0x0, 0x0, 0x2,
        0xA, 0xA, 0x0, 0xA, 0xA, 0x0, 0x1,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x14, 0x8, 0x0, 0x1, 0x0, 0x0, 0x1,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x44, 0x44, 0x44, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0,
        0x22, 0x17, 0x41, 0x0, 0x32, 0x36
    ]

    WF_PARTIAL = [
        0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0A, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1,
        0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
        0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
        0x22, 0x17, 0x41, 0xB0, 0x32, 0x36,
    ]

    update_full = 0xC7
    update_partial = 0x0F
    reset_high_ms = 50

    def __init__(self):
        super().__init__(name='2.9" BW V2', width=128, height=296)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0x27, 0x01, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x00, 0x80])

        self.set_cursor(0, 0)
        self.wait_until_idle()

        self.set_lut(self.WS_20_30)
        return 0

    def display_partial(self):
        self.digital_write(self.RST_PIN, GPIO.LOW)
        self.delay_ms(2)
        self.digital_write(self.RST_PIN, GPIO.HIGH)
        self.delay_ms(2)

        self.set_lut(self.WF_PARTIAL)

        self.send_command(self.DISPLAY_OPTION)
        self.send_data_multi([0x00, 0x00, 0x00, 0x00, 0x00,
                              0x40, 0x00, 0x00, 0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC0)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD2in66(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.66" - monochrome"""

    WF_PARTIAL = [
        0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x01, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22,
        0x00, 0x00, 0x00, 0x22, 0x17, 0x41, 0xB0, 0x32, 0x36,
    ]

    reset_high_ms = 200
    busy_poll_ms = 200

    def __init__(self):
        super().__init__(name='2.66" BW', width=152, height=296)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.SW_RESET)
        self.delay_ms(300)
        self.wait_until_idle()

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        # RAM addressing starts one byte in on this panel
        self.send_command(self.SET_RAM_X_START_END)
        self.send_data_multi([0x01, 0x13])
        self.send_command(self.SET_RAM_Y_START_END)
        self.send_data_multi([0x00, 0x00, 0x28, 0x01])

        if partial:
            self.send_command(self.WRITE_LUT_REGISTER)
            self.send_data_multi(list(self.WF_PARTIAL))

            self.send_command(self.DISPLAY_OPTION)
            self.send_data_multi([0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x40, 0x00, 0x00, 0x00, 0x00])

            self.send_command(self.BORDER_WAVEFORM_CONTROL)
            self.send_data(0x80)

            self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
            self.send_data(0xCF)
            self.send_command(self.MASTER_ACTIVATION)
            self.wait_until_idle()
        else:
            self.send_command(self.BORDER_WAVEFORM_CONTROL)
            self.send_data(0x01)
        return 0

    def turn_on_display(self, mode=None):
        """The waveform is picked at init time, so only 0x20 is needed here"""
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

    def display_full(self):
        self.send_command(self.SET_RAM_X_COUNTER)
        self.send_data(0x01)
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([0x27, 0x01])

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display()

    def display_base(self):
        self.display_full()

    def display_partial(self):
        self.display_full()


class EPD2in66b(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.66" B - black / white / red (drawn as black and white)"""

    reset_high_ms = 200
    reset_low_ms = 5
    busy_poll_ms = 20

    def __init__(self):
        super().__init__(name='2.66" B', width=152, height=296)
        self.colors = 3

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.SW_RESET)
        self.delay_ms(30)
        self.wait_until_idle()

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x00, 0x80])

        self.set_cursor(0, 0)
        self.wait_until_idle()
        return 0

    def turn_on_display(self, mode=None):
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

    def display_full(self):
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        # blank red channel
        self.send_command(self.WRITE_RAM_RED)
        self.send_data_multi(self.filled_bytes(0x00))
        self.turn_on_display()


class EPD2in7v2(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.7" BW V2 - monochrome"""

    update_full = 0xF7
    update_partial = 0xFF
    busy_poll_ms = 20

    def __init__(self):
        super().__init__(name='2.7" BW V2', width=176, height=264)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()
        self.wait_until_idle()

        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.SET_RAM_Y_START_END)
        self.send_data_multi([0x00, 0x00, 0x07, 0x01])

        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([0x00, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)
        return 0

    def display_partial(self):
        self.reset()

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD2in7b_V2(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 2.7" B V2 - black / white / red (drawn as black and white)"""

    def __init__(self):
        super().__init__(name='2.7" B V2', width=176, height=264)
        self.colors = 3

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        # 0x00 with three arguments is what the vendor driver sends here
        self.send_command(0x00)
        self.send_data_multi([0x27, 0x01, 0x00])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)
        return 0

    def turn_on_display(self, mode=None):
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

    def display_full(self):
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.send_command(self.WRITE_RAM_RED)
        self.send_data_multi(self.filled_bytes(0x00))
        self.turn_on_display()


class EPD4in2v2(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 4.2" BW V2 - monochrome"""

    update_full = 0xF7
    update_partial = 0xFF
    reset_high_ms = 100
    busy_poll_ms = 20

    def __init__(self):
        super().__init__(name='4.2" BW V2', width=400, height=300)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()
        self.wait_until_idle()

        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x40, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x05)

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x03)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)
        self.wait_until_idle()
        return 0

    def display_full(self):
        # writing both banks leaves a valid reference frame behind
        self.display_base()

    def display_partial(self):
        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_1)
        self.send_data_multi([0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x80)

        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.turn_on_display(self.update_partial)


class EPD7in5_HD(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 7.5" HD - monochrome"""

    busy_poll_ms = 0

    def __init__(self):
        super().__init__(name='7.5" HD BW', width=880, height=528)

    def wait_until_idle(self):
        super().wait_until_idle()
        self.delay_ms(200)

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_idle()
        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(0x46)  # auto write red RAM
        self.send_data(0xF7)
        self.wait_until_idle()
        self.send_command(0x47)  # auto write black/white RAM
        self.send_data(0xF7)
        self.wait_until_idle()

        self.send_command(self.BOOSTER_SOFT_START)
        self.send_data_multi([0xAE, 0xC7, 0xC3, 0xC0, 0x40])

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xAF, 0x02, 0x01])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x01)

        self.send_command(self.SET_RAM_X_START_END)
        self.send_data_multi([0x00, 0x00, 0x6F, 0x03])
        self.send_command(self.SET_RAM_Y_START_END)
        self.send_data_multi([0xAF, 0x02, 0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x05)

        self.send_command(self.TEMPERATURE_SENSOR_CONTROL)
        self.send_data(0x80)

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xB1)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

        self.send_command(self.SET_RAM_X_COUNTER)
        self.send_data_multi([0x00, 0x00])
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([0x00, 0x00])
        return 0

    def display_full(self):
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([0x00, 0x00])
        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())
        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xF7)
        self.send_command(self.MASTER_ACTIVATION)
        self.delay_ms(10)
        self.wait_until_idle()


class EPD7in5b_HD(WaveshareSSD16xx):
    """[EXPERIMENTAL] Waveshare 7.5" HD B - black / white / red (drawn as black and white)"""

    busy_poll_ms = 0
    reset_low_ms = 4

    def __init__(self):
        super().__init__(name='7.5" HD B', width=880, height=528)
        self.colors = 3

    def wait_until_idle(self):
        super().wait_until_idle()
        self.delay_ms(200)

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.SW_RESET)
        self.wait_until_idle()

        self.send_command(0x46)  # auto write red RAM
        self.send_data(0xF7)
        self.wait_until_idle()
        self.send_command(0x47)  # auto write black/white RAM
        self.send_data(0xF7)
        self.wait_until_idle()

        self.send_command(self.BOOSTER_SOFT_START)
        self.send_data_multi([0xAE, 0xC7, 0xC3, 0xC0, 0x40])

        self.send_command(self.DRIVER_OUTPUT_CONTROL)
        self.send_data_multi([0xAF, 0x02, 0x01])

        self.send_command(self.DATA_ENTRY_MODE)
        self.send_data(0x01)

        self.send_command(self.SET_RAM_X_START_END)
        self.send_data_multi([0x00, 0x00, 0x6F, 0x03])
        self.send_command(self.SET_RAM_Y_START_END)
        self.send_data_multi([0xAF, 0x02, 0x00, 0x00])

        self.send_command(self.BORDER_WAVEFORM_CONTROL)
        self.send_data(0x01)

        self.send_command(self.TEMPERATURE_SENSOR_CONTROL)
        self.send_data(0x80)
        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xB1)
        self.send_command(self.MASTER_ACTIVATION)
        self.wait_until_idle()

        self.send_command(self.SET_RAM_X_COUNTER)
        self.send_data_multi([0x00, 0x00])
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data_multi([0xAF, 0x02])
        return 0

    def display_full(self):
        self.send_command(self.SET_RAM_Y_COUNTER)
        self.send_data(0xAF)

        self.send_command(self.WRITE_RAM)
        self.send_data_multi(self.frame_bytes())

        self.send_command(self.WRITE_RAM_RED)
        self.send_data_multi(self.filled_bytes(0x00))

        self.send_command(self.DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC7)
        self.send_command(self.MASTER_ACTIVATION)
        self.delay_ms(200)
        self.wait_until_idle()


class EPD2in9d(WaveshareUC81xx):
    """[EXPERIMENTAL] Waveshare 2.9" D - monochrome (flexible)"""

    lut_vcom1 = [
        0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00,
    ]

    lut_ww1 = [
        0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]

    lut_bw1 = [
        0x80, 0x19, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]

    lut_wb1 = [
        0x40, 0x19, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]

    lut_bb1 = [
        0x00, 0x19, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]

    poll_status = True
    refresh_delay_ms = 10

    def __init__(self):
        super().__init__(name='2.9" D', width=128, height=296)
        self.supports_partial = True

    def reset(self):
        """This panel wants three reset pulses"""
        for _ in range(3):
            self.digital_write(self.RST_PIN, GPIO.HIGH)
            self.delay_ms(20)
            self.digital_write(self.RST_PIN, GPIO.LOW)
            self.delay_ms(5)
        self.digital_write(self.RST_PIN, GPIO.HIGH)
        self.delay_ms(20)

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.POWER_ON)
        self.wait_until_idle()

        self.send_command(self.PANEL_SETTING)
        self.send_data(0x1F)  # LUT from OTP

        self.send_command(self.RESOLUTION_SETTING)
        self.send_data_multi([0x80, 0x01, 0x28])

        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x97)
        return 0

    def set_partial_registers(self):
        self.send_command(self.POWER_SETTING)
        self.send_data_multi([0x03, 0x00, 0x2B, 0x2B, 0x03])

        self.send_command(self.BOOSTER_SOFT_START)
        self.send_data_multi([0x17, 0x17, 0x17])

        self.send_command(self.POWER_ON)
        self.wait_until_idle()

        self.send_command(self.PANEL_SETTING)
        self.send_data(0xBF)

        self.send_command(self.PLL_CONTROL)
        self.send_data(0x3A)

        self.send_command(self.RESOLUTION_SETTING)
        self.send_data_multi([self.width, (self.height >> 8) & 0xFF, self.height & 0xFF])

        self.send_command(self.VCM_DC_SETTING)
        self.send_data(0x12)

        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x97)

        for command, lut in ((0x20, self.lut_vcom1), (0x21, self.lut_ww1),
                             (0x22, self.lut_bw1), (0x23, self.lut_wb1),
                             (0x24, self.lut_bb1)):
            self.send_command(command)
            self.send_data_multi(list(lut))

    def display_full(self):
        self.send_command(self.DATA_START_TRANSMISSION_1)
        self.send_data_multi(self.filled_bytes(0x00))
        self.delay_ms(10)

        self.send_command(self.DATA_START_TRANSMISSION_2)
        self.send_data_multi(self.frame_bytes())
        self.delay_ms(10)

        self.turn_on_display()

    def display_partial(self):
        self.set_partial_registers()
        self.send_command(self.PARTIAL_IN)
        self.send_command(self.PARTIAL_WINDOW)
        self.send_data_multi([0, self.width - 1, 0, 0,
                              self.height // 256, self.height % 256 - 1, 0x28])

        self.send_command(self.DATA_START_TRANSMISSION_1)
        self.send_data_multi(self.frame_bytes())
        self.delay_ms(10)

        self.send_command(self.DATA_START_TRANSMISSION_2)
        self.send_data_multi(self.frame_bytes(invert=True))
        self.delay_ms(10)

        self.turn_on_display()


class EPD4in2b_V2(WaveshareUC81xx):
    """[EXPERIMENTAL] Waveshare 4.2" B V2 - black / white / red (drawn as black and white)"""

    # Waveshare probe the controller revision over a bit-banged SPI read, which
    # is not available here. Set this to True for boards that report revision
    # 0x01 (SSD1683) instead of the original UC8176.
    ssd1683 = False

    reset_low_ms = 5

    def __init__(self):
        super().__init__(name='4.2" B V2', width=400, height=300)
        self.colors = 3

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        if self.ssd1683:
            self.busy_value = 1
            self.wait_until_idle()
            self.send_command(0x12)  # SWRESET
            self.wait_until_idle()

            self.send_command(0x3C)  # border waveform
            self.send_data(0x05)
            self.send_command(0x18)
            self.send_data(0x80)
            self.send_command(0x11)  # data entry mode
            self.send_data(0x03)

            self.send_command(0x44)
            self.send_data_multi([0x00, self.width // 8 - 1])
            self.send_command(0x45)
            self.send_data_multi([0x00, 0x00,
                                  (self.height - 1) % 256, (self.height - 1) // 256])
            self.send_command(0x4E)
            self.send_data(0x00)
            self.send_command(0x4F)
            self.send_data_multi([0x00, 0x00])
            self.wait_until_idle()
        else:
            self.send_command(self.POWER_ON)
            self.wait_until_idle()

            self.send_command(self.PANEL_SETTING)
            self.send_data(0x0F)
        return 0

    def display_full(self):
        if self.ssd1683:
            self.send_command(0x24)
            self.send_data_multi(self.frame_bytes())
            self.send_command(0x26)
            self.send_data_multi(self.filled_bytes(0x00))

            self.send_command(0x22)
            self.send_data(0xF7)
            self.send_command(0x20)
            self.wait_until_idle()
        else:
            self.send_command(self.DATA_START_TRANSMISSION_1)
            self.send_data_multi(self.frame_bytes())
            self.send_command(self.DATA_START_TRANSMISSION_2)
            self.send_data_multi(self.filled_bytes(0x00))
            self.turn_on_display()

    def sleep(self):
        if self.ssd1683:
            self.send_command(0x10)
            self.send_data(0x03)
        else:
            super().sleep()


class EPD5in83v2(WaveshareUC81xx):
    """[EXPERIMENTAL] Waveshare 5.83" V2 - monochrome"""

    busy_poll_ms = 10

    def __init__(self):
        super().__init__(name='5.83" BW V2', width=648, height=480)
        self.supports_partial = True

    def init(self, partial=True, **kwargs):
        self.partial_refresh = partial
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.PANEL_SETTING)
        self.send_data(0x1F)

        if partial:
            self.send_command(0xE0)
            self.send_data(0x02)
            self.send_command(0xE5)
            self.send_data(0x6E)

            self.send_command(self.POWER_ON)
            self.delay_ms(100)
            self.wait_until_idle()
        else:
            self.send_command(self.POWER_ON)
            self.delay_ms(300)
            self.wait_until_idle()

            self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
            self.send_data_multi([0x21, 0x07])
        return 0

    def set_window(self, x_start, y_start, x_end, y_end):
        self.send_command(self.PARTIAL_IN)
        self.send_command(self.PARTIAL_WINDOW)
        self.send_data_multi([(x_start >> 8) & 0xFF, x_start & 0xFF,
                              (x_end >> 8) & 0xFF, x_end & 0xFF,
                              (y_start >> 8) & 0xFF, y_start & 0xFF,
                              (y_end >> 8) & 0xFF, y_end & 0xFF,
                              0x01])

    def display_full(self):
        buf = self.frame_bytes()
        self.send_command(self.DATA_START_TRANSMISSION_1)
        self.send_data_multi(buf)
        self.send_command(self.DATA_START_TRANSMISSION_2)
        self.send_data_multi(buf)
        self.turn_on_display()

    def display_partial(self):
        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data_multi([0xA9, 0x07])

        self.set_window(0, 0, self.width - 1, self.height - 1)

        self.send_command(self.DATA_START_TRANSMISSION_2)
        self.send_data_multi(self.frame_bytes())

        self.turn_on_display()
        self.send_command(self.PARTIAL_OUT)


class EPD5in83b_V2(WaveshareUC81xx):
    """[EXPERIMENTAL] Waveshare 5.83" B V2 - black / white / red (drawn as black and white)"""

    poll_status = True
    busy_poll_ms = 200
    reset_low_ms = 1
    refresh_delay_ms = 200

    def __init__(self):
        super().__init__(name='5.83" B V2', width=648, height=480)
        self.colors = 3

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.send_command(self.POWER_SETTING)
        self.send_data_multi([0x07, 0x07, 0x3F, 0x3F])

        self.send_command(self.POWER_ON)
        self.delay_ms(100)
        self.wait_until_idle()

        self.send_command(self.PANEL_SETTING)
        self.send_data(0x0F)

        self.send_command(self.RESOLUTION_SETTING)
        self.send_data_multi([0x02, 0x88, 0x01, 0xE0])

        self.send_command(0x15)
        self.send_data(0x00)

        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data_multi([0x11, 0x07])

        self.send_command(self.TCON_SETTING)
        self.send_data(0x22)
        return 0

    def display_full(self):
        self.send_command(self.DATA_START_TRANSMISSION_1)
        self.send_data_multi(self.frame_bytes())
        self.send_command(self.DATA_START_TRANSMISSION_2)
        self.send_data_multi(self.filled_bytes(0x00))
        self.turn_on_display()

    def sleep(self):
        self.send_command(self.POWER_OFF)
        self.wait_until_idle()
        self.send_command(self.DEEP_SLEEP)
        self.send_data(0xA5)


class EPD4in01f(WaveshareUC81xx):
    """[EXPERIMENTAL] Waveshare 4.01" F - 7 colors (drawn as black and white)"""

    # each source byte holds 8 pixels, each output byte holds two 4bpp pixels;
    # colour 0x0 is black and 0x1 is white
    NIBBLES = [bytes((((b >> 7) & 1) << 4 | ((b >> 6) & 1),
                      ((b >> 5) & 1) << 4 | ((b >> 4) & 1),
                      ((b >> 3) & 1) << 4 | ((b >> 2) & 1),
                      ((b >> 1) & 1) << 4 | (b & 1)))
               for b in range(256)]

    reset_low_ms = 1

    def __init__(self):
        super().__init__(name='4.01" F (7 color)', width=640, height=400)
        self.colors = 7

    def wait_until_busy_high(self):
        while self.digital_read(self.BUSY_PIN) == 0:
            self.delay_ms(10)

    def wait_until_busy_low(self):
        while self.digital_read(self.BUSY_PIN) == 1:
            self.delay_ms(10)

    def wait_until_idle(self):
        self.wait_until_busy_high()

    def init(self, partial=True, **kwargs):
        self.partial_refresh = False
        self.base_image_written = False
        if self.epd_init() != 0:
            return -1
        self.reset()

        self.wait_until_busy_high()
        self.send_command(self.PANEL_SETTING)
        self.send_data_multi([0x2F, 0x00])
        self.send_command(self.POWER_SETTING)
        self.send_data_multi([0x37, 0x00, 0x05, 0x05])
        self.send_command(0x03)
        self.send_data(0x00)
        self.send_command(self.BOOSTER_SOFT_START)
        self.send_data_multi([0xC7, 0xC7, 0x1D])
        self.send_command(0x41)
        self.send_data(0x00)
        self.send_command(self.VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x37)
        self.send_command(self.TCON_SETTING)
        self.send_data(0x22)
        self.send_command(self.RESOLUTION_SETTING)
        self.send_data_multi([0x02, 0x80, 0x01, 0x90])
        self.send_command(0xE3)
        self.send_data(0xAA)
        return 0

    def frame_bytes(self, invert=False):
        """Expand the 1bpp buffer into the panel's 4 bits per pixel format"""
        if self.frame_buffer is None:
            self.new_frame_buffer()
        nibbles = self.NIBBLES
        return bytearray().join([nibbles[b] for b in self.frame_buffer.tobytes('raw')])

    def display_full(self):
        self.send_command(self.RESOLUTION_SETTING)
        self.send_data_multi([0x02, 0x80, 0x01, 0x90])
        self.send_command(self.DATA_START_TRANSMISSION_1)
        self.send_data_multi(self.frame_bytes())
        self.send_command(self.POWER_ON)
        self.wait_until_busy_high()
        self.send_command(self.DISPLAY_REFRESH)
        self.wait_until_busy_high()
        self.send_command(self.POWER_OFF)
        self.wait_until_busy_low()

    def sleep(self):
        self.send_command(self.DEEP_SLEEP)
        self.send_data(0xA5)
