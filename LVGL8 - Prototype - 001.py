'''
PROTOTYPE
'''

import espidf as esp
import lvgl as lv
lv.init()

import btree
import network
import time

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('norzam5001', '74221486')

#LCD_MOSI = DO NOT CONENCT

#TCLK = CLK
#TCS = 25
#TDIN = MOSI
#TDO = MISO
#TIRQ




from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=esp.VSPI_HOST, mhz=50, factor=8, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=esp.VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

'''Setting Up DB : Using btree'''

def start_db():
        
    try:
        f = open("mydb", "r+b")
    except OSError:
        f = open("mydb", "w+b")
        
    global db
    
    db = btree.open(f)

    for key in db:
        print(key)
        
    '''fetching db'''
    for key in db:
        eval(db[str(eval(key))])    
        
    return db

def create_trigger(unique_id, name, begin, duration):
    #check all key and create new unique id
    
    temp  = {
             'name':name,
             'begin':str("{:06}".format(begin)),
             'duration':str(duration),
             'end':'000000',
             'arm':False,
             'isTriggered':False,
             }
    print(temp)
    db[str(unique_id).encode('UTF-8')] = str(temp).encode('UTF-8')
    
def fetch_keys():
    for key in db:
        print("db["+str(eval(key))+"]")
        print(eval(db[str(eval(key))]))    
    

'''LVGL 8'''

def home():
    
    def btn_event(obj,info):
        print(obj)
        print(info)
        
        if info == 'add new':
            lv.scr_act().clean()
            add_new()
    
    scr = lv.obj()
    scr.clean()
    lv.scr_load(scr)
    
    label = lv.label(scr)
    label.set_text("List of Triggers and Keys")
    label.align_to(scr, lv.ALIGN.TOP_LEFT, 10, 25)
    
    table = lv.table(scr)
    table.align_to(label, lv.ALIGN.OUT_BOTTOM_LEFT, 5,5)
    
    table.set_col_cnt(4)
    table.set_col_width(0,60)
    table.set_col_width(1,80)
    table.set_col_width(2,80)
    table.set_col_width(3,70)
    table.set_cell_value(0,0,"Keys")
    table.set_cell_value(0,1,"Begin")
    table.set_cell_value(0,2,"Dur(s)")
    table.set_cell_value(0,3,"Arm")

    counter = 1

    for key in db:
        '''fill table keys'''
        
        '''key'''
        table.set_cell_value(counter,0, str(eval(key)))
        
        '''begin'''
        table.set_cell_value(counter,1, (eval(db[str(eval(key))])['begin']))
        
        '''duration'''
        table.set_cell_value(counter,2, (eval(db[str(eval(key))])['duration']))
       
        '''arm'''
        table.set_cell_value(counter,3, str((eval(db[str(eval(key))])['arm'])))

        counter += 1
       
    btn = lv.btn(scr)
    btn.align_to(table, lv.ALIGN.OUT_BOTTOM_LEFT, 5, 5)
    btn_lbl = lv.label(btn)
    btn_lbl.set_text('Add New')
    btn.add_event_cb(lambda e:btn_event(e,"add new"), lv.EVENT.CLICKED, None)
    
    btn2 = lv.btn(scr)
    btn2.align_to(btn, lv.ALIGN.OUT_RIGHT_TOP, 10,0)
    btn2_lbl = lv.label(btn2)
    btn2_lbl.set_text('Save to DB')
    btn2.add_event_cb(lambda e:btn_event(e,"Save DB"), lv.EVENT.CLICKED, None)


