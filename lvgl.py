import espidf as esp
import lvgl as lv
import lvesp32
import micropython
import gc
import time
import machine

#TCLK = CLK
#TCS = 25
#TDIN = MOSI
#TDO = MISO
#TIRQ

from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,
        spihost=esp.VSPI_HOST, mhz=60, factor=8, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=esp.VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

class Trigger:
    
    def __init__(self):
        
        self.name = ""
        
        self.bhour = 0;
        self.bminute = 0;
        self.bsecond = 0;
        
        self.ehour = 0;
        self.eminute = 0;
        self.esec = 0;
        
        self.duration = 0;
        
        self.isArm = False
        self.isTriggered = False
        
trigger = []

for i in range(0,10):
    trigger.append(Trigger())

def m1():
    scr = lv.obj()
    lv.scr_load(scr)
    
    #make container
    con = lv.cont(scr)
    con.set_auto_realign(True)
    con.set_layout(lv.LAYOUT.CENTER)
    con.align(scr, lv.ALIGN.CENTER,0,0)
    con.set_fit(lv.FIT.TIGHT)
    
    #make label in container
    label = lv.label(con)
    label.set_text(
""" This is the first iteration
    of the water timer. The developer
    is not responsible for any
    damages caused by it. User is
    advise to proceed cautiously""")
    
    btn = lv.btn(con)
    label2 = lv.label(btn)
    label2.set_text("I Accept!")
    btn.set_event_cb(lambda obj, event: m2() if event == lv.EVENT.CLICKED else None)

def m2():
    print("This is callback for M2")
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #make container
    con = lv.cont(scr)
    con.set_auto_realign(True)
    con.set_layout(lv.LAYOUT.CENTER)
    con.align(scr, lv.ALIGN.CENTER,0,0)
    con.set_fit(lv.FIT.TIGHT)
    
    #make label in container
    label = lv.label(con)
    label.set_text(
""" This is the second screen""")
    
    ta = lv.textarea(con)
    kb = lv.keyboard(con)
    #kb.set_style_local_radius(0,0,0)
    kb.set_textarea(ta)
    
    btn = lv.btn(con)
    label = lv.label(btn)
    label.set_text("Skip la")
    btn.set_event_cb(lambda obj, event: m4() if event == lv.EVENT.CLICKED else None)
    
def m3():
    
    global trigger
    
    print("This is callback for M3")
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #make container
    con = lv.cont(scr)
    con.set_auto_realign(True)
    #con.set_layout(lv.LAYOUT.PRETTY_TOP)
    con.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    con.set_fit2(lv.FIT.PARENT,lv.FIT.TIGHT)
    con.set_style_local_radius(0,0,0)
    
    #label = lv.label(con)
    #label.set_text("Trigger No:")
    #label.align(con, lv.ALIGN.IN_TOP_LEFT,10,10)
    
    drop = lv.dropdown(con)
    drop.align(con, lv.ALIGN.IN_LEFT_MID,10, 0)
    drop.set_drag(False)
    drop.set_options("trigger 1\ntrigger 2\ntrigger 3\ntrigger 4\ntrigger 5\ntrigger 6\ntrigger 7\n")
    drop.set_event_cb(lambda obj, event:m3_1() if event == lv.EVENT.VALUE_CHANGED else None)
    
    
    btn = lv.btn(con)
    label_btn = lv.label(btn)
    btn.set_height(drop.get_height())
    label_btn.set_text("New")
    btn.align(con, lv.ALIGN.IN_RIGHT_MID,-10,0)
    
        
    def m3_1():
        
        #load values to begin and duration
    
        con2 = lv.cont(scr)
        con2.align(con, lv.ALIGN.OUT_BOTTOM_MID,0,0)
        con2.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
        con2.set_style_local_radius(0,0,0)
    
        position = drop.get_selected()
        
        con3 = lv.cont(con2)
        con3.align(con2, lv.ALIGN.IN_TOP_MID,0,0)
        con3.set_fit2(lv.FIT.PARENT,lv.FIT.TIGHT)
        tittle = lv.label(con3)
        tittle.align(con3, lv.ALIGN.CENTER,0,0)
        tittle.set_text("Set Begin Time")

    
        minute_btn = lv.btn(con2)
        minute_btn.align(con3, lv.ALIGN.OUT_BOTTOM_MID,0,0)
        minute_btn.set_style_local_radius(0,0,0)
        minute_btn.set_fit(lv.FIT.TIGHT)
        lbl_minute_btn = lv.label(minute_btn)
        lbl_minute_btn.set_text(str(trigger[position].bminute))
    
        hour_btn = lv.btn(con2)
        hour_btn.align(minute_btn, lv.ALIGN.OUT_LEFT_MID,0,0)
        hour_btn.set_style_local_radius(0,0,0)
        hour_btn.set_fit(lv.FIT.TIGHT)
        lbl_hour_btn = lv.label(hour_btn)
        lbl_hour_btn.set_text(str(trigger[position].bhour))
        
        second_btn = lv.btn(con2)
        second_btn.align(minute_btn, lv.ALIGN.OUT_RIGHT_MID,0,0)
        second_btn.set_style_local_radius(0,0,0)
        second_btn.set_fit(lv.FIT.TIGHT)
        lvl_second_btn = lv.label(second_btn)
        lvl_second_btn.set_text(str(trigger[position].bsecond))
            
    m3_1()


