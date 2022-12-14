# MIT License
#
# Copyright (c) 2021 Christopher Wells
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from machine import Pin,SPI,PWM
import framebuf
import time
import os

import bmp_file_reader as bmpr
import lcd

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

def to_color(red, green, blue):
    brightness = 1.0
    
    # Convert from 8-bit colors for red, green, and blue to 5-bit for blue and red and 6-bit for green.
    b = int((blue / 255.0) * (2 ** 5 - 1) * brightness)
    r = int((red / 255.0) * (2 ** 5 - 1) * brightness)
    g = int((green / 255.0) * (2 ** 6 - 1) * brightness)
    
    # Shift the 5-bit blue and red to take the correct bit positions in the final color value
    bs = b << 8
    rs = r << 3
    
    # Shift the 6-bit green value, properly handling the 3 bits that overlflow to the beginning of the value
    g_high = g >> 3
    g_low = (g & 0b000111) << 13
    
    gs = g_high + g_low
    
    # Combine together the red, green, and blue values into a single color value
    color = bs + rs + gs
    
    return color

def read_bmp_to_buffer(lcd_display, file_handle):
    reader = bmpr.BMPFileReader(file_handle)
    
    for row_i in range(0, reader.get_height()):
        row = reader.get_row(row_i)
        for col_i, color in enumerate(row):
            lcd_display.pixel(col_i, row_i, to_color(color.red, color.green, color.blue))
  
if __name__=='__main__':
    # Setup the LCD display
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    lcd_display = lcd.LCD_1inch3()
    
    # Display a loading screen
    lcd_display.fill(to_color(40,40,40))
    lcd_display.text("Loading...", 2, 28, to_color(244,244,244))
 
    lcd_display.show()
    
    # Iterate through showing all of the BMP images in the images directory
    images = os.listdir("images")
    while True:
        for image_filename in sorted(images):
            image_path = "images/" + image_filename
            
            # Load the image from the file and write it to the LCD buffer
            lcd_display.fill(0xFFFF)
            with open(image_path, "rb") as input_stream:
                read_bmp_to_buffer(lcd_display, input_stream)
   
            # Show the image on the display
            lcd_display.show()

            # Wait a bit before trying to load the next image. Actual time till next image shows is a
            # few seconds more due to time to load next image from flash storage.
            time.sleep(5)
