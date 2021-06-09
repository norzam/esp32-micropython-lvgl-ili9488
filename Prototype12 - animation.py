'''
PROTOTYPE
'''

import espidf as esp
import lvgl as lv
import lvesp32
import micropython
import gc
import time
import machine
import utime
import network
from imagetools import get_png_info, open_png

sta_if = network.WLAN(network.STA_IF)

#LCD_MOSI = DO NOT CONENCT

#TCLK = CLK
#TCS = 25
#TDIN = MOSI
#TDO = MISO
#TIRQ

lv.init()

from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=-1, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=esp.VSPI_HOST, mhz=60, factor=8, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=esp.VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

scr = lv.obj()
lv.scr_load(scr)

circle = lv.cont(scr)
circle.set_width(300)
circle.set_height(300)
circle.align(scr, lv.ALIGN.CENTER, 0, 0)
circle.set_style_local_radius(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.RADIUS.CIRCLE)
circle.fade_in(3000,0)

time.sleep(3)