from evaluationkit import *
import string

DEFAULT_BIN_DIR = r"C:\Program Files\Teledyne e2v\Evalkit-Emeraldgen2\1.0\pigentl\bin"
DEFAULT_CTI_NAME = "pigentl.cti"
DEFAULT_DLL_NAME = "pigentl-sdk.dll"

# used to map sensor features address from XML file
_xml_bootstrap_nodes_addresses = {
    "DeviceVendorName":      0x0,
    "DeviceModelName":       0x20,
    "DeviceVersion":         0x40,
    "DeviceFirmwareVersion": 0x60,
    "SerialNumber":          0xE0,
    "SensorWidth":   0x1000C,
    "SensorHeight":  0x10010,
    "PixelFormat":   0x10014,
    "AWBredGain":    0xE700000C,
    "AWBgreenGain":  0xE7000010,
    "AWBblueGain":   0xE7000014,
    "AWBenable":     0xE7000008,
    "TriggerSource": 0x11000,
}

# used to map Sensor features address from XML file
_xml_sensor_nodes_addresses = {
    "BaseAddress":  0x30000,
    "ExposureTime": 0x30020,
    "WaitTime":     0x3000B,
    "LineLength":   0x30006,
    "ConfigGain":   0x30022,
    "ClampOffset":  0x30036,
    "ChipID":       0x3007F,
}


# used to get the number of bits per pixel from the EK/XML pixel format
xml_pixel_format_nbits = {
    0x01080001: 8,   # Mono8
    0x010A0046: 10,  # Mono10p
    0x010C0047: 12,  # Mono12p
    0x01080009: 24,  # BayerRG8
    0x010A0058: 30,  # BayerRG10p
    0x010C0059: 36,  # BayerRG12p
    8: 0x01080001,   # Mono8
    10: 0x010A0046,  # Mono10p
    12: 0x010C0047,  # Mono12p
    24: 0x01080009,  # BayerRG8
    30: 0x010A0058,  # BayerRG10p
    36: 0x010C0059,  # BayerRG12p
}

# used to get the pixel type from the EK/XML pixel format
xml_pixel_format_type = {
    0x01080001: "Mono8",       # Mono8
    0x010A0046: "Mono10p",     # Mono10p
    0x010C0047: "Mono12p",     # Mono12p
    0x01080009: "BayerRG8",    # BayerRG8
    0x010A0058: "BayerRG10p",  # BayerRG10p
    0x010C0059: "BayerRG12p",  # BayerRG12p
    "Mono8":      0x01080001,  # Mono8
    "Mono10p":    0x010A0046,  # Mono10p
    "Mono12p":    0x010C0047,  # Mono12p
    "BayerRG8":   0x01080009,  # BayerRG8
    "BayerRG10p": 0x010A0058,  # BayerRG10p
    "BayerRG12p": 0x010C0059,  # BayerRG12p
}

def clean_char(text):
    # remove non printable char from ASCII chain
    return ''.join(c for c in text if c in string.printable)

def print_info(ek):
    print("Camera INFO:")
    print("\tManufacturer info          ", clean_char(ek.vendor_name))
    print("\tDevice name                ", clean_char(ek.model_name))
    print("\tSerial number              ", clean_char(ek.serial_number))
    print("\tDevice firmware version    ", clean_char(ek.firmware_version))
    print("\tImage width                ", ek.sensor_width)
    print("\tImage height               ", ek.sensor_height)
    print("\tPixel format               ", ek.pixel_format)
    print("\tLine length                 %.2f us" % (ek.line_length * 20e-3))
    print("\tExposure time               %.2f ms" % ek.exposure_time)
    print("\tWait time                   %.2f ms" % ek.wait_time)


