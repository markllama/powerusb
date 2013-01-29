#
# Library to control PowerUSB power strips
#
import sys


# manage inputs
from optparse import OptionParser

# work with XML DOM structures for configuration and automation
import lxml.etree as etree

# Use usb 0.4 until I can find the right way to split them
try:
    #import usb.core
    #import usb.util
    import usb.legacy as usb
except ImportError:
    import usb

class PowerUSBStrip:
    """
    Model a PowerUSB switchable power strip.
    """
    vendor_id = 0x04d8
    product_id = 0x003f
    
    def __init__(self, usbdevice, busnum=None, devnum=None):
        """
        busnum: Integer - index of this bus
        devnum: Integer - index of this device on the bus
        """
        self._usbdevice = usbdevice
        self._busnum = busnum
        self._devnum = devnum

        self._sockets = [PowerUSBOutlet(self, 1),
                         PowerUSBOutlet(self, 2),
                         PowerUSBOutlet(self, 3)]

    def sockets(self):
        return self._sockets

    @staticmethod
    def is_strip(device):
        return (device.idVendor == PowerUSBStrip.vendor_id and 
                device.idProduct == PowerUSBStrip.product_id)

    @staticmethod
    def scanbus():
        """
        Scan the USB bus and collect all PowerUSB strips
        Each bus can have zero or more devices any of which may be a power strip.
        Return the list of PowerUSB strips available
        """
        busses = usb.busses()
        strips = []
        for ibus in range(len(busses)):
            bus = busses[ibus]
            for idev in range(len(bus.devices)):
                dev = bus.devices[idev]
                if PowerUSBStrip.is_strip(dev):
                    strips.append(PowerUSBStrip(dev, ibus, idev))

        return strips

    def iSerialNumber(self):
        return self._usbdevice.iSerialNumber

    def reset():
        """Reset the entire strip"""

class PowerUSBOutlet:
    """
    A single outlet on a PowerUSB strip
    """

    def __init__(self, strip, port):
        self._strip = strip
        self._port = port

    def on():
        """Turn the outlet on"""

    def off():
        """Turn the outlet off"""

    def default(state=None):
        """get or set the default state"""

    



if __name__ == "__main__":
    
    #dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, find_all=True)
    #print dev
    strips = PowerUSBStrip.scanbus()
    print strips[0].iSerialNumber()
