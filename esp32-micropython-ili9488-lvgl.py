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


class Clock:
    
    def __init__(self):
        
        self.hour   = 0
        self.minute = 0
        self.second = 0
        self.daysOfWeek = 0
    
    def print(self):
        print("{}:{}:{}".format(str(self.hour), str(self.minute), str(self.second)))
        
class Trigger:
    
    def __init__(self):
        
        self.name = ""
        self.desc = ""
        
        self.bhour     = 0
        self.bminute   = 0
        self.bsecond   = 0
    
        self.ehour     = 0
        self.eminute   = 0
        self.esec      = 0
        
        self.hourdur   = 0
        self.minutedur = 0
        self.seconddur = 0
        
        self.isArmed            = False
        self.isTriggered        = False
        
        self.isFlowSensorEnable = False
        self.maxFlowLimit       = 0
        self.minFlowLimit       = 0
        self.minFlowTime        = 0
        
        self.isRainSensorEnable = False
        self.rainSensorTimeCheck= False
        
        self.isMETapiEnable     = False
        
        self.isSoilSensorEnable = False

clock = Clock()

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
    
    #dropdown - event callback here
    
    def btn_event(obj, event):
        
        if obj == drop and event == lv.EVENT.VALUE_CHANGED:
        
            position = drop.get_selected()
            print("changing trigger position to {}".format(str(position)))
            m4_1(position) #call to refresh roller position
            
        if obj == home and event == lv.EVENT.CLICKED:
            m5() #return home
    
    #Trigger Config Page
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #container for drop and switch
    cont = lv.cont(scr)
    cont.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    cont.set_style_local_radius(0,0,0)
    cont.set_style_local_pad_all(0,0,0)
    
    #back to home button
    home = lv.btn(cont)
    home.align(cont, lv.ALIGN.IN_LEFT_MID,-20,0)
    home.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    home.set_style_local_radius(0,0,0)
    home.set_event_cb(btn_event)
    
    lbl_home = lv.label(home)
    lbl_home.set_text(lv.SYMBOL.HOME)
    
    
    #dropdown
    drop = lv.dropdown(cont)
    drop.align(home, lv.ALIGN.OUT_RIGHT_MID,5,0)
    drop.set_style_local_border_post(lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE,lv.BORDER_SIDE.NONE)
    drop.set_options("Trigger 1\nTrigger 2\nTrigger 3\nTrigger 4\nTrigger 5\nTrigger 6\nTrigger 7\nTrigger 8\nTrigger 9\n Trigger 10")
    drop.set_event_cb(btn_event)
    
    #label
    lbl1 = lv.label(cont)
    lbl1.align(drop, lv.ALIGN.OUT_RIGHT_MID,0,0)
    lbl1.set_text("Arm?")
    
    #switch
    switch = lv.switch(cont)
    switch.align(lbl1, lv.ALIGN.OUT_RIGHT_MID,0,0)
    
    #tabview
    tab = lv.tabview(scr)
    tab.align(cont, lv.ALIGN.OUT_BOTTOM_MID,0,0)
    
    tab1 = tab.add_tab("Time")
    tab2 = tab.add_tab("Auto")
    tab3 = tab.add_tab("Switches")
    tab4 = tab.add_tab("Desc")
    
    
####Tab 1 - Trigger Config
    
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
    
    #button (set timer) - event (set start and end)
    
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
            
            print("btn2 - end duration set")
            
            #calculate end duration
            #set to current trigger begin position
            endhour = trigger[position].bhour
            endminute = trigger[position].bminute
            endsecond = trigger[position].bsecond
            
            #convert to seconds
            totalseconds = (trigger[position].hourdur * 60 * 60) + (trigger[position].minutedur * 60) + trigger[position].seconddur
            
            #new end trigger time
            
            for i in range(1, totalseconds):
                
                endsecond + 1
                
                if endsecond > 1:
                    endminute += 1
                    endsecond = 0
                    
                if endminute >59:
                    endhour += 1
                    endminute = 0
                    
                if endhour > 23:
                    endhour = 0
                    
            #set value to class Trigger
            trigger[position].ehour = endhour
            trigger[position].eminute = endminute
            trigger[position].esec = endsecond
            
            print("End trigger time is SET")
        
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