class Sensor(EvaluationKit):
    def __init__(self, dll_path=None, cti_path=None):
        self.DEFAULT_BIN_DIR = DEFAULT_BIN_DIR
        self.DEFAULT_CTI_NAME = DEFAULT_CTI_NAME
        self.DEFAULT_DLL_NAME = DEFAULT_DLL_NAME
        if dll_path is None:
            dll_path = os.path.join(os.path.dirname(__file__), self.DEFAULT_BIN_DIR, self.DEFAULT_DLL_NAME)
        if cti_path is None:
            cti_path = os.path.join(os.path.dirname(__file__), self.DEFAULT_BIN_DIR, self.DEFAULT_CTI_NAME)
        super().__init__(dll_path, cti_path)

    def __del__(self):
        super().__del__()

    @property
    def clkref(self):
        return 50  # MHz

    @property
    def model_name(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceModelName"], size=32)[1]

    @property
    def vendor_name(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceVendorName"], size=32)[1]

    @property
    def firmware_version(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceFirmwareVersion"], size=32)[1]

    @property
    def serial_number(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["SerialNumber"], size=16)[1]

    @property
    def pixel_format(self):
        return xml_pixel_format_type[
            int.from_bytes(
                self.read(address=_xml_bootstrap_nodes_addresses["PixelFormat"], size=4, decode=False)[1],
                byteorder="little",
            )
        ]

    @property
    def sensor_width(self):
        return int.from_bytes(
            self.read(address=_xml_bootstrap_nodes_addresses["SensorWidth"], size=4, decode=False)[1],
            byteorder="little",
        )

    @property
    def sensor_height(self):
        return int.from_bytes(
            self.read(address=_xml_bootstrap_nodes_addresses["SensorHeight"], size=4, decode=False)[1],
            byteorder="little",
        )

    @property
    def line_length(self):  # in
        return int.from_bytes(
            self.read(address=_xml_sensor_nodes_addresses["LineLength"], size=2, decode=False)[1], byteorder="little"
        )

    @property
    def wait_time(self):  # in ms
        return (
            int.from_bytes(
                self.read(address=_xml_sensor_nodes_addresses["WaitTime"], size=2, decode=False)[1],
                byteorder="little",
            )
            * (self.line_length / self.clkref)
        ) * 1e-3

    @property
    def exposure_time(self):  # in ms
        return (
            int.from_bytes(
                self.read(address=_xml_sensor_nodes_addresses["ExposureTime"], size=2, decode=False)[1],
                byteorder="little",
            )
            * (self.line_length / self.clkref)
        ) * 1e-3

    @exposure_time.setter
    def exposure_time(self, value):  # in ms
        return self.write(
            address=_xml_sensor_nodes_addresses["ExposureTime"],
            data=np.uint16((value * self.clkref / self.line_length) * 1e3),
        )

    def close(self):
        super().__del__()

    def white_balance(self, red, green, blue):
        # Enable AWB and write red-gree-blue color gains
        # err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(0b1))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBredGain"], data=int(red * 1e6))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBgreenGain"], data=int(green * 1e6))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBblueGain"], data=int(blue * 1e6))
        return err

    def enable_white_balance(self, enable):
        # Enable AWB, active when acquisition is running
        if enable == 0:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(0))
        else:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(1))
        return err

    def do_white_balance(self, enable):
        # Enable AWB, active when acquisition is running
        if enable == 0:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(1))
        else:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(3))
        return err

    def read_sensor_reg(self, address):
        addr=address+_xml_sensor_nodes_addresses["BaseAddress"]
        rval=int.from_bytes(self.read(address=addr, size=2, decode=False)[1], byteorder="little", )
        # print("RD 0x{:05x} = 0x{:04x}".format(addr, rval))
        return rval

    def write_sensor_reg(self, address, value):
        addr=address+_xml_sensor_nodes_addresses["BaseAddress"]
        val = np.uint16(value)
        # print("WR 0x{:05x} = 0x{:04x}".format(addr, val))
        error = self.write(address=addr, data=val)
        return error

    def set_camera_format(self, format):
        err = self.write(address=_xml_bootstrap_nodes_addresses["PixelFormat"], data=xml_pixel_format_nbits[format])
        return err

    def set_trigger_source(self, source):
        #trigger source: 0=Trig_None 1=Trig_Generator 2=Trig_Ext1 4=Trig_Sensor_Rdy
        err = self.write(address=_xml_bootstrap_nodes_addresses["TriggerSource"], data=source)
        return err

    def set_trigger_mode(self, mode):
        #TRIG mode      0:no trig   1:forbidden   2:trig frame  tint by com interface    3:trig ITC  use both edge of trig
        address=0x03
        mask=0xF3FF # b11 / b10
        reg = self.read_sensor_reg(address)
        mode = mode << 10
        value = (reg & mask) + mode
        err = self.write_sensor_reg(address, value)
        return err