def add_new():
        
    def btn_event(obj, info):
        if info == "Cancel":
            lv.scr_act().clean()
            home()
            
    def ta_event_cb(e, keyboard):
        code = e.get_code()
        text_area = e.get_target()
        
        if code == lv.EVENT.FOCUSED:
            keyboard.set_textarea(text_area)
            keyboard.clear_flag(lv.obj.FLAG.HIDDEN)
            keyboard.move_foreground()
            cont.add_flag(lv.obj.FLAG.HIDDEN)
            
        if code == lv.EVENT.DEFOCUSED:
            keyboard.set_textarea(None)
            keyboard.add_flag(lv.obj.FLAG.HIDDEN)
            cont.clear_flag(lv.obj.FLAG.HIDDEN)
    
    
    '''main scr'''
    scr = lv.obj()
    scr.clean()
    
    
    lv.scr_load(scr)
    
    btn_cancel = lv.btn(scr)
    btn_cancel.add_event_cb(lambda e:btn_event(e,"Cancel"), lv.EVENT.CLICKED, None)
    btn_cancel_text = lv.label(btn_cancel)
    btn_cancel_text.set_text('Cancel')
    
    btn_save = lv.btn(scr)
    btn_save.align_to(btn_cancel, lv.ALIGN.OUT_RIGHT_TOP,185,0)
    btn_save_text = lv.label(btn_save)
    btn_save_text.set_text('Save')
    
    label = lv.label(scr)
    label.set_text('Add New Trigger')
    label.align_to(btn_cancel, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    
    label2 = lv.label(scr)
    label2.set_text('Trigger Name (Max: 8 char)')
    label2.align_to(label, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    
    text_area = lv.textarea(scr)
    text_area.set_height(40)
    text_area.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    text_area.add_event_cb(lambda e: ta_event_cb(e, keyboard), lv.EVENT.ALL, None)
    
    keyboard = lv.keyboard(scr)
    keyboard.set_textarea(text_area)
    keyboard.add_flag(lv.obj.FLAG.HIDDEN)
    
    label3 =lv.label(lv.scr_act())
    label3.set_text("Set Time to begin Trigger")
    label3.align_to(text_area, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    
    '''cont'''
    cont = lv.obj(lv.scr_act())
    cont.align_to(label3, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    cont.set_height(150)
    cont.set_width(320)
    
    '''roller options'''
    opts1 = "\n".join(["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23"])
    
    dump = []
    for i in range(0,60):
        dump.append(str(i))
        
    opts2 = "\n".join(dump)
    
    '''roller'''
    roller1 = lv.roller(cont)
    roller1.align_to(cont, lv.ALIGN.LEFT_MID,0,20)
    roller1.set_width(60)
    roller1.set_options(opts1, lv.roller.MODE.NORMAL)
    roller1.set_visible_row_count(3)
    roller1.set_selected(8, lv.ANIM.ON)
    
    roller2 = lv.roller(cont)
    roller2.align_to(roller1, lv.ALIGN.OUT_RIGHT_TOP,5,0
                     )
    roller2.set_width(60)
    roller2.set_options(opts2, lv.roller.MODE.NORMAL)
    roller2.set_visible_row_count(3)
    roller2.set_selected(30, lv.ANIM.ON)
    
    roller3 = lv.roller(cont)
    roller3.align_to(roller2, lv.ALIGN.OUT_RIGHT_TOP,5,0)
    roller3.set_width(60)
    roller3.set_options(opts2, lv.roller.MODE.NORMAL)
    roller3.set_visible_row_count(3)
    roller3.set_selected(0, lv.ANIM.ON)
    
    label4 = lv.label(cont)
    label4.align_to(roller1, lv.ALIGN.OUT_TOP_MID,0,0)
    label4.set_text('hour')
    
    label5 = lv.label(cont)
    label5.align_to(roller2, lv.ALIGN.OUT_TOP_MID,0,0)
    label5.set_text('min')
    
    label6 = lv.label(cont)
    label6.align_to(roller3, lv.ALIGN.OUT_TOP_MID,0,0)
    label6.set_text('sec')
    
    
    '''reset button'''
    btn_reset = lv.btn(cont)
    btn_reset.align_to(roller3, lv.ALIGN.OUT_RIGHT_TOP,10 ,0)
    btn_reset.set_height(50)
    btn_reset.set_width(85)
     
    btn_reset_lbl = lv.label(btn_reset).set_text("RESET")
    
        
    
'''START'''
start_db()
home()
    