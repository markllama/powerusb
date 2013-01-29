#
# Library to control PowerUSB power strips
#
import sys


# manage inputs
from optparse import OptionParser

# work with XML DOM structures for configuration and automation
import lxml.etree as etree

try:
    import usb.core
    import usb.util
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

    @staticmethod
    def is_strip(device):
        return (device.idVendor == PowerUSBStrip.vendor_id and 
                device.idProduct == PowerUSBStrip.product_id)

    @staticmethod
    def scanbus():
        """
        Scan the USB bus and collect all PowerUSB strips
        Each bus can have zero or more devices any of which may be a power strip.
        """
        
        devices = [device for bus in usb.busses() for device in bus.devices]
        
        strips = [PowerUSBStrip(device) for device in devices if PowerUSBStrip.is_strip(device)]

        return strips

    def iSerialNumber(self):
        return self._usbdevice.iSerialNumber

class PowerUSBOutlet:

    def __init__(self, strip, port):
        self._strip = strip
        self._port = port

vendor_id = 0x04d8
product_id = 0x003f


if __name__ == "__main__":
    
    #dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, find_all=True)
    #print dev
    strips = PowerUSBStrip.scanbus()
    print strips[0].iSerialNumber()
