#
# Library to control PowerUSB power strips
#
import sys


# manage inputs
from optparse import OptionParser

# work with XML DOM structures for configuration and automation
import lxml.etree as etree

import pyudev

class PowerUSBStrip:
    """
    Model a PowerUSB switchable power strip.
    """
    vendor_id = "04d8"
    product_id = "003f"

    buffer_len = 256
    buffer_write = 65
    
    def __init__(self, usbdevice, busnum=None, devnum=None):
        """
        busnum: Integer - index of this bus
        devnum: Integer - index of this device on the bus
        """
        self._usbdevice = usbdevice
        self._busnum = busnum
        self._devnum = devnum

        self._outlets = [PowerUSBOutlet(self, 1),
                         PowerUSBOutlet(self, 2),
                         PowerUSBOutlet(self, 3)]

    @staticmethod
    def list_strips():
        """
        Search the udev list for power strip devices
        """
        context = pyudev.Context()
        usb_devices = context.list_devices(subsystem="usb")
        strips = [d for d in usb_devices 
                  if 'idVendor' in d.attributes.keys()
                  and d.attributes['idVendor'] == PowerUSBStrip.vendor_id
                  and d.attributes['idProduct'] == PowerUSBStrip.product_id]
        
        return strips

    def outlets(self):
        return self._outlets

    @staticmethod
    def get_interface():
        return Interface(vendor_id = PowerUSBStrip.vendor_id, 
                         product_id = PowerUSBStrip.product_id)

    def iSerialNumber(self):
        return self._usbdevice.iSerialNumber

    def reset():
        """Reset the entire strip"""
        pass

    def firmware_verson():
        """Read the power strip firmware version"""
        pass

    def model():
        """Read the power strip model"""
        pass

    def current():
        """Read the instantanious current from the whole strip"""
        pass

    def current_cumultive():
        """Read the cumulative current from the whole strip"""
        pass

    def reset_current_counter():
        """Reset the current counter"""
        pass

    def all_on():
        pass

    def all_off():
        pass

    def mode(value=None):
        """Set or get the 'mode'"""
        pass


class PowerUSBOutlet:
    """
    A single outlet on a PowerUSB strip
    """
    _on_code = ['A', 'C', 'E']
    _off_code = ['B', 'D', 'P']
    _defon_code = ['N', 'G', 'O']
    _defoff_code = ['F', 'Q', 'H']
    _read = [0xa1, 0xa2, 0xac]
    _read_pwrup = [0xa3, 0xa4, 0xad]

    def __init__(self, strip, port):
        self._strip = strip
        self._port = port

    def on():
        """Turn the outlet on"""

    def off():
        """Turn the outlet off"""

    def default(state=None):
        """get or set the default state"""

    def state():
        """Retrive the power state of the outlet"""
        pass
    



if __name__ == "__main__":

    set_debug(HID_DEBUG_ALL)
    set_debug_stream(sys.stdout)
    
    #dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, find_all=True)
    #print dev
    #strips = PowerUSBStrip.scanhid()
    #print strips
    interface = PowerUSBStrip.get_interface()
    interface.dump_tree(sys.stdout)
