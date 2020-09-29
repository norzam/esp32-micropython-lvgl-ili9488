import espidf as esp
import lvgl as lv
import lvesp32
import micropython
import gc
import time
import machine
import utime

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

class Trigger:
    
    def __init__(self):
        
        self.name = ""
        self.desc = ""
        
        self.bhour     = 0;
        self.bminute   = 0;
        self.bsecond   = 0;
        
        self.ehour     = 0;
        self.eminute   = 0;
        self.esec      = 0;
        
        self.hourdur   = 0;
        self.minutedur = 0;
        self.seconddur = 0;
        
        self.isArmed = False
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
    
    position = 0
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #container for drop and switch
    cont = lv.cont(scr)
    cont.set_auto_realign(True)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    cont.set_layout(lv.LAYOUT.PRETTY_MID)
    cont.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    cont.set_style_local_radius(0,0,0)
    
    #dropdown - event
    
    def drop_event(obj, event):
        
        if event == lv.EVENT.VALUE_CHANGED:
        
            position = drop.get_selected()
            print("changing trigger position to {}".format(str(position)))
            m4_1(position) #call to refresh roller position
                
    #dropdown
    drop = lv.dropdown(cont)
    drop.set_style_local_border_post(lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE)
    drop.set_options("Trigger 1\nTrigger 2\nTrigger 3\nTrigger 4\nTrigger 5\nTrigger 6\nTrigger 7\nTrigger 8\nTrigger 9\n Trigger 10")
    drop.set_event_cb(drop_event)
    
    #tabview
    
    tab = lv.tabview(scr)
    tab.align(cont, lv.ALIGN.OUT_BOTTOM_MID,0,0)
    
    tab1 = tab.add_tab("Time")
    tab2 = tab.add_tab("Auto")
    tab3 = tab.add_tab("Switches")
    tab4 = tab.add_tab("Desc")
    
    
