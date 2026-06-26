import time
import serial
import pty
import os
from serial_reader import SerialReaderThread
from PySide6.QtCore import QCoreApplication
import sys

# We can just emit the regex string directly to see if UI changes
print("Run a quick test")
