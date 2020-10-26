![image](https://github.com/mytechnotalent/MicroPython_MFRC522/blob/main/MicroPython_MFRC522.png?raw=true)

# MicroPython MFRC522
An MFRC522 device driver library for MicroPython.

## Introduction
The MFRC522 is a specialized chip that reads and writes RFID data over SPI. Its available on [Amazon](https://www.amazon.com/SunFounder-Mifare-Reader-Arduino-Raspberry/dp/B07KGBJ9VG).

## Installation & Dependencies
This driver depends on:
* [MicroPython](https://github.com/micropython/micropython)

## Usage Examples
```python
from machine import Pin, SoftSPI

from micropython_mfrc522.mfrc522 import MFRC522

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

while True:
    try:
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            if status == reader.OK:
                print('New Card Detected')
                print('  - Tag Type: 0x%02x' % tag_type)
                print('  - uid: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                print('')
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTH, 8, key, raw_uid) == reader.OK:
                        print("Address Data: %s" % reader.read(8))
                        reader.stop_crypto1()
                    else:
                        print("AUTH ERROR")
                else:
                    print("FAILED TO SELECT TAG")
    except KeyboardInterrupt:
        break
```
```python
from machine import Pin, SoftSPI

from micropython_mfrc522.mfrc522 import MFRC522

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

print('')
print('Place Card In Front Of Device To Write Unique Address')
print('')

while True:
    try:
        (status, tag_type) = reader.request(reader.CARD_REQIDL)
        if status == reader.OK:
            (status, raw_uid) = reader.anticoll()
            if status == reader.OK:
                print('New Card Detected')
                print('  - Tag Type: 0x%02x' % tag_type)
                print('  - UID: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                print('')
                if reader.select_tag(raw_uid) == reader.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    if reader.auth(reader.AUTH, 8, key, raw_uid) == reader.OK:
                        # Write your unique address here
                        status = reader.write(8, b'\x08\x06\x07\x05\x03\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                        reader.stop_crypto1()
                        if status == reader.OK:
                            print('Data Written To Card...')
                        else:
                            print('FAILED TO WRITE DATA')
                    else:
                        print('AUTH ERROR')
                else:
                    print('FAILED TO SELECT TAG')
    except KeyboardInterrupt:
        break
```
