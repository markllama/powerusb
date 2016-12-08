#
# hidapi
#   adapted and partially ported to Python by
#   Mark Lamourine <markllama@gmai.com>
#
# Originally from:
#/*******************************************************
# HIDAPI - Multi-Platform library for
# communication with HID devices.
#
# Alan Ott
# Signal 11 Software
#
# 8/22/2009
# Linux Version - 6/2/2010
# Libusb Version - 8/13/2010
#
# Copyright 2009, All Rights Reserved.
#
# At the discretion of the user of this library,
# this software may be licensed under the terms of the
# GNU Public License v3, a BSD-Style license, or the
# original HIDAPI license as outlined in the LICENSE.txt,
# LICENSE-gpl3.txt, LICENSE-bsd.txt, and LICENSE-orig.txt
# files located at the root of the source distribution.
# These files may also be found in the public source
# code repository located at:
#        http://github.com/signal11/hidapi .
#********************************************************/

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

    hid_devices = []

    busses = list(usb.busses())

    # check each bus
    for b_index in range(0, len(busses)):
        bus = busses[b_index]
        # check each device on a bus
        for d_index in range(0, len(bus.devices)):
            device = bus.devices[d_index]

            # If the device matches all criteria
            if device.deviceClass == USB_CLASS_PER_INTERFACE \
                and device.idVendor == vendor_id \
                and device.idProduct == product_id:

                for c in device.configurations:
                    for ilist in c.interfaces:
                        for interface in ilist:
                            if interface.interfaceClass == USB_CLASS_HID:
                                hid_devices.append(
                                    HIDDevice(device, b_index, d_index))

    return hid_devices


class HIDDevice():

    _timeout = 0 # milliseconds (0 = no timeout)

    def __init__(self, usb_device, bus_index=None, device_index=None):
        self.usb_device = usb_device
        self.dh = None
        self.blocking = True
        self.busnum = bus_index
        self.devnum = device_index

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
        try:
            self.dh.interruptWrite(
                self.output_endpoint.address,
                buffer + chr(0xff) * (64 - len(buffer)),
                HIDDevice._timeout
                )
        except usb.USBError():
            raise

    def read(self, size):

        try:
            outstring = self.dh.interruptRead(self.input_endpoint.address,
                                              64, HIDDevice._timeout)
        except usb.USBError(e):
            pass

        return outstring

    @staticmethod
    def devices(vendor_id=None, product_id=None):
        usb_devices = [d for b in usb.busses() for d in b.devices
                       if d.deviceClass == USB_CLASS_PER_INTERFACE
                       and d.idVendor == vendor_id
                       and d.idProduct == product_id]

        return [HIDDevice(u) for u in usb_devices]