''' Original M5()
def m5(): # home screen
    
    #main bootup
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    # btn_event (declare before others)
    
    #run menu command based on buttton event below
    def btn_event(obj, event):
        
        if (obj == btn) and (event == lv.EVENT.CLICKED):
            m6()
                       
        if (obj == btn2) and (event == lv.EVENT.CLICKED):
            m4() #trigger config
            
        if (obj == btn3) and (event == lv.EVENT.CLICKED):
            return
                
    #create tab by rectangle
        
       
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
'''

def m5():
    
    scr = lv.obj()
    lv.scr_load(scr)
       
    #Buttong Event - create this below is the menu
    def btn_event(obj, event):
        
        if obj == b1 and event == lv.EVENT.CLICKED:    #Timer config
            m4()
        
        if obj == b2 and event == lv.EVENT.CLICKED:    #Wifi Config
            m6() #temp
            
        if obj == b3 and event == lv.EVENT.CLICKED:    #Dashborad
            m7() #temp
            
        if obj == b4 and event == lv.EVENT.CLICKED:
            m5() #temp
            
        if obj == b5 and event == lv.EVENT.CLICKED:
            m5() #temp
            
        if obj == b6 and event == lv.EVENT.CLICKED:
            m5() #temp
            
    #top tab
    cont = lv.cont(scr)
    cont.align(scr, lv.ALIGN.IN_TOP_LEFT,0,0)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    lbl_today = lv.label(cont)
    
    lbl_today.set_text("Sunday     14-01-2021     {}:{}:{}".format(str(clock.hour),str(clock.minute),str(clock.second)))
    
    lbl_today.align(cont, lv.ALIGN.CENTER,0,10)
 
 #List of boxes using button
    
    #1st column
    b1 = lv.btn(scr)
    b1.align(cont, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)
    b1.set_height(100)
    b1.set_style_local_radius(0,0,0)
    b1.set_event_cb(btn_event) #callback
    lbl_b1 = lv.label(b1) 
    lbl_b1.set_text("Timer Config")
        
    b3 = lv.btn(scr)
    b3.align(b1, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
    b3.set_height(100)
    b3.set_style_local_radius(0,0,0)
    b3.set_event_cb(btn_event)
    lbl_b3 = lv.label(b3)
    lbl_b3.set_text("Dashboard")
    
    b5 = lv.btn(scr)
    b5.align(b3, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
    b5.set_height(100)
    b5.set_style_local_radius(0,0,0)
    b5.set_event_cb(btn_event)
    lbl_b5 = lv.label(b5)
    lbl_b5.set_text("Manual Control")
    
    
    #2nd column
    b2 = lv.btn(scr)
    b2.align(cont, lv.ALIGN.OUT_BOTTOM_RIGHT, -10, 10)
    b2.set_height(100)
    b2.set_style_local_radius(0,0,0)
    b2.set_event_cb(btn_event)
    lbl_b2 = lv.label(b2)
    lbl_b2.set_text("Wifi Config")
           
    b4 = lv.btn(scr)
    b4.align(b2, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
    b4.set_height(100)
    b4.set_style_local_radius(0,0,0)
    b4.set_event_cb(btn_event)
    lbl_b4 = lv.label(b4)
    lbl_b4.set_text("Clock Config")
    
    b6 = lv.btn(scr)
    b6.align(b4, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
    b6.set_height(100)
    b6.set_style_local_radius(0,0,0)
    b6.set_event_cb(btn_event)
    lbl_b6 = lv.label(b6)
    lbl_b6.set_text("Phone Config")
    
    
''' Original
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
'''


def clock_tick(): 
    
    clock.second += 1 #add 1 to second everytime function call
    
    if clock.second > 59:
        clock.second = 0
        clock.minute += 1
        
    if clock.minute > 59:
        clock.minute = 0
        clock.hour += 1
    
    if clock.hour > 23:
        clock.hour = 0
        
def trigger_check():
    
    for t in trigger:
               
        #switch on trigger
        if t.bhour == clock.hour and t.bminute == clock.minute and t.bsecond == clock.second and t.isArmed == True:    
            t.isTriggered == True
            print('trigger is Turned ON')
            
            
        #swithc off trigger
        if t.ehour == clock.hour and t.eminute == clock.minute and t.esec == clock.second:    
            t.isTriggered == False
            
            
            
def m6():    #Wifi Settings
    
    
    #list event callback
    
    
    
    #button call back
    
    def list_event(obj, event):
        
        list_btn = lv.list.__cast__(obj)
        
        if event == lv.EVENT.CLICKED:
            
            print(list_btn.get_btn_text())
            
            m6_1(list_btn.get_btn_text())
            
    def btn_event(obj, event):
        
        if obj == home and event == lv.EVENT.CLICKED:
            m5()
            
        if obj == switch and event == lv.EVENT.VALUE_CHANGED:
            print('Value change : ' + str(obj.get_state()))
            
            if obj.get_state() == True:
                
                print('Enabling Wifi')
                sta_if.active(True)
                data = sta_if.scan()
                
                list = lv.list(scr)
                list.align(cont1, lv.ALIGN.OUT_BOTTOM_MID,0,0)
                                
                for d in data:
                    list.add_btn(lv.SYMBOL.RIGHT, str(d[0].decode('UTF-8'))).set_event_cb(list_event)
            
            if obj.get_state() == False:
                
                print('Disabling Wifi')
                sta_if.active(False)
                
                
    
    
    scr = lv.obj()
    lv.scr_load(scr)
    
    #top tab dengan home button
    cont = lv.cont(scr)
    cont.set_auto_realign(True)
    cont.set_style_local_radius(0,0,0)
    cont.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    
    #home button
    home = lv.btn(cont)
    home.align(cont, lv.ALIGN.IN_LEFT_MID, 0,10)
    home.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    home.set_event_cb(btn_event)
    lbl_home = lv.label(home)
    lbl_home.set_text(lv.SYMBOL.HOME)
    
    #label top tab
    
    lbl_top = lv.label(cont)
    lbl_top.set_text("Wifi Config")
    lbl_top.align(home, lv.ALIGN.OUT_RIGHT_MID,10,0)
    
    #set wifi
    
    cont1 = lv.cont(scr)
    cont1.set_auto_realign(True)
    cont1.align(cont, lv.ALIGN.OUT_BOTTOM_MID,0,20)
    cont1.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    
    lbl_en_wifi = lv.label(cont1)
    lbl_en_wifi.set_text("Enable Wifi")
    lbl_en_wifi.align(cont1, lv.ALIGN.IN_LEFT_MID, 10, 10)
    switch = lv.switch(cont1)
    switch.align(lbl_en_wifi, lv.ALIGN.OUT_RIGHT_MID, 100, 0)
    switch.set_event_cb(btn_event)
    
    

def m6_1(data): #wifi password window
    
    #button events
    def btn_event(obj, event):
        
        if obj == home and event == lv.EVENT.CLICKED:
            m5()
            
    def kbd_event_cb(obj, event):
        
        obj.def_event_cb(event)
            
        if event == lv.EVENT.APPLY:
           
           print('OK button pressed')
           print(password.get_text())
           obj.delete()
           
           print('connecting to ' + data)
           print('using password ' + password.get_text())
           
           log = lv.label(scr)
           log.align(cont1, lv.ALIGN.OUT_BOTTOM_MID,0,10)
           text = 'Trying to connect'
           
           if not sta_if.isconnected():
               log.set_text(text)
               
               sta_if.connect(data, password.get_text())
               while not sta_if.isconnected():
                   text = text + " . "
                   log.set_text(text)
           
           #if successful
           log.set_text('Successfully connected')
           log.align(cont1, lv.ALIGN.OUT_BOTTOM_MID,0,10)
           
               

    
    #main page
    scr = lv.obj()
    lv.scr_load(scr)
    
    #top tab dengan home button
    cont = lv.cont(scr)
    cont.set_auto_realign(True)
    cont.set_style_local_radius(0,0,0)
    cont.align(scr, lv.ALIGN.IN_TOP_MID,0,0)
    cont.set_fit2(lv.FIT.PARENT, lv.FIT.TIGHT)
    
    #home button
    home = lv.btn(cont)
    home.align(cont, lv.ALIGN.IN_LEFT_MID, 0,10)
    home.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    home.set_event_cb(btn_event)
    lbl_home = lv.label(home)
    lbl_home.set_text(lv.SYMBOL.HOME)
    
    #label top tab
    
    lbl_top = lv.label(cont)
    lbl_top.set_text("Wifi Config")
    lbl_top.align(home, lv.ALIGN.OUT_RIGHT_MID,10,0)
    
    #set wifi
    
    cont1 = lv.cont(scr)
    cont1.set_auto_realign(True)
    cont1.align(cont, lv.ALIGN.OUT_BOTTOM_MID,0,20)
    cont1.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    
    lbl_en_wifi = lv.label(cont1)
    lbl_en_wifi.set_text("Connecting to " + data)
    lbl_en_wifi.align(cont1, lv.ALIGN.IN_LEFT_MID, 10, 10)
    
    lbl_in_pass = lv.label(cont1)
    lbl_in_pass.set_text("Insert Wifi password : ")
    lbl_in_pass.align(lbl_en_wifi, lv.ALIGN.OUT_BOTTOM_MID,0, 10)
    
    #text area for password
    
    password = lv.textarea(cont1)
    password.set_size(200,50)
    password.align(lbl_in_pass, lv.ALIGN.OUT_BOTTOM_MID,0,10)
    password.set_pwd_mode(True)
    password.set_text("")
    
    keyboard = lv.keyboard(scr)
    keyboard.set_size(320, 480 // 2)
    keyboard.set_textarea(password)
    keyboard.set_cursor_manage(False)
    keyboard.set_event_cb(kbd_event_cb)
            
            
def m7(): # dashboard

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
    home_button.set_event_cb(btn_event)
    
    lbl_home = lv.label(home_button)
    lbl_home.set_text(lv.SYMBOL.HOME)
    
    lbl_header = lv.label(cont)
    lbl_header.set_text("Dashboard")
    lbl_header.align(home_button, lv.ALIGN.OUT_RIGHT_MID,10,0)

    tab_header = lv.tabview(scr)
    tab_header.align(cont, lv.ALIGN.OUT_BOTTOM_MID, 0, 0)

    tab1 = tab_header.add_tab("Triggers")
    tab2 = tab_header.add_tab("Switches")
    tab3 = tab_header.add_tab("Sensors")
    tab4 = tab_header.add_tab("Charts")

    #tab1 : Triggers
    
    '''
    tab1.set_auto_realign(True)
    tab1.set_layout(lv.LAYOUT.PRETTY_TOP)
    '''
    
    cont1 = lv.cont(tab1)
    cont1.set_auto_realign(True)
    cont1.set_fit2(lv.FIT.TIGHT, lv.FIT.TIGHT)
    cont1.set_layout(lv.LAYOUT.PRETTY_TOP)
    
    card = []
    
    for i in range(0, len(trigger)):
        
        card.append(lv.cont(cont1))
        card[i].set_width(220)
        card[i].set_height(100)
        
        lbl_trigger = lv.label(card[i])
        lbl_trigger.set_text("Trigger " + str(i))
        
    #making trigger cards
   
def m_task():
    
    m5()
    
    current = 0
    previous = 0
    treshold = 1000
    
    while True:
        
        
        lv.task_handler()
        lv.tick_inc(5)        
        current = utime.ticks_ms()
        
        '''
        Clock Function
        '''
        if current - previous > treshold:
            clock_tick()
            trigger_check()
            clock.print()
            previous = utime.ticks_ms()
        
m_task()




