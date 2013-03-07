#!/usr/bin/python
"""
Control one or more PowerUSB power strips

* display the set of connected strips

* Turn a socket on or off
* Read the power state of a socket
* Set the default for a socket
* Turn an entire strip on or off
* read the cumulative power from a strip

* Assign a label to a strip

powerusb --strips

powerusb --status <strip>[:<socket>]

powerusb --socket <strip>:<socket> (-on|-off) [--default]

powerusb --meter <strip> [--cumulative|--reset]]

"""

import argparse
import re
import time
import xml.dom.minidom as xml
import lxml.etree as etree

import json
import hidapi

##############################################################################
#
# Argument Parsing
#
##############################################################################

class CommandAction(argparse.Action):
    """
    Parse one of the 5 command actions
    """
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.command = re.sub("^--", "", option_string)
        namespace.socket = values

def parse_command_line():
    """Parse the command line arguments"""

    parser = argparse.ArgumentParser(description="Manage power strips")
    parser.add_argument("--verbose", "-v", action="store_true")
    fmt_group = parser.add_mutually_exclusive_group()
    fmt_group.add_argument("--text", "-t", dest="format", 
                           action="store_const", const="text", default="text", )
    fmt_group.add_argument("--xml", "-x", dest="format", 
                           action="store_const", const="xml")
    fmt_group.add_argument("--json", "-j", dest="format",
                           action="store_const", const="json")
    cmd_group = parser.add_mutually_exclusive_group()

    cmd_group.add_argument("--list_strips", "-l", action="store_true")
    cmd_group.add_argument("--strip", '-s', metavar="STRIPSPEC", 
                           action=CommandAction, dest="command", nargs="+")
    strip_actions = parser.add_mutually_exclusive_group()
    strip_actions.add_argument("--current", const="current",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--power", const="power",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--reset_power", const="resetpower",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--get_overload", const="getoverload",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--set_overload", const="setoverload",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--set_current_ratio", const="setcurrratio",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--reset", const="resetstrip",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--set_current_offset", const="setcurroffset",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--allon", const="allon",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--alloff", const="alloff",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--set_mode", const="setmode",
                               dest="stripcmd", action="store_const")
    strip_actions.add_argument("--get_mode", const="getmode",
                               dest="stripcmd", action="store_const")

    cmd_group.add_argument("--socket", "-p", metavar="SOCKETSPEC",
                           action=CommandAction, dest="command", nargs="+")
    cmd_group.add_argument("--meter", "-m", metavar="SOCKETSPEC",
                           action=CommandAction, dest="command", nargs="+")

    on_off = parser.add_mutually_exclusive_group()
    on_off.add_argument("--on", dest="on", action="store_true", default=None) 
    on_off.add_argument("--off", dest="on", action="store_false")
    parser.add_argument("--default", action="store_true")
    parser.add_argument("--cumulative", action="store_true")
    #parser.add_argument("--reset", action="store_true")
    parser.add_argument("--debug", "-d", action="store_true", default=False)
    return parser.parse_args()

###############################################################################
#
# PowerUSB Commands
#
###############################################################################

def strip_status(format):
    strips = PowerUSBStrip.strips()
    
    if format == "text":
        print "%d device(s) connected" % len(strips)
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            print "%d) %s" % (i, strip)
            strip.close()

    elif format == "xml":
        #stripxml = xml.Element("powerstrips")
        #for i in range(0, len(strips)):
        #    strip = strips[i]
        #    strip.open()
        #    stripxml.appendChild(strip.xml())
        #    strip.close()
        #print stripxml.toprettyxml(indent="  ")
        
        stripxml = etree.Element("powerstrips")
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            stripxml.append(strip.etree())
            strip.close()

        etree.dump(stripxml, pretty_print=True)
        print ""
        

###############################################################################
#
# MAIN
#
###############################################################################

if __name__ == "__main__":

    opts = parse_command_line()

    if opts.debug: print opts

    if opts.list_strips == True:
        strip_status(opts.format)
    elif opts.command == 'status':
        # validate the socket spec
        print opts.command + ": " + opts.socket[0]

    elif opts.command == 'socket':

        strips = PowerUSBStrip.strips()

        for currspec in opts.socket:
            busstr, devstr, sockstr = currspec.split(':')
            busnum = int(busstr)
            devnum = int(devstr)
            socknum = int(sockstr)

            matchstrips = [s for s in strips if s.busnum == busnum and s.devnum == devnum]

            if len(matchstrips) != 1:
                print "error: more than one strip matches %s" % currespec
                continue

            currstrip = matchstrips[0]
            currstrip.open()
            # get the strip containing the socket

            if opts.on == None:
                # request the power state for the socket
                if opts.default:
                    print "strip %s:%s socket %s: %s (default)" % (
                        busstr, devstr, sockstr, currstrip.socket[socknum].power)
                else:
                    print "strip %s:%s socket %s: %s" % (
                        busstr, devstr, sockstr, currstrip.socket[socknum].power)

            elif opts.on == True:
                if opts.default:
                    # set the socket default on
                    currstrip.socket[socknum].default = "on"
                else:
                    # set the socket on
                    currstrip.socket[socknum].power = "on"

            elif opts.on == False:
                if opts.default:
                    # set the socket default on
                    currstrip.socket[socknum].default = "off"
                else:                                         
                    # set the socket off
                    currstrip.socket[socknum].default = "off"



            currstrip.close()
