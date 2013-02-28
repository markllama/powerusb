#
# hidapi ported to python
#

import usb

USB_CLASS_PER_INTERFACE = 0
USB_CLASS_HID = 3

USB_REQ_GET_STATUS =		0x00
USB_REQ_CLEAR_FEATURE =		0x01
#/* 0x02 is reserved */
USB_REQ_SET_FEATURE =		0x03
#/* 0x04 is reserved */
USB_REQ_SET_ADDRESS = 		0x05
USB_REQ_GET_DESCRIPTOR =       	0x06
USB_REQ_SET_DESCRIPTOR =       	0x07
USB_REQ_GET_CONFIGURATION =	0x08
USB_REQ_SET_CONFIGURATION =	0x09
USB_REQ_GET_INTERFACE =		0x0A
USB_REQ_SET_INTERFACE =		0x0B
USB_REQ_SYNCH_FRAME =		0x0C

USB_TYPE_STANDARD =		(0x00 << 5)
USB_TYPE_CLASS =		(0x01 << 5)
USB_TYPE_VENDOR	=		(0x02 << 5)
USB_TYPE_RESERVED =		(0x03 << 5)

USB_RECIP_DEVICE =		0x00
USB_RECIP_INTERFACE =		0x01
USB_RECIP_ENDPOINT =		0x02
USB_RECIP_OTHER	=		0x03

#/*
# * Various libusb API related stuff
# */

USB_ENDPOINT_IN	= 0x80
USB_ENDPOINT_OUT = 0x00

def hid_enumerate(vendor_id, product_id):

    # Find matching devices FIRST
    usb_devices = [d for b in usb.busses() for d in b.devices
                   if d.deviceClass == USB_CLASS_PER_INTERFACE
                   and d.idVendor == vendor_id and d.idProduct == product_id]

    
    hid_devices = []
    for d in usb_devices:
        for c in d.configurations:
            for ilist in c.interfaces:
                for interface in ilist:
                    if interface.interfaceClass == USB_CLASS_HID:
                        hid_devices.append(d)

    return [HIDDevice(d) for d in hid_devices]
            

class HIDDevice():

    def __init__(self, usb_device):
        self.usb_device = usb_device
        self.dh = None
        self.blocking = True
        
    @property
    def configuration(self):
        return self.usb_device.configurations[0]

    @property
    def interface(self):
        """Find the HID interface"""
        
        for ilist in self.configuration.interfaces:
            for interface in ilist:
                if interface.interfaceClass == USB_CLASS_HID:
                    return interface
        return None

    @property
    def input_endpoint(self):
        """Find the HID interface input endpoint"""
        for e in self.interface.endpoints:
            if e.address & 0x80 == USB_ENDPOINT_IN:
                return e
        return None

    @property
    def output_endpoint(self):
        """Find the HID interface input endpoint"""
        for e in self.interface.endpoints:
            if e.address & 0x80 == USB_ENDPOINT_OUT:
                return e
        return None

    def blocking(self, block=True):
        self.blocking = block

    def open(self):
        self.dh = self.usb_device.open()
        self.dh.claimInterface(0)

    def close(self):
        self.dh.releaseInterface()

    def write(self, buffer):
        """Write to the interrupt output endpoint"""
        self.dh.interruptWrite(
            self.output_endpoint.address, 
            buffer + chr(0xff) * (64 - len(buffer)))

    def read(self, size):
        return self.dh.interruptRead(self.input_endpoint.address, 64)

    @staticmethod
    def devices(vendor_id=None, product_id=None):
        usb_devices = [d for b in usb.busses() for d in b.devices
                       if d.deviceClass == USB_CLASS_PER_INTERFACE
                       and d.idVendor == vendor_id 
                       and d.idProduct == product_id]

        return [HIDDevice(u) for u in usb_devices]
        
