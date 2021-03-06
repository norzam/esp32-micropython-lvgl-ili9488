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
cont.set_auto_realign(True)
cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
cont.set_layout(lv.LAYOUT.PRETTY_TOP)

btn_list = []
label_list = []
label_properties = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def btn_event(obj, event):
    
    if event == lv.EVENT.CLICKED:
        btn_position = btn_list.index(obj) 
        print(label_list[btn_position].get_text())
        
list_range = len(label_properties)

#use list range to create all buttons
for i in range(0, list_range):
    btn_list.append(lv.btn(cont))
    btn_list[i].set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    btn_list[i].set_style_local_radius(0,0,0)
    btn_list[i].set_event_cb(btn_event)
    
    label_list.append(lv.label(btn_list[i]))
    label_list[i].set_text(label_properties[i])
    


    
    
    
    
