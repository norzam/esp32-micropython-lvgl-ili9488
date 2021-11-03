#TEST REPLICATING WHATSAPP USER INTERFACE

from config import user, password
from espidf import VSPI_HOST
import lvgl as lv
import urandom
import utime

from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=VSPI_HOST, mhz=50, factor=16, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=False, initialize=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)


WIDTH=320

scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(0x089e85),0)
scr.clear_flag(lv.obj.FLAG.SCROLLABLE) #do not scroll
btn = lv.btn(scr)
btn.set_width(WIDTH)
btn.set_style_radius(lv.STATE.DEFAULT,0)
btn.align_to(scr, lv.ALIGN.TOP_MID, 0, 0)
btn.set_height(50)
btn.set_style_bg_color(lv.color_hex(0x089e85),0)

label = lv.label(btn)
label.set_style_text_font(lv.font_montserrat_14,0)
label.set_text('WHATZAPP LGVL')
label.align_to(btn, lv.ALIGN.LEFT_MID,10,0)

label2 = lv.label(btn)
label2.set_text(lv.SYMBOL.EYE_OPEN)
label2.align_to(btn, lv.ALIGN.RIGHT_MID,-10,0)

tabv = lv.tabview(scr, lv.DIR.TOP, 50)
tabv.get_child(0).set_style_bg_color(lv.color_hex(0x0089e85),0)
tabv.set_width(WIDTH)
tabv.align_to(btn, lv.ALIGN.OUT_BOTTOM_MID,0,0)

tab1 = tabv.add_tab("CHATS")
tab2 = tabv.add_tab("STATUS")
tab3 = tabv.add_tab("CALLS")

tabs_btn = tabv.get_tab_btns()
tabs_btn.set_style_text_color(lv.color_hex(0xffffff),0)
tabs_btn.set_style_bg_color(lv.color_hex(0x0516d), lv.PART.ITEMS | lv.STATE.CHECKED)
tabs_btn.set_style_text_color(lv.color_hex(0xffffff), lv.PART.ITEMS | lv.STATE.CHECKED)
tabs_btn.set_style_border_color(lv.color_hex(0x9df8e9), lv.PART.ITEMS | lv.STATE.CHECKED)

tab1.set_flex_flow(lv.FLEX_FLOW.COLUMN)
tab1.set_style_pad_row(lv.STATE.DEFAULT,0)
tab1.set_style_pad_all(lv.STATE.DEFAULT,0)
tab1.set_style_pad_column(lv.STATE.DEFAULT,1)

name = ['Ahmad', 'Ali', 'Abu', 'Mawar', 'Cempaka', 'Raja', 'Ah Chong', 'Gopal', 'Kamil', 'Bakar']
cards = []

for i in range (0,10):
    cards.append(lv.btn(tab1)) 
    cards[i].set_width(WIDTH)
    cards[i].set_height(lv.SIZE.CONTENT)
    cards[i].set_style_bg_color(lv.color_hex(0xffffff),0)
    cards[i].set_style_radius(lv.STATE.DEFAULT, 0)
    cards[i].set_style_pad_row(lv.STATE.DEFAULT, 1)

    image = lv.btn(cards[i])
    image.set_style_bg_color(lv.color_hex(0xced0cf),0)
    image.set_size(40,40)
    image.align_to(cards[i], lv.ALIGN.LEFT_MID, 5, 0)
    image.set_style_radius(lv.RADIUS.CIRCLE,0)

    card_label_name = lv.label(cards[i])
    card_label_name.set_style_text_font(lv.font_montserrat_14,0)
    card_label_name.set_style_text_color(lv.color_hex(0x000000),0)
    card_label_name.set_text('{}'.format(name[i]))
    card_label_name.align_to(cards[i], lv.ALIGN.OUT_TOP_LEFT, 70, 25)

    card_label_msg = lv.label(cards[i])
    card_label_msg.set_style_text_font(lv.font_montserrat_14,0)
    card_label_msg.set_style_text_color(lv.color_hex(0x5f5f5f),0)
    card_label_msg.set_text('Lorem ipsum{}'.format(i))
    card_label_msg.align_to(card_label_name, lv.ALIGN.OUT_BOTTOM_LEFT,0, 5)

    tabv.set_height(lv.SIZE.CONTENT)

lv.scr_load(scr)