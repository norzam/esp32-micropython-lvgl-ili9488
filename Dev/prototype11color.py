'''
PROTOTYPE
'''

#import espidf as esp
import lvgl as lv
#import lvesp32
#import micropython
#import gc
#import time
#import machine
#import utime
import network
from lv_colors import lv_colors

sta_if = network.WLAN(network.STA_IF)

#LCD_MOSI = DO NOT CONENCT

#TCLK = CLK
#TCS = 25
#TDIN = MOSI
#TDO = MISO
#TIRQ

lv.init()

from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=esp.VSPI_HOST, mhz=60, factor=8, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=esp.VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)


scr = lv.obj()
lv.scr_load(scr)


#create style
style = lv.style_t()
style.init()
style.set_bg_color(lv.STATE.DEFAULT, lv.color_hex(0x0090ff))


button = lv.btn(scr)
button.add_style(button.PART.MAIN, style)
