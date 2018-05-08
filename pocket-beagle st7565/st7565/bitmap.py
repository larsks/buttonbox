import logging
import st7565.bitops as bitops

LOG = logging.getLogger(__name__)


class Bitmap (list):

    def __init__(self, pages=8, columns=128):
        '''Create an ST7565-compatible bitmap.  Each *page* contains
        *columns* bytes, and each byte represents a column of eight pixels.
        In other words:

                      COLUMN 1 | COLUMN 2
                   7     .     |    .
                   6     .     |    .
                   5     .     |    .
            PAGE 1 4     .     |    .
                   3     .     |    .
                   2     .     |    .
                   1     .     |    .
                   0     .     |    .
                   ------------|----------
                   7     .     |    .
                   6     .     |    .
                   5     .     |    .
            PAGE 2 4     .     |    .
                   3     .     |    .
                   2     .     |    .
                   1     .     |    .
                   0     .     |    .

        This buffer can be written directly to the LCD using the
        `st7565.lcd.LCD.write_buffer` method.
        '''

        self.pages = pages
        self.columns = columns
        self.width = columns
        self.height = 8 * pages

        super(Bitmap, self).__init__([0] * pages * columns)

    def clear(self):
        '''Clear the buffer (reset all locations to 0).'''
        self[:] = [0] * self.pages * self.columns

    def set_pixel(self, x, y, pen=True):
        '''Set (or unset, if `pen` == `False`) a single pixel.'''
        if x < 0 or x > self.width:
            raise ValueError(x)
        if y < 0 or y > self.height:
            raise ValueError(y)

        col = x
        page = y/8

        i = (page * self.columns) + col

        if pen:
            self[i] |= 1 << (7-(y % 8))
        else:
            self[i] &= ~(1 << (7-(y % 8)))

    def vline(self, x, y, len, pen=True):
        '''Create a vertical line starting at position `(x,y)` and extending
        for `len` pixels.'''
        LOG.debug('vline from (%d,%d) length %d',
                  x, y, len)
        for l in range(len):
            self.set_pixel(x, y+l, pen)

    def hline(self, x, y, len, pen=True):
        '''Create a horizontal line starting at position `(x,y)` and extending
        for `len` pixels.'''
        LOG.debug('hline from (%d,%d) length %d',
                  x, y, len)
        for l in range(len):
            self.set_pixel(x+l, y, pen)

    def box(self, x1, y1, x2, y2, pen=True):
        '''Create a box with upper left corner at position `(x1, y1)`
        and bottom right corner at position `(x2, y2)`.  Set pixels if
        `pen` == `True`, unset pixels if `pen` == `False`.'''
        LOG.debug('box from (%d, %d) to (%d, %d)',
                  x1, y1, x2, y2)
        self.hline(x1, y1, (x2-x1) + 1, pen)
        self.hline(x1, y2, (x2-x1) + 1, pen)
        self.vline(x1, y1, (y2-y1) + 1, pen)
        self.vline(x2, y1, (y2-y1) + 1, pen)

    def drawbitmap(self, img, tx=0, ty=0, centerx=False, centery=False):
        '''Render an image (a `PIL.Image.Image` instance) onto the buffer,
        with upper left at position `(tx, ty)`.  Center the image
        horizontally if `centerx` is `True`, and center the image
        vertically if `centery` is True.
        
        The image must be no larger than the size of the bitmap buffer, and
        must be a mode '1' (monochrome) image.'''

        LOG.debug('render image of size (%d, %d) at position (%d, %d).',
                  *(img.size + (tx, ty)))
        # convert to black and white
        img = img.convert('1')
        img_x, img_y = img.size

        # bail out if the image is too big
        if img_x > self.width or img_y > self.height:
            raise ValueError('image is too large: (%d,%d) '
                             'is larger than (%d, %d)' % (
                                 img_x, img_y,
                                 self.width, self.height))

        if centerx:
            tx = self.width/2 - img_x/2

        if centery:
            ty = self.height/2 - img_y/2

        imgdata = list(img.getdata())
        for x in range(img_x):
            for y in range(img_y):
                pen = imgdata[(y*img_x) + x]
                self.set_pixel(tx+x, ty+y, pen == 0)

    def vscroll(self, steps=1):
        '''Scroll the bitmap buffer vertically by `steps` pixels.'''
        for col in range(self.columns):
            bits = self[col::self.columns]
            if steps > 0:
                self[col::self.columns] = bitops.rotater(bits, steps)
            elif steps < 0:
                self[col::self.columns] = bitops.rotatel(bits, abs(steps))

    def hscroll(self, steps=1):
        '''Scroll the bitmap buffer horizontally by `steps` pixels.'''
        steps = 0-steps
        for page in range(self.pages):
            t = self[page * self.columns:(page * self.columns) + self.columns]
            t = t[steps:] + t[:steps]
            self[page * self.columns:(page * self.columns) + self.columns] = t

    def dump(self, chars=None):
        '''Print an ASCII representation of the bitmap buffer.  Good for
        debugging.  Normally prints `.` for unset pixels and `#` for set
        pixels, but you can pass a two-character string to `chars` to
        change these defaults.'''
        if chars is None:
            chars = '.#'
        lines = []
        for page in range(self.pages):
            t = self[page * self.columns:(page * self.columns) + self.columns]
            for bit in range(8):
                line = []
                for col in t:
                    val = chars[int(((col) & (1 << (8-(bit+1)))) != 0)]
                    line.append(val)

                lines.append(''.join((str(x) for x in line)))

        return '\n'.join(lines)

def main():
    
    bit_map = Bitmap()
    print(bit_map.dump())

if __name__ == '__main__':
    main()
