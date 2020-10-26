# import unittest
# unittest.main('test_mfrc522')


import unittest
from machine import SoftSPI, Pin

from micropython_mfrc522.mfrc522 import MFRC522

class TestMFRC522(unittest.TestCase):
    def test_mfrc522_read(self):
        """
        test mfrc522 write properly writes a value
        """
        # Setup
        input('\nPLEASE PLACE CARD IN FRONT OF READER TO PROCEED AND PRESS ENTER WHEN READY')
        sck = Pin(18, Pin.OUT)
        mosi = Pin(23, Pin.OUT)
        miso = Pin(19, Pin.OUT)
        spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
        sda = Pin(21, Pin.OUT)

        # Instantiate
        reader = MFRC522(spi, sda)

        # Calls
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            if status == reader.OK:
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTHENT1A, 8, key, raw_uid) == reader.OK:
                        reader.stop_crypto1()
        
        # Asserts
        self.assertEqual(status, 0)
    
    def test_mfrc522_write(self):
        """
        test mfrc522 write properly writes a value
        """
        # Setup
        sck = Pin(18, Pin.OUT)
        mosi = Pin(23, Pin.OUT)
        miso = Pin(19, Pin.OUT)
        spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
        sda = Pin(21, Pin.OUT)

        # Instantiate
        reader = MFRC522(spi, sda)

        # Calls
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            if status == reader.OK:
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTHENT1A, 8, key, raw_uid) == reader.OK:
                        status = reader.write(8, b'\x08\x06\x07\x05\x03\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                        reader.stop_crypto1()
        
        # Asserts
        self.assertEqual(status, 0)