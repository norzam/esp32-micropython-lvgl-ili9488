'''
PROTOTYPE
'''

import espidf as esp
import lvgl as lv
lv.init()

import btree
import network
import utime

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
        spihost=esp.VSPI_HOST, mhz=50, factor=16, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=esp.VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

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

    def table_event_cb(e):
        
        row = lv.point_t()
        col = lv.point_t()    
        lv.table.get_selected_cell(table, row, col)
        
        print("row :" + str(row.x))
        print("col :" + str(col.x))
        print("value :" + table.get_cell_value(row.x, col.x))
        
        key = str(table.get_cell_value(row.x, col.x))

        msb_edit_table(key)

        global tabledata
        tabledata = e

        return tabledata

    
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

    '''Table event : get row and column'''
    table.add_event_cb(lambda e: table_event_cb(e), lv.EVENT.PRESSING, None)
       
    btn = lv.btn(scr)
    btn.align_to(table, lv.ALIGN.OUT_BOTTOM_LEFT, 5, 5)
    btn_lbl = lv.label(btn)
    btn_lbl.set_text('Add New')
    btn.add_event_cb(lambda e:btn_event(e,"add new"), lv.EVENT.CLICKED, None)
    
    btn2 = lv.btn(scr)
    btn2.align_to(btn, lv.ALIGN.OUT_RIGHT_TOP, 10,0)
    btn2_lbl = lv.label(btn2)
    btn2_lbl.set_text('Write to Btree DB')
    btn2.add_event_cb(lambda e:btn_event(e,"Save DB"), lv.EVENT.CLICKED, None)

    
    label2 = lv.label(scr)
    label2.align_to(btn, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    label2.set_text('Operation Log')

    textarea = lv.textarea(scr)
    textarea.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    textarea.set_width(290)
    textarea.set_height(180)

    '''
    textarea.add_text(" string " + '\0')

    '''

def msb_edit_table(key):
    msgbox = lv.msgbox(lv.scr_act(), "Quick Edit", "Do you want to change value : {} ?".format(key), ["Yes","No"], True)
    msgbox.center()

def msb_save():
    msgbox = lv.msgbox(lv.scr_act(), "Attention!", "Unsaved settings will be lost. Do you want to exit?", ["Yes","No"], True)
    msgbox.center()


def add_new():
    
    '''button events'''
        
    def btn_event(obj, param):
        
        if param == "Cancel":
            lv.scr_act().clean()
            home()
            
        if param == "Reset 1":
            roller1.set_selected(0, lv.ANIM.ON)
            roller2.set_selected(0, lv.ANIM.ON)
            roller3.set_selected(0, lv.ANIM.ON)
            
        if param == "Set AM 1":
            roller1.set_selected(6, lv.ANIM.ON)
            roller2.set_selected(0, lv.ANIM.ON)
            roller3.set_selected(0, lv.ANIM.ON)
        
        if param == "Set PM 1":
            roller1.set_selected(13, lv.ANIM.ON)
            roller2.set_selected(0, lv.ANIM.ON)
            roller3.set_selected(0, lv.ANIM.ON)

        if param == "Reset 2":
            roller4.set_selected(0, lv.ANIM.ON)
            roller5.set_selected(0, lv.ANIM.ON)
            roller6.set_selected(0, lv.ANIM.ON)

        if param == "Reset hour":
            roller4.set_selected(0, lv.ANIM.ON)
        
        if param == "Reset minute":
            roller5.set_selected(0, lv.ANIM.ON)
           
        
            
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
    keyboard.align_to(scr, lv.ALIGN.BOTTOM_MID,0,0)
    keyboard.set_textarea(text_area)
    keyboard.add_flag(lv.obj.FLAG.HIDDEN)
    
    label3 =lv.label(lv.scr_act())
    label3.set_text("Set Time to begin Trigger")
    label3.align_to(text_area, lv.ALIGN.OUT_BOTTOM_LEFT,5,10)
    
    '''cont width'''
    
    cont_width = 280
    
    '''cont'''
    cont = lv.obj(lv.scr_act())
    cont.align_to(label3, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    cont.set_height(150)
    cont.set_width(cont_width)
    
    '''roller options'''
    dump = []
    for i in range(0,24):
        dump.append(str(i))
        
    opts1 = "\n".join(dump)
    
    del dump
    
    dump = []
    for i in range(0,60):
        dump.append(str(i))
        
    opts2 = "\n".join(dump)
    
    '''roller trigger time'''
    roller1 = lv.roller(cont)
    roller1.align_to(cont, lv.ALIGN.LEFT_MID,0,20)
    roller1.set_width(50)
    roller1.set_options(opts1, lv.roller.MODE.NORMAL)
    roller1.set_visible_row_count(3)
    roller1.set_selected(8, lv.ANIM.ON)
    
    roller2 = lv.roller(cont)
    roller2.align_to(roller1, lv.ALIGN.OUT_RIGHT_TOP,5,0
                     )
    roller2.set_width(50)
    roller2.set_options(opts2, lv.roller.MODE.NORMAL)
    roller2.set_visible_row_count(3)
    roller2.set_selected(30, lv.ANIM.ON)
    
    roller3 = lv.roller(cont)
    roller3.align_to(roller2, lv.ALIGN.OUT_RIGHT_TOP,5,0)
    roller3.set_width(50)
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
    
    
    '''reset button trigger'''
    btn_reset = lv.btn(cont)
    btn_reset.align_to(roller3, lv.ALIGN.OUT_RIGHT_TOP,10 ,0)
    btn_reset.add_event_cb(lambda e:btn_event(e,"Reset 1"), lv.EVENT.CLICKED, None)
    btn_reset_lbl = lv.label(btn_reset)
    btn_reset_lbl.set_text("RESET")
    
    btn_am = lv.btn(cont)
    btn_am.align_to(btn_reset, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    btn_am.add_event_cb(lambda e:btn_event(e,"Set AM 1"), lv.EVENT.CLICKED, None)
    btn_am_lbl = lv.label(btn_am)
    btn_am_lbl.set_text('am')
    
    btn_pm = lv.btn(cont)
    btn_pm.align_to(btn_am, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    btn_pm.add_event_cb(lambda e:btn_event(e,"Set PM 1"), lv.EVENT.CLICKED, None)
    btn_pm_lbl = lv.label(btn_pm)
    btn_pm_lbl.set_text('pm')
    
    label7 = lv.label(scr)
    label7.align_to(cont, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    label7.set_text('Set Duration')
    
    '''cont 2'''
    
    cont2 = lv.obj(scr)
    cont2.align_to(label7, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    cont2.set_height(150)
    cont2.set_width(cont_width)
    
    '''roller duration'''
    roller4 = lv.roller(cont2)
    roller4.align_to(cont2, lv.ALIGN.LEFT_MID,0,20)
    roller4.set_width(50)
    roller4.set_options(opts1, lv.roller.MODE.NORMAL)
    roller4.set_visible_row_count(3)
    roller4.set_selected(0, lv.ANIM.ON)
    
    roller5 = lv.roller(cont2)
    roller5.align_to(roller4, lv.ALIGN.OUT_RIGHT_TOP,5,0)
    roller5.set_width(50)
    roller5.set_options(opts2, lv.roller.MODE.NORMAL)
    roller5.set_visible_row_count(3)
    roller5.set_selected(0, lv.ANIM.ON)
    
    roller6 = lv.roller(cont2)
    roller6.align_to(roller5, lv.ALIGN.OUT_RIGHT_TOP,5,0)
    roller6.set_width(50)
    roller6.set_options(opts2, lv.roller.MODE.NORMAL)
    roller6.set_visible_row_count(3)
    roller6.set_selected(30, lv.ANIM.ON)
    
    label8 = lv.label(cont2)
    label8.align_to(roller4, lv.ALIGN.OUT_TOP_MID,0,0)
    label8.set_text('hour')
    
    label9 = lv.label(cont2)
    label9.align_to(roller5, lv.ALIGN.OUT_TOP_MID,0,0)
    label9.set_text('min')
    
    label10 = lv.label(cont2)
    label10.align_to(roller6, lv.ALIGN.OUT_TOP_MID,0,0)
    label10.set_text('sec')
    
    '''reset button duration'''
    btn_reset2 = lv.btn(cont2)
    btn_reset2.align_to(roller6, lv.ALIGN.OUT_RIGHT_TOP,10 ,0)
    btn_reset2.add_event_cb(lambda e:btn_event(e,"Reset 2"), lv.EVENT.CLICKED, None)
    btn_reset_lbl2 = lv.label(btn_reset2)
    btn_reset_lbl2.set_text("RESET")
    
    btn_am2 = lv.btn(cont2)
    btn_am2.align_to(btn_reset2, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    btn_am2.add_event_cb(lambda e:btn_event(e, "Reset hour"), lv.EVENT.CLICKED, None)
    btn_am_lbl2 = lv.label(btn_am2)
    btn_am_lbl2.set_text('hour')
    
    btn_pm2 = lv.btn(cont2)
    btn_pm2.align_to(btn_am2, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    btn_pm2.add_event_cb(lambda e:btn_event(e, "Reset minute"),lv.EVENT.CLICKED, None)
    btn_pm_lbl2 = lv.label(btn_pm2)
    btn_pm_lbl2.set_text('minute')
    
    label10 = lv.label(scr)
    label10.align_to(cont2, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    label10.set_text('Set Automatic disable trigger settings')
    
    '''cont 3'''
    
    cont3 = lv.obj(scr)
    cont3.align_to(label10, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    cont3.set_height(150)
    cont3.set_width(cont_width)
    
    label11 = lv.label(cont3)
    label11.align_to(cont3, lv.ALIGN.TOP_LEFT,0, 5)
    label11.set_text("Enable Flow Sensor")
    
    switch_flow = lv.switch(cont3)
    switch_flow.align_to(cont3, lv.ALIGN.TOP_RIGHT,0 , -5)
    
    #label12 = lv.label(cont3)
    #label12.align_to(label11, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    #label12.set_text('5 sec threshold')
    
    checkbox1 = lv.checkbox(cont3)
    checkbox1.align_to(label11, lv. ALIGN.OUT_BOTTOM_LEFT,5,10)
    checkbox1.set_text("Min reading 5 sec")

    label13 = lv.label(cont3)
    label13.align_to(checkbox1, lv.ALIGN.OUT_BOTTOM_LEFT,0,5)
    label13.set_text('Max Flow (l): ')

    spinbox1 = lv.spinbox(cont3)
    spinbox1.align_to(label13, lv.ALIGN.OUT_BOTTOM_LEFT,0,0)
    spinbox1.set_range(0, 9999)

    h = spinbox1.get_height()

    btn_spinbox1 = lv.btn(cont3)
    btn_spinbox1.align_to(spinbox1, lv.ALIGN.OUT_RIGHT_TOP,0,0)
    btn_spinbox1.set_style_bg_img_src(lv.SYMBOL.PLUS, 0)
    btn_spinbox1.set_size(h,h)

    btn_spinbox2 = lv.btn(cont3)
    btn_spinbox2.align_to(btn_spinbox1, lv.ALIGN.OUT_RIGHT_TOP,0,0)
    btn_spinbox2.set_style_bg_img_src(lv.SYMBOL.MINUS, 0)
    btn_spinbox2.set_size(h,h)

    '''Rain sensor'''

    cont4 = lv.obj(scr)
    cont4.align_to(cont3, lv.ALIGN.OUT_BOTTOM_LEFT,0, 10)
    cont4.set_height(90)
    cont4.set_width(cont_width)

    label13 = lv.label(cont4)
    label13.align_to(cont4, lv.ALIGN.TOP_LEFT,0, 5)
    label13.set_text("Enable Rain Sensor")
    
    switch_flow2 = lv.switch(cont4)
    switch_flow2.align_to(cont4, lv.ALIGN.TOP_RIGHT,0 , -5)

    checkbox2 = lv.checkbox(cont4)
    checkbox2.align_to(label13, lv. ALIGN.OUT_BOTTOM_LEFT,5,10)
    checkbox2.set_text("Min reading 5 sec")

    '''Calender'''

    cont5 = lv.obj(scr)
    cont5.align_to(cont4, lv.ALIGN.OUT_BOTTOM_LEFT,0, 10)
    cont5.set_height(290)
    cont5.set_width(cont_width)

    label14 = lv.label(cont5)
    label14.align_to(cont5, lv.ALIGN.TOP_LEFT,0, 5)
    label14.set_text("Enable days")
    
    switch_flow3 = lv.switch(cont5)
    switch_flow3.align_to(cont5, lv.ALIGN.TOP_RIGHT,0 , -5)

    checkbox3 = lv.checkbox(cont5)
    checkbox3.align_to(label14, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox3.set_text("Monday")

    checkbox4 = lv.checkbox(cont5)
    checkbox4.align_to(checkbox3, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox4.set_text("Tuesday")

    checkbox5 = lv.checkbox(cont5)
    checkbox5.align_to(checkbox4, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox5.set_text("Wednesday")

    checkbox6 = lv.checkbox(cont5)
    checkbox6.align_to(checkbox5, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox6.set_text("Thursday")

    checkbox7 = lv.checkbox(cont5)
    checkbox7.align_to(checkbox6, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox7.set_text("Friday")

    checkbox8 = lv.checkbox(cont5)
    checkbox8.align_to(checkbox7, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox8.set_text("Saturday")

    checkbox9 = lv.checkbox(cont5)
    checkbox9.align_to(checkbox8, lv. ALIGN.OUT_BOTTOM_LEFT,0,10)
    checkbox9.set_text("Sunday")

    
'''START'''

def system_loop():
    
    '''run once'''
    start_db()
    home()
    
    '''main loop'''
    while(True):
        
      lv.task_handler()
      lv.tick_inc(5)  
  
#system_loop()  

start_db()
home()


    