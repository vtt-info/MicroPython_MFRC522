from machine import Pin, SoftSPI

from micropython_mfrc522.mfrc522 import MFRC522

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
sda = Pin(21, Pin.OUT)
reader = MFRC522(spi, sda)

print('')
print('Place Card To Write Address - 0x08')
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
                    if reader.auth(reader.AUTHENT1A, 8, key, raw_uid) == reader.OK:
                        status = reader.write(8, b'\x08\x06\x07\x05\x03\x00\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                        reader.stop_crypto1()
                        print(status)
                        print(reader.OK)
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