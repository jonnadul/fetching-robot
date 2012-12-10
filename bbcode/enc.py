#! /usr/bin/python
# Based on MMAP code from https://groups.google.com/forum/#!msg/beagleboard/alKf67dwMHI/b9W2igN6Lr4J
from mmap import mmap
from collections import namedtuple
import struct

MMAP_OFFSET = 0x44c00000                # base address of registers
MMAP_SIZE   = 0x48ffffff-MMAP_OFFSET    # size of the register memory space
CM_PER_BASE = 0x44e00000 - MMAP_OFFSET
CM_PER_EPWMSS1_CLKCTRL = CM_PER_BASE + 0xcc
CM_PER_EPWMSS0_CLKCTRL = CM_PER_BASE + 0xd4
CM_PER_EPWMSS2_CLKCTRL = CM_PER_BASE + 0xd8
CONTROL_MODULE_BASE = 0x44e10000 - MMAP_OFFSET
PWMSS_CTRL = 0x664
PWMSS0_BASE = 0x48300000 - MMAP_OFFSET
PWMSS1_BASE = 0x48302000 - MMAP_OFFSET
PWMSS2_BASE = 0x48304000 - MMAP_OFFSET
CLKCONFIG = 0x8
CLKSTATUS = 0xC
EPWM2_BASE = 0x48304200 - MMAP_OFFSET
EQEP0_BASE = 0x48300180 - MMAP_OFFSET
EQEP1_BASE = 0x48302180 - MMAP_OFFSET
EQEP2_BASE = 0x48304180 - MMAP_OFFSET
DMTIMER2_BASE = 0x48040000 - MMAP_OFFSET
DMTIMER2_ID     = DMTIMER2_BASE + 0x0
DMTIMER2_TCTRLR = DMTIMER2_BASE + 0x38
DMTIMER2_TCNTRR = DMTIMER2_BASE + 0x3C
QPOSCNT = 0x0
QPOSINIT = 0x4
QPOSMAX = 0x8
QPOSCMP = 0xC
QPOSILAT = 0x10
QPOSSLAT = 0x14
QPOSLAT = 0x18
QUTMR = 0x1C
QUPRD = 0x20
QWDTMR = 0x24
QWDPRD = 0x26
QDECCTL = 0x28
QEPCTL = 0x2a
QCAPCTL = 0x2c
QPOSCTL = 0x2e
QEINT = 0x30
QFLG = 0x32
QCLR = 0x34
QFRC = 0x36
QEPSTS = 0x38
QCTMR = 0x3A
QCPRD = 0x3C
QCTMRLAT = 0x3E
QCPRDLAT = 0x40
REVID = 0x5C
Encoder = namedtuple('EncoderCounts','Left Right')
with open("/dev/mem", "r+b") as f:
	mem = mmap(f.fileno(), MMAP_SIZE, offset=MMAP_OFFSET)
def _andReg(address, mask):
	""" Sets 32-bit Register at address to its current value AND mask. """
	_setReg(address, _getReg(address)&mask)
def _orReg(address, mask):
	""" Sets 32-bit Register at address to its current value OR mask. """
	_setReg(address, _getReg(address)|mask)
def _xorReg(address, mask):
	""" Sets 32-bit Register at address to its current value XOR mask. """
	_setReg(address, _getReg(address)^mask)
def _getReg(address):
	""" Returns unpacked 32 bit register value starting from address. """
	return struct.unpack("<L", mem[address:address+4])[0]
def _setReg(address, new_value):
	""" Sets 32 bits at given address to given value. """
	mem[address:address+4] = struct.pack("<L", new_value)
def pollEnc():
	encoders = Encoder(Left = _getReg(EQEP2_BASE+QPOSCNT), Right = _getReg(EQEP1_BASE+QPOSCNT))
	#print 'Count: ' + hex(encoders.Left) + ' ' + hex(encoders.Right)
	return encoders
def setEnc(Left, Right):
	_setReg(EQEP2_BASE+QPOSCNT, Left)
	_setReg(EQEP1_BASE+QPOSCNT, Right)
def startTimer():
	_setReg(DMTIMER2_TCNTRR, 0x00000000)
	_setReg(DMTIMER2_TCTRLR, 0x03)
def stopTimer():
	_setReg(DMTIMER2_TCTRLR, 0x02)
	return _getReg(DMTIMER2_TCNTRR)
def getTimerID():
	return _getReg(DMTIMER2_ID)
