import logging
import struct

LOG = logging.getLogger(__name__)


class SpiDev (object):
    '''This is a simple wrapper for accessing SPI devices using the Linux
    spidev kernel driver, described at:

    <https://www.kernel.org/doc/Documentation/spi/spi-summary>'''

    def __init__(self, bus, dev):
        self.bus = bus
        self.dev = dev
        self.fd = -1

        self.open()

    def open(self):
        LOG.debug('opening SPI device %d.%d',
                  self.bus, self.dev)
        assert(self.fd == -1)
        self.fd = open(
            '/dev/spidev%d.%d' % (self.bus, self.dev),
            'w')

    def write(self, bytes):
        assert(self.fd != -1)
        self.fd.write(
            struct.pack('%ds' % len(bytes),
                        ''.join(chr(x) for x in bytes)))
        self.fd.flush()

    def read(self, len=None):
        raise NotImplementedError()

    # compatability with spidev module
    writebytes = write

    def close(self):
        LOG.debug('closing SPI device %d.%d',
                  self.bus, self.dev)
        self.fd.close()
        self.fd = -1

    def fileno(self):
        return self.fd

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
