'''
PROTOTYPE
automatic create all button from list
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
import urequest
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

cont = lv.cont(scr)
cont.set_auto_realign(False)
cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
cont.set_layout(lv.LAYOUT.PRETTY_TOP)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('norzam5001-93A8', '74221486')
while sta_if.isconnected() == False:
    print('.')


chart = lv.chart(cont)
chart.set_size(200, 300)
chart.set_type(lv.chart.TYPE.LINE)

ser1 = chart.add_series(lv_colors.RED)

import json

# binance data
while True:
    
    
    
    data = urequest.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
    print(data.content)
    chart.set_next(ser1, float((json.loads(data.content))['price']))
    time.sleep(10)

