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
copi = Pin(23, Pin.OUT) # Controller out, peripheral in
cipo = Pin(19, Pin.OUT) # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

print('Place Card In Front Of Device To Read Unique Address')
print('')

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
copi = Pin(23, Pin.OUT) # Controller out, peripheral in
cipo = Pin(19, Pin.OUT) # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

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

### Hardware Set-up
Connect 3.3 V to 3.3 V power source, GND to ground, SCK, COPI, CIPO, SPI and SDA to the appropriate pins.

### Basics
You must import machine, SoftSPI, Pin and the library:
```python
from machine import SoftSPI, Pin
```
To set-up the device to gather data, initialize the SoftI2CDevice using SDA, SCK, COPI and CIPO pins and then initialize the library to provide new data ready to be read or write.

### Read
To read the unique address data:
```python
print("Address Data: %s" % reader.read(8))
```

### Write
To write the unique address data:
```python
status = reader.write(8, b'\x08\x06\x07\x05\x03\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00')
```

## Run Tests in REPL
```bash
import unittest
unittest.main('test_mfrc522')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT License](https://github.com/mytechnotalent/MicroPython_MPU6050/blob/main/LICENSE)
