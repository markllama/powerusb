#!/usr/bin/python
#
#
import unittest
import mock

import hidapi

class TestHIDDevice(unittest.TestCase):
    
    def testConstructor(self):
        
        usb_device = object()
        d = hidapi.HIDDevice(usb_device)
        

if __name__ == "__main__":

    unittest.main()
