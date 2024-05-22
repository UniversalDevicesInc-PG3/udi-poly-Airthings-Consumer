#!/usr/bin/env python3
"""
This is a NodeServer for Airthings Consumer API Polyglot v3 written in Python3
by JimBo.Automates jimbo.automates@gmail.com
"""

from udi_interface import Interface,LOGGER
import sys
import time
from nodes import VERSION, Controller

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        LOGGER.error("ERROR: Python 3.6 or greater is required not {}.{}".format(sys.version_info[0],sys.version_info[1]))
        sys.exit(1)
    try:
        polyglot = Interface([Controller])
        polyglot.start(VERSION)
        control = Controller(polyglot, 'controller', 'controller', 'Airthings Controller')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
