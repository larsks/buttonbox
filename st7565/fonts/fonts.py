"""
Indexes and lists fonts contained in this directory for use in bitmaps. 
Currently only works with numbers
Fonts must be in the form of an image containing 0-9 in ascending order on the same line with their regular letter spacing included.
"""
from PIL import Image
import st7565.images.images as images
import os 

fonts_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def create_font(font_name):
    """
    Returns a dictionary containing a `PIL` image object for every number in the specified font image `font_name`.jpg, callable in dictionary format.
    """
    font = {}
    try:
        numbers = Image.open(fonts_path + font_name + ".jpg")
        numbers = images.fit_to_display(numbers, True)
        width, height = numbers.size
        font["d"] = Image.open(fonts_path + "degree.jpg")
        font["d"] = images.fit_to_display(font["d"])
        box_width = float(width)/10    
        #Crop out each character in the provided image and save that to a dictionary
        for i in range(0, 10):
            box = [int(round(i*(box_width))), 0, int(round((i + 1)*(box_width))), height]
            #Checks if a subrectangle passes the width of the image, and shortens it if necessary
            if box[3] > width:
                box[3] = width
                
            #pix_dif = ((i + 1)*pix_dif) % 1
            
            box = tuple(box)
            font[str(i)] = numbers.crop(box) 
        return font
    except IOError:
        print("Specified font file: %s.jpg cannot be found at: %s" % (font_name,fonts_path))
def display_c(c, font, screen, lcd, size=5, x=0, y=0):
    """
    Displays a character in the given `font` with top-left corner at the specified `x` and `y` coordinates
    
    `c`: A character
    `font`: A font dictionary
    `size`: An integer from 1-10, 10 being max size that can fit the display
    """
    char = font[str(c)]
    width, height = char.size
    """
    if not(size == 10):
        size /= 10.0
        width = int(round(size*width))
        height = int(round(size*height))
        char.resize((width,height))
    """
    size = int(size * 10)
    images.display_img(char,screen,lcd,size,x,y)
        
def display_s(s, font, screen, lcd, size=5, x=0, y=0):
    """
    Displays a string of characters in the given `font` with top-left corner at the specified `x` and `y` coordinates
    """
    i = 0
    spacing = size * .11
    s = str(s)
    char = s[0]
    char_w, char_h = font[char].size
    for c in s:
        display_c(c,font,screen,lcd,size,(int(i*spacing*char_w)+x),y)
        i += 1        
        
        
        