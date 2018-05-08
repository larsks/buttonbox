"""
Allows for creation, manipulation, and displaying of images contained in this directory for use in bitmaps.
"""
import os
from os import walk
from PIL import Image

import st7565.bitmap
import st7565.lcd

images_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def create_img(file_name):
    """Returns a `PIL` image object of `file_name`, resized to fit the display """
    try:
        img = Image.open(images_path + file_name)
        return fit_to_display(img)
        
    except IOError:
        print("Specified image file: %s cannot be found at: %s" % (file_name,images_path))

def create_images():
    """
    Returns a dictionary containing a `PIL` image object for every image in this directory. Images must end in `.pbm` or `.jpg`.
    Using `images['filename']` will yield a `PIL` image object for that filename. 
    """
    images = {}
    for (dirpath, dirnames, filenames) in walk(images_path):
        break
    for file in filenames:
        if ((".pbm" in file) or (".jpg" in file)):
            images[file[:-4]] = create_img(file)
    return images

def fit_to_display(img, fit_by_height = None):
    """
    Returns a proportionally resized image with the largest dimensions that can fit on the display.
    
    `fit_by_height`: whether to force resizing using height
    """
    width, height = img.size
    ratio = float(width) / height
    if fit_by_height == None:
        if (height*2) >= width:
            fit_by_height = True
        else:
            fit_by_height = False
    if (fit_by_height):
        if not(height == 64):
            dif = 64 - height
            height = int(round(height + dif))
            width = int(round((dif*ratio) + width))
            #Takes care of the case when shrinking the image would eliminate its width dimension
            if width == 0:
                width = 1
            return img.resize((width, height))
    else:
        if not (width == 128):
            dif = 128 - width
            width = int(round(width + dif))
            height = int(round((dif/ratio) + height))
            #Takes care of the case when shrinking the image would eliminate its height dimension
            if height == 0:
                height = 1
            return img.resize((width, height))    

def resize_image(img, size):
    """
    Returns a proportionally resized image to `size` percent of the original image, relative to image max size on display.
    
    `img`: A `PIL` image object.
    """
    size /= 100.0
    width, height = img.size
    width = int(round(width*size))
    height = int(round(height*size))
    img = img.resize((width,height))
    return img
            
def display_img(img, screen, lcd, size = 100, x=0, y=0):
    """
    Displays PIL image objects on the ST7565 display at a specified x and y coordinates.
    
    `img`: A `PIL` image object.
    `screen`: A bitmap object. What will be written to the display.
    `lcd`: An lcd object.
    """
    if not(size == 100):
        img = resize_image(img, size)
    try:    
        screen.drawbitmap(img, x, y)
        lcd.write_buffer(screen) 
    except IndexError:
        size = img.size
        print("Image with size (%d,%d) cannot be fit onto (128, 64) size display using given coordinates: (%d,%d)" % (size[0], size[1], x, y))
    


