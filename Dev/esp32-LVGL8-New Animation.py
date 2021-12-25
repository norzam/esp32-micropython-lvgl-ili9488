'''Animation'''

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

'''animation styles'''

def anim(obj, val1, val2, style):

    global a1

    def anim_style(obj, val, style):
        
        if style == 'position_x':
            obj.set_x(val)

        if style == 'position_y':
            obj.set_y(val)
            
    a1 = lv.anim_t()
    a1.init()
    a1.set_var(obj)
    a1.set_values(val1, val2)
    a1.set_time(1000)
    a1.set_playback_delay(100)
    #a1.set_playback_time(300)
    #a1.set_repeat_delay(500)
    #a1.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
    a1.set_path_cb(lv.anim_t.path_overshoot)
    a1.set_custom_exec_cb(lambda a1,val: anim_style(obj, val, style))

    return a1

purple = lv.color_hex(0x7808ad)


scr = lv.scr_act()
scr.set_style_bg_color(purple,0)

welcome_bar = lv.obj(scr)
welcome_bar.set_x(10)
welcome_bar.set_y(20)
welcome_bar.set_height(50)
welcome_bar.set_width(300)
welcome_bar.set_style_radius(50,lv.STATE.DEFAULT)
welcome_bar.set_style_border_color(lv.color_hex(0xffffff),0)
welcome_bar.set_style_shadow_width(30,lv.STATE.DEFAULT)

anim(welcome_bar, -300, 10, 'position_x')
lv.anim_t.start(a1)

welcome_bar_text = lv.label(welcome_bar)
welcome_bar_text.set_text('Add New Trigger')
welcome_bar_text.set_style_text_color(purple,0)
#welcome_bar_text.set_style_text_font(lv.font_montserrat_28,0)
anim(welcome_bar_text, 10, 40, 'position_x')
lv.anim_t.start(a1)

def btn_event(obj):
    lv.scr_act().clean()
    menu1()

restart_btn = lv.btn(scr)
restart_btn.center()
restart_btn.add_event_cb(btn_event, lv.EVENT.CLICKED,None)
restart_btn.set_style_bg_color(lv.color_hex(0xffffff),0)


restart_btn_lbl = lv.label(restart_btn)
restart_btn_lbl.set_text('Restart')