####Tab 1
    
    
    #label
    lbl1 = lv.label(cont)
    lbl1.set_text("Arm?")
    
    #switch
    switch = lv.switch(cont)
    
    lbl2 = lv.label(tab1)
    lbl2.set_text("Set time to begin trigger :")
     
    lbl2.align(tab1, lv.ALIGN.IN_TOP_MID,0,10)
    
    
    #contain - sort vert
    cont2 = lv.cont(tab1)
    cont2.align(lbl2, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    cont2.set_auto_realign(True)
    cont2.set_layout(lv.LAYOUT.ROW_MID)
    cont2.set_fit(lv.FIT.TIGHT)
    
    roller_hour = lv.roller(cont2)
    roller_hour.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23",lv.roller.MODE.NORMAL)
    roller_minute = lv.roller(cont2)
    roller_minute.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45\n46\n47\n48\n49\n50\n51\n52\n53\n54\n55\n56\n57\n58\n59", lv.roller.MODE.NORMAL)
    roller_sec = lv.roller(cont2)
    roller_sec.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45\n46\n47\n48\n49\n50\n51\n52\n53\n54\n55\n56\n57\n58\n59", lv.roller.MODE.NORMAL)
              
    btn = lv.btn(cont2)
    lbl_btn = lv.label(btn)
    lbl_btn.set_text("SET")
    
    
    #duration
    
    lbl3 = lv.label(tab1)
    lbl3.set_text("Set duration for trigger : ")
    lbl3.align(cont2, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    
    cont3 = lv.cont(tab1)
    cont3.align(lbl3, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    cont3.set_auto_realign(True)
    cont3.set_layout(lv.LAYOUT.ROW_MID)
    cont3.set_fit(lv.FIT.TIGHT)
    
    roller_hour_dur = lv.roller(cont3)
    roller_hour_dur.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23",lv.roller.MODE.NORMAL)
    roller_minute_dur = lv.roller(cont3)
    roller_minute_dur.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45\n46\n47\n48\n49\n50\n51\n52\n53\n54\n55\n56\n57\n58\n59", lv.roller.MODE.NORMAL)
    roller_sec_dur = lv.roller(cont3)
    roller_sec_dur.set_options("00\n01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45\n46\n47\n48\n49\n50\n51\n52\n53\n54\n55\n56\n57\n58\n59", lv.roller.MODE.NORMAL)
    
    #button (set timer) - event
    
    def btn_event(obj, event):
        
        if obj == btn and event == lv.EVENT.CLICKED:
            
            position = drop.get_selected()
            
            trigger[position].bhour = roller_hour.get_selected()
            trigger[position].bminute = roller_minute.get_selected()
            trigger[position].bsecond = roller_sec.get_selected()
                                   
            print("btn - event : position {}, bhour {}, bminute {}, bsec{}".format(str(position),str(roller_hour.get_selected()),str(roller_minute.get_selected()),str(roller_sec.get_selected())))
    
        if obj == btn2 and event == lv.EVENT.CLICKED:
            
            position = drop.get_selected()
            
            trigger[position].hourdur = roller_hour_dur.get_selected()
            trigger[position].minutedur = roller_minute_dur.get_selected()
            trigger[position].seconddur = roller_sec_dur.get_selected()
            
            print("btn2 - event")
        
        if obj == switch and event == lv.EVENT.VALUE_CHANGED:
            
            position = drop.get_selected()
            trigger[position].isArmed = switch.get_state()
            
            print("Arming trigger {}".format(switch.get_state()))
           
        if obj == btn_t4_1 and event == lv.EVENT.CLICKED:
            m5()
            
    btn2 = lv.btn(cont3)
    lbl_btn2 = lv.label(btn2)
    lbl_btn2.set_text("SET")
    
    #button event call
    btn.set_event_cb(btn_event)
    btn2.set_event_cb(btn_event)
    switch.set_event_cb(btn_event)
    
   
       
    def m4_1(_position): #run after dropdown selected or pos 0 default
        
        position = _position
        print("M4_1() calling position {}".format(position))
          
        roller_hour.set_selected(trigger[position].bhour, lv.ANIM.ON)
        roller_minute.set_selected(trigger[position].bminute,lv.ANIM.ON)
        roller_sec.set_selected(trigger[position].bsecond, lv.ANIM.ON)
        
        roller_hour_dur.set_selected(trigger[position].hourdur, lv.ANIM.ON)
        roller_minute_dur.set_selected(trigger[position].minutedur,lv.ANIM.ON)
        roller_sec_dur.set_selected(trigger[position].seconddur, lv.ANIM.ON)
        
        #set proper state of switch
        
        if switch.get_state() != trigger[position].isArmed:
            switch.toggle(lv.ANIM.ON)
        
                     
    m4_1(position)
    
#####Tab 2 - Automation
    
    tab2.set_height(320)
    
    lbl_t2 = lv.label(tab2)
    lbl_t2.align(tab1, lv.ALIGN.IN_TOP_MID,210,10)
    lbl_t2.set_text("Automatic trigger disable settings")
    
    cont3 = lv.cont(tab2)
    cont3.set_auto_realign(True)
    cont3.set_layout(lv.LAYOUT.PRETTY_MID)
    cont3.align(lbl_t2, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    cont3.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    
    lbl_t2_2 =lv.label(cont3)
    lbl_t2_2.set_text("Enable Flow Sensor")
    
    switch_t2_1 = lv.switch(cont3)
    
    lbl_t2_3 = lv.label(cont3)
    lbl_t2_3.set_text("Enable Rain Sensor")
    
    switch_t2_2 = lv.switch(cont3)
    
    lbl_t2_4 = lv.label(cont3)
    lbl_t2_4.set_text("Enable MET weather API")
    
    switch_t2_3 = lv.switch(cont3)
    
    lbl_t2_5 = lv.label(cont3)
    lbl_t2_5.set_text("Enable Soil Sensor")
    
    switch_t2_4 = lv.switch(cont3)
    
    gauge_t2 = lv.gauge(tab2)
    gauge_t2.align(cont3, lv.ALIGN.OUT_BOTTOM_MID,0,10)
           
####Tab 3 - Switches
    
    tab3.set_height(320)
    lbl_t3 = lv.label(tab3)
    lbl_t3.align(tab3, lv.ALIGN.IN_TOP_MID,-80,10)
    lbl_t3.set_text("Assign Pin to be triggered")
    
    #page4 = lv.page(tab3)
    #page4.set_auto_realign(True)
    #page4.align(lbl_t3, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    #page4.set_size(290,800)
    
    btnmtx_t3 = lv.btnmatrix(tab3)
    btnmtx_t3.align(lbl_t3, lv.ALIGN.OUT_BOTTOM_MID,0,0)
    btnmtx_t3.set_width(250)
    btnmtx_t3.set_height(600)
        
    btn_map_t3 = ["3.3v","GND","\n",
                  "EN", "23", "\n",
                  "36", "22", "\n",
                  "39", "01", "\n",
                  "34", "03", "\n",
                  "35", "21", "\n",
                  "32","GND", "\n",
                  "33", "19", "\n",
                  "25", "18", "\n",
                  "26", "05", "\n",
                  "27", "17", "\n",
                  "14", "16", "\n",
                  "12", "04", "\n",
                  "GND","00", "\n",
                  "13", "02", "\n",
                  "09", "15", "\n",
                  "10", "08", "\n",
                  "11", "07", "\n",
                  "VIN","06",""]
    
    btnmtx_t3.set_map(btn_map_t3)
    btnmtx_t3.set_btn_ctrl_all(btnmtx_t3.CTRL.CHECKABLE)
    
    btn_t3_save = lv.btn(tab3)
    btn_t3_save.align(btnmtx_t3, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    lbl_btn_t3_save = lv.label(btn_t3_save)
    lbl_btn_t3_save.set_text("Save Toggles")
    
#### Tab 4 Description
    
    btn_t4_1 = lv.btn(tab4)
    btn_t4_1.align(tab4, lv.ALIGN.CENTER, 0,0)
    btn_t4_1.set_event_cb(btn_event)
    lbl_btn_t4_1 = lv.label(btn_t4_1)
    lbl_btn_t4_1.set_text(lv.SYMBOL.HOME)


def m5(): # home screen
           
    scr = lv.obj()
    lv.scr_load(scr)
    
    # btn_event
    
    def btn_event(obj, event):
        
        if (obj == btn) and (event == lv.EVENT.CLICKED):
            m6()
                       
        if (obj == btn2) and (event == lv.EVENT.CLICKED):
            m4() #trigger config
            
        if (obj == btn3) and (event == lv.EVENT.CLICKED):
            return
                
    #wifi 
    
    btn = lv.btn(scr)
    btn.align(scr, lv.ALIGN.IN_TOP_MID,0,10)
    btn.set_event_cb(btn_event)
    lbl_btn = lv.label(btn)
    lbl_btn.set_text("Connect WiFi")
    
    #trigger config
    
    btn2 = lv.btn(scr)
    btn2.align(btn, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    btn2.set_event_cb(btn_event)
    lbl_btn2 = lv.label(btn2)
    lbl_btn2.set_text("Trigger Config")
    
    #run loop
    
    btn3 = lv.btn(scr)
    btn3.align(btn2, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    btn3.set_event_cb(btn_event)
    

def m6(): #wifi
    
    def btn_event(obj, event):
        
        if obj == btn2 and event == lv.EVENT.CLICKED:
            
            m5()
        
        if obj == ta and event == lv.EVENT.CLICKED:
            kb = lv.keyboard(scr)
            kb.set_textarea(ta)
        
            
            
            
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    tab = lv.tabview(scr)
   
    tab1 = tab.add_tab("Wifi Settings")
    
    btn2 = lv.btn(tab)
    btn2.align(tab, lv.ALIGN.IN_TOP_LEFT,0,0)
    lbl_btn2 = lv.label(btn2)
    lbl_btn2.set_text(lv.SYMBOL.HOME)
    btn2.set_fit(lv.FIT.TIGHT)
    btn2.set_event_cb(btn_event)
        
    cont = lv.cont(tab1)
    cont.align(tab1, lv.ALIGN.IN_TOP_MID,0,20)  
    cont.set_fit2(lv.FIT.TIGHT,lv.FIT.TIGHT)
        
    ta = lv.textarea(cont)
    ta.align(cont, lv.ALIGN.IN_TOP_MID,0,10)
    ta.set_one_line(True)
    ta.set_event_cb(btn_event)
    
    btn = lv.btn(cont)
    btn.align(ta, lv.ALIGN.OUT_BOTTOM_MID,0,0)
       
    
    #import network
            
    #global sta_if
            
    #sta_if = network.WLAN(network.STA_IF)
    #sta_if.active(True)
    #sta_if.connect("norzam5001-93A8", "")
    #sta_if.isconnected()
    
            
def m_task():
    
    m5()
    
    current = 0
    previous = 0
    treshold = 1000
    
    while True:
        
        lv.task_handler()
        lv.tick_inc(5)
        
        current = utime.ticks_ms()
        
        if current - previous > treshold:
            print('hello world')
            previous = utime.ticks_ms()
        
m_task()





