'''
PROTOTYPE
'''

import espidf as esp
import lvgl as lv
#import lvesp32
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


def m1():
    scr = lv.obj()
    lv.scr_load(scr)
    scr.set_style_local_bg_color(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex(0xffffff))

    decoder = lv.img.decoder_create()
    decoder.info_cb = get_png_info
    decoder.open_cb = open_png

    with open('bonsai-logo.png', 'rb') as f:
          png_data = f.read()
      
    global png_img_dsc
    
    png_img_dsc = lv.img_dsc_t({
    'data_size':len(png_data),
    'data':png_data
    })

    img1 = lv.img(scr)
    img1.set_src(png_img_dsc)
    img1.align(scr, lv.ALIGN.CENTER,0,0)
    img1.fade_in(2000,0)
    img1.set_drag(True)
    time.sleep(2)
    img1.fade_out(2000,0)
    time.sleep(2)
    m2()
    
def m2():
    '''
    MAIN SCREEN
    '''
    
    '''scr'''
    scr = lv.obj()
    lv.scr_load(scr)
    scr.set_style_local_bg_color(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex(0xffffff))
    
    
    head = lv.cont(scr)
    head.align(scr, lv.ALIGN.IN_TOP_MID, 0, 50)
    head.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    head.set_style_local_border_post(lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE)
    head.set_style_local_border_width(lv.obj.PART.MAIN, lv.STATE.DEFAULT,0)
    
    head_text = lv.label(head)
    head_text.set_text("Welcome")
    head_text.align(head, lv.ALIGN.CENTER, 0, 0)
    head_text.fade_in(1000,0)
    

    ''''main card
            - this will be looped
    '''
    cont = lv.cont(scr)
    cont.set_style_local_border_post(lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE)
    cont.set_auto_realign(True)
    cont.align(head, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    cont.set_style_local_border_width(lv.obj.PART.MAIN, lv.STATE.DEFAULT,0)
    cont.set_style_local_bg_color(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex(0xf3ffd6))
    cont.fade_in(1000,800)
    '''gradient - disable gradient for now''
    # cont.set_style_local_bg_grad_color(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex(0xffffff))
    # cont.set_style_local_bg_grad_dir(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.GRAD_DIR.VER)    
    '''
    cont.set_height(100)
    cont.set_width(300)
    cont.set_drag(True)
    #cont.set_style_local_radius(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.RADIUS.CIRCLE)
    
    
    '''pic container'''
    in_cont = lv.cont(cont)
    in_cont.set_height(80)
    in_cont.set_width(80)
    in_cont.align(cont, lv.ALIGN.IN_LEFT_MID, 10,0)
    in_cont.set_style_local_border_width(lv.obj.PART.MAIN, lv.STATE.DEFAULT,0)
    in_cont.set_style_local_radius(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.RADIUS.CIRCLE)
    in_cont.set_style_local_bg_color(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.color_hex(0xffffff))
    in_cont.fade_in(300,1100)
    '''pic in in_cont'''
    pic_in_cont = lv.img(in_cont)
    pic_in_cont.set_src(png_img_dsc)
    #pic_in_cont.set_style_local_radius(lv.obj.PART.MAIN, lv.STATE.DEFAULT, lv.RADIUS.CIRCLE)
    pic_in_cont.set_zoom(50)
    pic_in_cont.align(in_cont, lv.ALIGN.CENTER, 0, 0)
    pic_in_cont.set_drag(True)
    pic_in_cont.fade_in(300, 1400)
    
    
    '''cont label - Trigger'''
    cont_label = lv.label(cont)
    cont_label.set_text('Trigger 0')
    cont_label.align(cont, lv.ALIGN.IN_TOP_LEFT,100,10)
    cont_label.fade_in(300,1700)
    
    cont_label_time_begin = lv.label(cont)
    cont_label_time_begin.set_text("Begins at : {:02}:{:02}:{:02}".format(8,30,10))
    cont_label_time_begin.align(cont_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 0)
    cont_label_time_begin.fade_in(300,2000)

m1()

    
    
    
    
