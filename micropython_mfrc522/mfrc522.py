# The MIT License (MIT)
#
# Copyright (c) 2020 My Techno Talent, LLC For MicroPython
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`MFRC522`
====================================================
Driver class for the MFRC522 board.  RF tag reader and writer.

* Author(s): Kevin Thomas
"""
from machine import Pin, SPI
from os import uname

__version__ = "1.0.0"
__repo__ = "https://github.com/mytechnotalent/MicroPython_MFRC522.git"

MAX_LEN							= 16
CALCULATE_CRC					= 0x03
ANTICOLL						= 0x93
SELECT_TAG						= 0x93
TRANSCEIVE						= 0x0C
AUTHENTICATE					= 0x0E
READ							= 0x30
WRITE							= 0xA0

MFRC522_COMMAND_REG				= 0x01
MFRC522_COML_EN_REG				= 0x02
MFRC522_DIVL_EN_REG				= 0x03
MFRC522_COM_IRQ_REG				= 0x04
MFRC522_DIV_IRQ_REG				= 0x05
MFRC522_ERROR_REG				= 0x06
MFRC522_STATUS_2_REG			= 0x08	
MFRC522_FIFO_DATA_REG			= 0x09
MFRC522_FIFO_LEVEL_REG			= 0x0A
MFRC522_CONTROL_REG 			= 0x0C
MFRC522_BIT_FRAMING_REG 		= 0x0D
MFRC522_MODE_REG				= 0x11
MFRC522_TX_CONTROL_REG			= 0x14
MFRC522_TX_AUTO_REG				= 0x15
MFRC522_CRC_RESULT_REG_H		= 0x21
MFRC522_CRC_RESULT_REG_L		= 0x22
MFRC522_T_MODE_REG 				= 0x2A
MFRC522_T_PRESCALAR_REG 		= 0x2B
MFRC522_T_RELOAD_REG_H			= 0x2C
MFRC522_T_RELOAD_REG_L			= 0x2D


class MFRC522:
	"""
	A class used to represent the MFRC522

	...

	Attributes
	----------
	spi : <class 'SoftSPI'>
		Instance of the SoftSPI class
	cs : int
		Chip select

	Methods
	-------
	# TODO FIX
	# combine_register_values(self, temp_h, temp_l)
		# Combine reg values
	"""
	OK 							= 0
	NO_TAG_ERR 					= 1
	ERR 						= 2
	CARD_REQIDL					= 0x26
	AUTH 						= 0x60
	

	def __init__(self, spi, cs):
		"""
		Parameters
		----------
		spi : <class 'SoftSPI'>
			Instance of the SoftSPI class
		cs : int
			Chip select
		"""
		self.spi = spi
		self.cs = cs
		self.cs.value(1)
		self.spi.init()
		self.init()

	def _write_reg(self, reg, val):
		"""Write value into register

		Parameters
		----------
		reg : int
			Register
		val : int
			Value

		Returns
		-------
		None
		"""
		self.cs.value(0)
		self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
		self.spi.write(b'%c' % int(0xff & val))
		self.cs.value(1)

	def _read_reg(self, reg):
		"""Read value from register

		Parameters
		----------
		reg : int
			Register

		Returns
		-------
		None
		"""
		self.cs.value(0)
		self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
		val = self.spi.read(1)
		self.cs.value(1)
		return val[0]

	def _set_bit_mask(self, reg, mask):
		"""Set the bit mask

		Parameters
		----------
		reg : int
			Register
		mask : int
			Mask

		Returns
		-------
		None
		"""
		self._write_reg(reg, self._read_reg(reg) | mask)

	def _clear_bit_mask(self, reg, mask):
		"""Clear the bit mask

		Parameters
		----------
		reg : int
			Register
		mask : int
			Mask

		Returns
		-------
		None
		"""
		self._write_reg(reg, self._read_reg(reg) & (~mask))

	def _tocard(self, cmd, send):
		"""To card

		Parameters
		----------
		cmd : int
			Command
		send : int
			Send data

		Returns
		-------
		tuple
			Returns a tuple of status, recv, bits
		"""
		recv = []
		bits = irq_en = wait_irq = n = 0
		status = self.ERR
		if cmd == AUTHENTICATE:
			irq_en = 0x12
			wait_irq = 0x10
		elif cmd == TRANSCEIVE:
			irq_en = 0x77
			wait_irq = 0x30
		self._write_reg(MFRC522_COML_EN_REG, irq_en | 0x80)
		self._clear_bit_mask(MFRC522_COM_IRQ_REG, 0x80)
		self._set_bit_mask(MFRC522_FIFO_LEVEL_REG, 0x80)
		self._write_reg(MFRC522_COMMAND_REG, 0x00)
		for c in send:
			self._write_reg(MFRC522_FIFO_DATA_REG, c)
		self._write_reg(MFRC522_COMMAND_REG, cmd)
		if cmd == TRANSCEIVE:
			self._set_bit_mask(MFRC522_BIT_FRAMING_REG, 0x80)
		i = 2000
		while True:
			n = self._read_reg(MFRC522_COM_IRQ_REG)
			i -= 1
			if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
				break
		self._clear_bit_mask(MFRC522_BIT_FRAMING_REG, 0x80)
		if i:
			if (self._read_reg(MFRC522_ERROR_REG) & 0x1B) == 0x00:
				status = self.OK
				if n & irq_en & 0x01:
					status = self.NOTAGERR
				elif cmd == TRANSCEIVE:
					n = self._read_reg(MFRC522_FIFO_LEVEL_REG)
					last_bits = self._read_reg(MFRC522_CONTROL_REG) & 0x07
					if last_bits != 0:
						bits = (n - 1) * 8 + last_bits
					else:
						bits = n * 8
					if n == 0:
						n = 1
					elif n > MAX_LEN:
						n = MAX_LEN
					for _ in range(n):
						recv.append(self._read_reg(MFRC522_FIFO_DATA_REG))
			else:
				status = self.ERR
		return status, recv, bits

	def _calculate_crc(self, data):
		"""Calculate CRC

		Parameters
		----------
		data : int
			Data

		Returns
		-------
		int
			Returns an int read_reg
		"""
		self._clear_bit_mask(MFRC522_DIV_IRQ_REG, 0x04)
		self._set_bit_mask(MFRC522_FIFO_LEVEL_REG, 0x80)
		for c in data:
			self._write_reg(MFRC522_FIFO_DATA_REG, c)
		self._write_reg(MFRC522_COMMAND_REG, CALCULATE_CRC)
		i = 0xFF
		while True:
			n = self._read_reg(MFRC522_DIV_IRQ_REG)
			i -= 1
			if not ((i != 0) and not (n & MFRC522_COM_IRQ_REG)):
				break
		return [self._read_reg(MFRC522_CRC_RESULT_REG_L), self._read_reg(MFRC522_CRC_RESULT_REG_H)]

	def init(self):
		"""
		Parameters
		----------
		None
		"""
		self.reset()
		self._write_reg(MFRC522_T_MODE_REG, 0x8D)
		self._write_reg(MFRC522_T_PRESCALAR_REG, 0x3E)
		self._write_reg(MFRC522_T_RELOAD_REG_L, 30)
		self._write_reg(MFRC522_T_RELOAD_REG_H, 0)
		self._write_reg(MFRC522_TX_AUTO_REG, 0x40)
		self._write_reg(MFRC522_MODE_REG, 0x3D)
		self.antenna_on()

	def reset(self):
		"""Reset

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		self._write_reg(MFRC522_COMMAND_REG, 0x0F)

	def antenna_on(self, on=True):
		"""Turn antenna on

		Parameters
		----------
		on : bool
			Antenna on/off flag

		Returns
		-------
		None
		"""
		if on and ~(self._read_reg(MFRC522_TX_CONTROL_REG) & 0x03):
			self._set_bit_mask(MFRC522_TX_CONTROL_REG, 0x03)
		else:
			self._clear_bit_mask(MFRC522_TX_CONTROL_REG, 0x03)

	def request(self, mode):
		"""Method to start the transmission of data

		Parameters
		----------
		mode : list
			Mode

		Returns
		-------
		int
			Returns an int of status and bit
		"""
		self._write_reg(MFRC522_BIT_FRAMING_REG, 0x07)
		(status, recv, bits) = self._tocard(MFRC522_CONTROL_REG, [mode])
		if (status != self.OK) | (bits != 0x10):
			status = self.ERR
		return status, bits

	def anticoll(self):
		"""Anticoll

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		serial_number_check = 0
		serial_number = [ANTICOLL, 0x20]
		self._write_reg(MFRC522_BIT_FRAMING_REG, 0x00)
		(status, recv, bits) = self._tocard(TRANSCEIVE, serial_number)
		if status == self.OK:
			if len(recv) == 5:
				for i in range(4):
					serial_number_check = serial_number_check ^ recv[i]
				if serial_number_check != recv[4]:
					status = self.ERR
			else:
				status = self.ERR
		return status, recv

	def select_tag(self, serial_number):
		"""Select tag

		Parameters
		----------
		serial_number : int
			Serial number

		Returns
		-------
		bool
			Returns a bool if OK or ERR if error
		"""
		buffer = [SELECT_TAG, 0x70] + serial_number[:5]
		buffer += self._calculate_crc(buffer)
		(status, recv, bits) = self._tocard(TRANSCEIVE, buffer)
		return self.OK if (status == self.OK) and (bits == 0x18) else self.ERR

	def auth(self, mode, addr, sect, serial_number):
		"""Auth

		Parameters
		----------
		mode : int
			Mode
		addr : int
			Addr
		sect : int
			Sect
		serial_number : int
			Serial number

		Returns
		-------
		bool
			Returns a bool if OK or ERR if error
		"""
		return self._tocard(AUTHENTICATE, [mode, addr] + sect + serial_number[:4])[0]

	def stop_crypto1(self):
		"""Stop crypto 1

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		self._clear_bit_mask(MFRC522_STATUS_2_REG, 0x08)

	def read(self, addr):
		"""Read

		Parameters
		----------
		addr : int
			Addr

		Returns
		-------
		bool
			Returns a bool if OK or None
		"""
		data = [READ, addr]
		data += self._calculate_crc(data)
		(status, recv, _) = self._tocard(TRANSCEIVE, data)
		return recv if status == self.OK else None

	def write(self, addr, data):
		"""Write

		Parameters
		----------
		addr : int
			Addr
		data : bytes
			Data

		Returns
		-------
		int
			Returns an int of the status
		"""
		buffer = [WRITE, addr]
		buffer += self._calculate_crc(buffer)
		(status, recv, bits) = self._tocard(TRANSCEIVE, buffer)
		if not (status == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
			status = self.ERR
		else:
			buffer = []
			for i in range(MAX_LEN):
				buffer.append(data[i])
			buffer += self._calculate_crc(buffer)
			(status, recv, bits) = self._tocard(TRANSCEIVE, buffer)
			if not (status == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
				status = self.ERR
		return status