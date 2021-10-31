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



'''animate'''

#1 Create lv.anim_t()

def animation(obj, value1, value2, anim_time,pb_delay,pb_time, path, cb, **kwargs):
    
    global animate
            
    animate = lv.anim_t()
    animate.init()
    animate.set_var(obj)
    animate.set_values(value1, value2)
    animate.set_time(anim_time)
    animate.set_playback_delay(pb_delay)
    animate.set_playback_time(pb_time)
    animate.set_path_cb(path)
    animate.set_custom_exec_cb(lambda animate, val: cb(obj,val,2))
    
    return animate


'''animate callback'''
def animate_cb(obj, val, params):
    if params == 1:
        obj.set_y(val)
    if params == 2:
        obj.set_size(20+val, 20+val)

scr = lv.scr_act()

circle = lv.obj(scr)
circle.set_style_radius(lv.RADIUS.CIRCLE,0)
circle.center()
circle.set_size(20,20)
circle.set_style_bg_color(lv.color_hex(0xff00ae),0)

anim_list = []
anim_list.append(animation(circle, -100, 100, 1000, 0, 0, lv.anim_t.path_ease_in_out, animate_cb))
anim_list.append(animation(circle, 20, 50, 1000, 0, 0, lv.anim_t.path_ease_in_out, animate_cb))

lv.anim_t.start(anim_list[0])
lv.anim_t.start(anim_list[1])
