from config import user, password
from espidf import VSPI_HOST
import lvgl as lv
import urandom
import utime
import machine

from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=VSPI_HOST, mhz=60, factor=16, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=False, initialize=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

'''Figma Testing'''

#color
dark        =   lv.color_hex(0x000000)
light_dark  =   lv.color_hex(0x2c2c2c)
white       =   lv.color_hex(0xffffff)
light_green =   lv.color_hex(0x464646)

scr = lv.scr_act()
scr.set_style_bg_color(dark, 0)

header = lv.obj(scr)
header.set_size(300, 80)
header.align_to(scr, lv.ALIGN.TOP_LEFT, 5, 10)
header.set_style_bg_color(light_dark,0)
header.set_style_border_color(dark,0)

header_nav = lv.btn(header)
header_nav.set_size(50,50)
header_nav.set_style_bg_color(light_dark,0)
header_nav.set_style_border_color(light_dark,0)
header_nav.set_style_shadow_color(light_dark,0)
header_nav.align_to(header, lv.ALIGN.LEFT_MID,0,0)

header_nav_label = lv.label(header_nav)
header_nav_label.set_text(lv.SYMBOL.LEFT)
header_nav_label.center()

header_nav_title = lv.label(header)
header_nav_title.set_text('Add New')
header_nav_title.set_style_text_font(lv.font_montserrat_28,0)
header_nav_title.set_style_text_color(white,0)
header_nav_title.align_to(header_nav, lv.ALIGN.OUT_RIGHT_MID,10,0)

#content1
content = lv.obj(scr)
content.set_size(300,100)
content.align_to(header, lv.ALIGN.OUT_BOTTOM_MID,0 ,10)
content.set_style_bg_color(light_dark,0)
content.set_style_border_color(light_dark,0)

#label = Trigger Name
c1 = lv.label(content)
c1.set_text("Trigger Name")
c1.set_style_text_color(white,0)
c1.align_to(content,lv.ALIGN.TOP_MID,0,0)

#textarea = Trigger Name Input
c2 = lv.textarea(content)
c2.set_size(260,40)
c2.align_to(c1, lv.ALIGN.OUT_BOTTOM_MID,0,10)
c2.set_style_bg_color(light_green,0)
c2.set_style_border_color(light_green,0)

#content2
content2 = lv.obj(scr)
content2.set_size(300,310)
content2.align_to(content, lv.ALIGN.OUT_BOTTOM_MID,0 ,10)
content2.set_style_bg_color(light_dark,0)
content2.set_style_border_color(light_dark,0)

c2_1 = lv.label(content2)
c2_1.set_text('Set hour, minute and seconds to\nstart with duration\n\nStart Trigger at:')
c2_1.set_style_text_color(white,0)

#TIME
b2_1 = lv.btn(content2)
b2_1.set_size(80,80)
b2_1.align_to(c2_1, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
b2_1.set_style_bg_color(light_green,0)
b2_1.set_style_border_color(light_green,0)
b2_1_lbl = lv.label(b2_1)
b2_1_lbl.set_text('HH')
b2_1_lbl.center()
b2_1_lbl.set_style_text_font(lv.font_montserrat_28,0)

b2_2 = lv.btn(content2)
b2_2.set_size(80,80)
b2_2.align_to(b2_1, lv.ALIGN.OUT_RIGHT_MID,10,0)
b2_2.set_style_bg_color(light_green,0)
b2_2.set_style_border_color(light_green,0)
b2_2_lbl = lv.label(b2_2)
b2_2_lbl.set_text('MM')
b2_2_lbl.center()
b2_2_lbl.set_style_text_font(lv.font_montserrat_28,0)

b2_3 = lv.btn(content2)
b2_3.set_size(80,80)
b2_3.align_to(b2_2, lv.ALIGN.OUT_RIGHT_MID,10,0)
b2_3.set_style_bg_color(light_green,0)
b2_3.set_style_border_color(light_green,0)
b2_3_lbl = lv.label(b2_3)
b2_3_lbl.set_text('SS')
b2_3_lbl.center()
b2_3_lbl.set_style_text_font(lv.font_montserrat_28,0)

#DURATION
c2_2 = lv.label(content2)
c2_2.align_to(b2_1, lv.ALIGN.OUT_BOTTOM_LEFT,0,20)
c2_2.set_text('Set the duration')
c2_2.set_style_text_color(white, 0)

b2_4 = lv.btn(content2)
b2_4.set_size(80,80)
b2_4.align_to(c2_2, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
b2_4.set_style_bg_color(light_green,0)
b2_4.set_style_border_color(light_green,0)
b2_4_lbl = lv.label(b2_4)
b2_4_lbl.set_text('HH')
b2_4_lbl.center()
b2_4_lbl.set_style_text_font(lv.font_montserrat_28,0)

b2_5 = lv.btn(content2)
b2_5.set_size(80,80)
b2_5.align_to(b2_4, lv.ALIGN.OUT_RIGHT_MID,10,0)
b2_5.set_style_bg_color(light_green,0)
b2_5.set_style_border_color(light_green,0)
b2_5_lbl = lv.label(b2_5)
b2_5_lbl.set_text('MM')
b2_5_lbl.center()
b2_5_lbl.set_style_text_font(lv.font_montserrat_28,0)

b2_6 = lv.btn(content2)
b2_6.set_size(80,80)
b2_6.align_to(b2_5, lv.ALIGN.OUT_RIGHT_MID,10,0)
b2_6.set_style_bg_color(light_green,0)
b2_6.set_style_border_color(light_green,0)
b2_6_lbl = lv.label(b2_6)
b2_6_lbl.set_text('SS')
b2_6_lbl.center()
b2_6_lbl.set_style_text_font(lv.font_montserrat_28,0)

#Content 3 : Automation stuff
content3 = lv.obj(scr)
content3.set_size(300,100)
content3.align_to(content2, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
content3.set_style_bg_color(light_dark,0)
content3.set_style_border_color(light_dark,0)

c3_1 = lv.label(content3)
c3_1.set_text('Automation Settings\n\n ')
c3_1.set_style_text_color(white,0)