def m4():
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #container for drop and switch
    cont = lv.cont(scr)
    cont.set_auto_realign(True)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    cont.set_layout(lv.LAYOUT.PRETTY_MID)
    cont.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    
    #dropdown
    drop = lv.dropdown(cont)
    drop.set_style_local_border_post(lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE)
    drop.set_options("Trigger 1\nTrigger 2\nTrigger 3\nTrigger 4\nTrigger 5\nTrigger 6\nTrigger 7\nTrigger 8\nTrigger 9\n Trigger 10")
    
    #label
    lbl1 = lv.label(cont)
    lbl1.set_text("Arm?")
    
    #switch
    switch = lv.switch(cont)
        
    
    #tabview
    
    tab = lv.tabview(scr)
    tab.align(cont, lv.ALIGN.OUT_BOTTOM_MID,0,0)
    
    tab1 = tab.add_tab("Time")
    tab2 = tab.add_tab("Auto")
    tab3 = tab.add_tab("Switches")
    
    #tab1
    
    lbl2 = lv.label(tab1)
    lbl2.set_text("Start time [h][m][s]")
    lbl2.align(tab1, lv.ALIGN.IN_TOP_MID,0,0)
    
    trig_btn = lv.btnmatrix(tab1)
    trig_btn.set_height(200)
    trig_btn.align(lbl2, lv.ALIGN.OUT_BOTTOM_MID,0,0)
    
  
    def remap():
        btn_map = [lv.SYMBOL.UP, lv.SYMBOL.UP , lv.SYMBOL.UP, "\n",
           str(trigger[0].bhour), str(trigger[0].bminute) , str(trigger[0].bsecond), "\n",
           lv.SYMBOL.DOWN, lv.SYMBOL.DOWN , lv.SYMBOL.DOWN, "\n",
           lv.SYMBOL.SAVE,"" , "" ]
        
        print('remapped called')
        
        return btn_map
    
    trig_btn.set_map(remap())
    #trig_btn.set_style
       
    def event_handler(obj, event):
        if event == lv.EVENT.VALUE_CHANGED:
            txt = obj.get_active_btn()
            print("{} was pressed".format(txt))
            
            if (txt == 0):
                trigger[0].bhour += 1
            
            if (txt == 1):
                trigger[0].bminute +=1
                
            if (txt == 2):
                trigger[0].bsecond +=1
                
            if (txt == 6):
                trigger[0].bhour -= 1
                
            if (txt == 7):
                trigger[0].bminute -= 1
                
            if (txt == 8):
                trigger[0].bsecond -= 1
            
            trig_btn.set_map(remap())
            
    trig_btn.set_event_cb(event_handler)
    
    
    #label set duration
    lbl3 = lv.label(tab1)
    lbl3.align(trig_btn, lv.ALIGN.OUT_BOTTOM_MID,-100,0)
    lbl3.set_text("Set trigger duration [h][m][s]")
    
    roller= lv.roller(tab1)
       
    
m1()


