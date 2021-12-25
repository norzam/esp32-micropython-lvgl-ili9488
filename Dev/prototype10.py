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



# m7() # dashboard

#btn_event

def btn_event(obj, event):

    if obj == home_button and event == lv.EVENT.CLICKED:
        m5()

#gui code

scr = lv.obj()
lv.scr_load(scr)

cont = lv.cont(scr)
cont.align(scr, lv.ALIGN.IN_TOP_MID, 0, 0)
cont.set_style_local_radius(0, 0, 0)
cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)

home_button = lv.btn(cont)
home_button.align(cont, lv.ALIGN.IN_LEFT_MID,0,10)
home_button.set_fit(lv.FIT.TIGHT)


lbl_home = lv.label(home_button)
lbl_home.set_text(lv.SYMBOL.HOME)
lbl_home.set_event_cb(btn_event)

lbl_header = lv.label(cont)
lbl_header.set_text("Dashboard")
lbl_header.align(home_button, lv.ALIGN.OUT_RIGHT_MID,0,-5)

tab_header = lv.tabview(scr)
tab_header.align(cont, lv.ALIGN.OUT_BOTTOM_MID, 0, 0)

tab1 = tab_header.add_tab("Triggers")
tab2 = tab_header.add_tab("Switches")
tab3 = tab_header.add_tab("Sensors")
tab4 = tab_header.add_tab("Charts")


#tab1 : Triggers

#making trigger cards





