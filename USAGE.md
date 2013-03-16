# Query and control PowerUSB power strips

__NOTE__: a number of features are TBD

## Identifying strips and sockets

Each strip is identified by the USB bus and device numbers. A strip ID
is the bus number and device number separated by a colon:

    0:1 # The power strip on bus 0, device 1

Each strip has 3 controllable sockets, numbered 1-3. A socket is
identified by the strip ID followed by a colon and the socket number.

    0:1:2 # Socket 2 on power strip 0:1

* Get the list of connected strips and status

    powerusb [--list-strips]

## Strip Commands

   powerusb --strip <strip id> [on|off|reset|current|power|clear] __(TBD)__

## Socket Commands

    powerusb --socket <socket id> [on|off]

## Output formats __(TBD)__

You can select the output format for queries:

* __--text__: Print human readable status to stdout [default]
* __--xml__: Print an XML document to stdout
* __--json__: Print a JSON stream to stdout
* __--syslog__: log the current status
* __--format <format>__: select _text_, _xml_, _json_ or _syslog_