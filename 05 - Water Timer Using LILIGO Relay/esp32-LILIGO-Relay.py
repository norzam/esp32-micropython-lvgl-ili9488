import utime
import machine
from machine import Timer
import network
import ntptime

#ILI9488
from espidf import VSPI_HOST
import lvgl as lv
LED     = 22   #RED
T_CS    = 26   #PURPLE
MOSI    = 13   #GREEN
RESET   = 27   #ORANGE
DC      = 32   #WHITE
MISO    = 12   #GREY
CS      = 15   #LIGHT BROWN
CLK     = 14   #BLUE


from ili9XXX import ili9488
disp = ili9488(miso=12, mosi=13, clk=14, cs=15, dc=32, rst=27, power=-1, backlight=22, backlight_on=1, power_on=1, rot=0x80,
        spihost=VSPI_HOST, mhz=60, factor=16, hybrid=True, width=320, height=480,
        invert=False, double_buffer=True, half_duplex=False, initialize=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=T_CS, spihost=VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

lv.init()

#LED auto brightness settings
led = machine.Pin(LED)
led_pwm = machine.PWM(led)
#led_pwm.freq(1000)    #blinking speed
led_pwm.duty(1000)  # brightness
lcd_threshold  = 30 * 1000
lcd_current_duty = 1023

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
print(sta_if.scan())

#Trigger List
#hb         = hour to begin
#mb         = minute to begin
#sb         = second to begin
#dur        = duration to trigger in seconds
#timerno    = timer variable number (auto)
#daysoweek  = days of week (sunday to saturday) in number to enable trigger 
#cardnum    = the trigger position assigned to card_items (lv.btn)
#sec_start  = store the time (utime.time()) when trigger started`

#INITIAL TIMERS
trigger = [{'name':'Baja A', 'hb':0, 'mb':0, 'sb':5, 'dur':15, 'pin':5, 'timerno':0,'cardnum':0, 'daysoweek':[0,1,2,3,4,5,6], 'sec_start':0},
           {'name':'Baja B', 'hb':0, 'mb':0, 'sb':6, 'dur':25, 'pin':18, 'timerno':0,'cardnum':0, 'daysoweek':[0,1,2,3,4,5,6], 'sec_start':0},
           {'name':'Pam Air','hb':0, 'mb':0, 'sb':7, 'dur':35, 'pin':19, 'timerno':0,'cardnum':0, 'daysoweek':[0,1,2,3,4,5,6], 'sec_start':0}]

#GLOBAL VALUES
timer_counter = 0
primary = lv.color_hex(0x1822bf)
#primary_enable = lv.color_hex(0x03735c) #darker green
primary_enable = lv.color_hex(0x18BF62) #lighter green options
primary_disable = lv.color_hex(0x8867a7)
red = lv.color_hex(0xfc0000)

############
# FUNCTIONS
############

def current_time():
    return machine.RTC().datetime()

#This will check if trigger time  == current time
def isTriggerMatch(trigger_items):
    
    current_t = current_time()
    trigger_items = trigger_items
    
    if trigger_items['hb'] == current_t[4] and trigger_items['mb'] == current_t[5] and \
       trigger_items['sb'] == current_t[6]:
        return True

    else:
        return False

#This will check if trigger dayofweek matches current daysofweek
def isDaysoWeekMatch(trigger_item):
    current_dow = machine.RTC().datetime()[3]
    trigger_dow = trigger_item['daysoweek']

    if current_dow in trigger_dow:
        return True
    else:
        return False

def isCurrentTriggerPinDisable(trigger_item):
    current_trigger_pin = machine.Pin(trigger_item['pin']).value()

    if current_trigger_pin == 0:
        return True
    else:
        return False
       
#simple function to set the ESP32 time
def set_time(year, month, day, dayoweek, hour, minute, sec):
    machine.RTC().datetime((year, month, day, dayoweek, hour, minute, sec, 0))

#This will turn switch trigger ON, set a timer using duration to call timer_cb to turn OFF switch.
def trigger_logic(trigger_item):

    trigger_item = trigger_item
    
    #main switching algo. 
    #check  1. is Pin in OFF position, if already ON ignore
    #check  2. isTriggerMatch True?
    #check  3. daysOfWeek True?
    
    if  isTriggerMatch(trigger_item) and\
        isCurrentTriggerPinDisable(trigger_item) and\
        isDaysoWeekMatch(trigger_item):
        
        global timer_counter
        
        print('switching ON : Pin{}'.format(trigger_item['pin']))

        #result Pin set to ON.
        #result set a Time to turn off.
        #result timer_counter added.``
        machine.Pin(trigger_item['pin'], machine.Pin.OUT).on()
        print('Init Timer({})'.format(timer_counter))

        #create a timer
        Timer(timer_counter)
        Timer(timer_counter).init(period=trigger_item['dur'] * 1000, mode=Timer.ONE_SHOT,
                            callback=lambda t: timer_cb(trigger_item))
        
        trigger_item['timerno'] = timer_counter
        trigger_item['sec_start'] = utime.time()

        timer_counter = timer_counter + 1

#Timer call back
def timer_cb(trigger_item):
    print('timer callback : Timer({}), switching OFF pin{}'.format(trigger_item['timerno'], trigger_item['pin']))
    machine.Pin(trigger_item['pin'], machine.Pin.OUT).off()
    trigger_item['timerno'] = 0
    trigger_item['sec_start'] = 0
    Timer(trigger_item['timerno']).deinit()

def auto_bg_main_stop(sec_start, dur):
    ##255 max, 0 min
    ##duration max = 255
    ##duration_portion = 255/duration
    portion_size = int(255/dur) * (utime.time()-sec_start)
    grad_val = int(255 - portion_size)
    return grad_val

def auto_bg_grad_stop(sec_start, dur):
    portion_size = int(255/(dur+10)) * (utime.time()-sec_start)
    grad_val = int(255 - portion_size)
    return grad_val
   
    
def gui_main():

    global scr

    def btn_event(event, params):

        #Relay1
        if params == 'relay1' and machine.Pin(21).value() == 1:
            machine.Pin(21, machine.Pin.OUT).off()

        elif params == 'relay1' and machine.Pin(21).value() == 0:        
            print('Button Pressed')
            machine.Pin(21, machine.Pin.OUT).on()
        
        #Relay2
        elif params == 'relay2' and machine.Pin(19).value() == 1:
            machine.Pin(19, machine.Pin.OUT).off()

        elif params == 'relay2' and machine.Pin(19).value() == 0:        
            print('Button Pressed')
            machine.Pin(19, machine.Pin.OUT).on()
        
        #Relay3

        elif params == 'relay3' and machine.Pin(18).value() == 1:
            machine.Pin(18, machine.Pin.OUT).off()

        elif params == 'relay3' and machine.Pin(18).value() == 0:        
            print('Button Pressed')
            machine.Pin(18, machine.Pin.OUT).on()

        #Relay4

        elif params == 'relay4' and machine.Pin(5).value() == 1:
            machine.Pin(5, machine.Pin.OUT).off()

        elif params == 'relay4' and machine.Pin(5).value() == 0:        
            print('Button Pressed')
            machine.Pin(5, machine.Pin.OUT).on()

        elif params == 'header':
            gui_time()

        elif params == 'other_settings':
            gui_other_settings()

        elif params['name'] == 'save_to_db':
            save_to_db(trigger)

        elif params['name'] == 'open_db':
            open_db()
        
        

    scr = lv.obj()
    lv.scr_load(scr)
    #scr.set_style_bg_color(lv.color_hex(0x010101), 0)

    header=lv.btn(scr)
    header.set_size(320,50)
    header.set_style_bg_color(primary,0 )
    header.add_event_cb(lambda task:btn_event(task, 'header'), lv.EVENT.CLICKED, None)

    label = lv.label(header)

    def refresh_label(btn1, btn2, btn3, btn4):
        #label date/time
        label.set_text('{:02}/{:02}/{:02}  {:02}:{:02}:{:02}'.format(current_time()[2], current_time()[1], \
            current_time()[0], current_time()[4],  current_time()[5],  current_time()[6]))

        pins = [{'pinno':21, 'relayno':'Relay 1', 'btn':btn1}, {'pinno':19, 'relayno':'Relay 2', 'btn':btn2}, 
        {'pinno':18, 'relayno':'Relay 3', 'btn':btn3}, {'pinno':5, 'relayno':'Relay 4', 'btn':btn4}]                
        
        #change color of buttons
        def check_card(relay, status):
            for card in card_items:

                if relay in card.get_child(0).get_text():

                    trig = trigger[int(card.get_child(1).get_text())] #getting trigger number from btn. hid in label   

                    if status == 'on' and trig['sec_start'] > 0:
                        #animate cards
                        card.set_style_bg_color(primary_enable, 0)
                        card.set_style_bg_grad_color(primary,0)
                        card.set_style_bg_grad_dir(lv.GRAD_DIR.HOR, 0)
                        card.set_style_bg_main_stop(auto_bg_main_stop(trig['sec_start'], trig['dur']),0)
                        card.set_style_bg_grad_stop(auto_bg_grad_stop(trig['sec_start'], trig['dur']),0)

                    elif status == 'off':
                        card.set_style_bg_color(primary,0)
        
        #change color logic (relay btn and cards items)
        for pin in pins:
            #if off
            if machine.Pin(pin['pinno']).value() == 0:
                pin['btn'].set_style_bg_color(primary, 0)
                check_card(pin['relayno'], 'off')

            #if on
            if machine.Pin(pin['pinno']).value() == 1:
                pin['btn'].set_style_bg_color(primary_enable, 0)
                check_card(pin['relayno'], 'on')

        #updating cards item information
        for num, card in enumerate(card_items,0):
            trig = trigger[num]

            #if timer is running, change duration to time left
            if trig['sec_start'] > 0:
                running_time = int(utime.time()-trig['sec_start'])
                time_left = int(trig['dur'] - running_time)
                card.get_child(0).set_text('Name : {} \nTime Begin : {:02}:{:02}:{:02}\nTime Left : {} seconds\nPin to Trigger : {}\
                \nDays of Week : {}\nTimer No :  {} '.format(trig['name'], trig['hb'], trig['mb'], trig['sb'], str(time_left),
                relayname[trig['pin']], str(trig['daysoweek']), trig['timerno'] ))

            #if timer not running, use default
            else:
                card.get_child(0).set_text('Name : {} \nTime Begin : {:02}:{:02}:{:02}\nDuration : {} seconds\nPin to Trigger : {}\
                \nDays of Week : {}\nTimer No :  {} '.format(trig['name'], trig['hb'], trig['mb'], trig['sb'], trig['dur'],
                relayname[trig['pin']], str(trig['daysoweek']), trig['timerno'] ))

    lv.timer_create(lambda task: refresh_label(btn1, btn2, btn3, btn4), 600, None)

    label.set_style_text_font(lv.font_montserrat_28,0)
    label.center()

    label2 = lv.label(scr)
    label2.set_text('Manual Control')
    label2.align_to(header, lv.ALIGN.OUT_BOTTOM_LEFT,10,10)

    btn1 = lv.btn(scr)
    btn1.set_size(130, 60)
    btn1.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)
    btn1_label = lv.label(btn1)
    btn1_label.set_text('Relay 1')
    btn1_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn1_label.center()
    btn1.add_event_cb(lambda task: btn_event(task,'relay1'),lv.EVENT.CLICKED, None)

    btn2 = lv.btn(scr)
    btn2.set_size(130, 60)
    btn2.align_to(btn1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    btn2_label = lv.label(btn2)
    btn2_label.set_text('Relay 2')  
    btn2_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn2_label.center()
    btn2.add_event_cb(lambda task: btn_event(task,'relay2'),lv.EVENT.CLICKED, None)

    btn3 = lv.btn(scr)
    btn3.set_size(130, 60)
    btn3.align_to(btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    btn3_label = lv.label(btn3)
    btn3_label.set_text('Relay 3')  
    btn3_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn3_label.center()
    btn3.add_event_cb(lambda task: btn_event(task,'relay3'),lv.EVENT.CLICKED, None)

    btn4 = lv.btn(scr)
    btn4.set_size(130,60)
    btn4.align_to(btn3, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    btn4_label = lv.label(btn4)
    btn4_label.set_text('Relay 4')  
    btn4_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn4_label.center()
    btn4.add_event_cb(lambda task: btn_event(task,'relay4'),lv.EVENT.CLICKED, None)

    label3 = lv.label(scr)
    label3.align_to(btn3, lv.ALIGN.OUT_BOTTOM_LEFT, -20, 20)
    label3.set_text('Trigger Preset (Tap to edit)')

    #cards
    
    def card_event_handler(task, trig, flag):
        if flag == 'edit':
            num = int(task.get_target().get_child(1).get_text())
            print('Card Event Handler Num : {}'.format(num))
            gui_edit_trigger(num, flag)
        
        elif flag == 'new':
            gui_edit_trigger(99, flag)

    global card_items
    card_items = []
    
    for num, trig in enumerate(trigger,0):
    
        card_items.append(lv.btn(scr))
        card_items[num].set_style_bg_color(primary_disable,0)
        card_items[num].set_size(250, 100)
        trig['cardnum'] = num
        card_items[num].add_event_cb(lambda task: card_event_handler(task, trig, 'edit'), lv.EVENT.CLICKED, None)
        print('Card Event Num : {}'.format(num))

        if num == 0:
            card_items[num].align_to(label3, lv.ALIGN.OUT_BOTTOM_LEFT, 30, 10)
        
        else:
            card_items[num].align_to(card_items[num-1],lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

        relayname = {21:'Relay 1', 19:'Relay 2', 18:'Relay 3' , 5:'Relay 4'}

        card_lbl1 = lv.label(card_items[num])
        card_lbl1.set_text('Name : {} \nTime Begin : {:02}:{:02}:{:02}\nDuration : {} seconds\nPin to Trigger : {}\
            \nDays of Week : {}\nTimer No :  {} '.format(trig['name'], trig['hb'], trig['mb'], trig['sb'], trig['dur'],
             relayname[trig['pin']], str(trig['daysoweek']), trig['timerno'] ))
        
        card_lbl2 = lv.label(card_items[num])
        card_lbl2.set_text(str(num))
        card_lbl2.align_to(card_items[num], lv.ALIGN.TOP_RIGHT,0,0)

    btn5 = lv.btn(scr)
    btn5_lbl = lv.label(btn5)
    btn5_lbl.set_text('Add New Trigger')
    btn5.align_to(card_items[-1], lv.ALIGN.OUT_BOTTOM_LEFT,0, 20)
    btn5.add_event_cb(lambda task: card_event_handler(task, len(trigger)+1, 'new'), lv.EVENT.CLICKED, None)
    btn5.set_style_bg_color(primary, 0)

    btn6 = lv.btn(scr)
    btn6.set_style_bg_color(primary, 0)
    btn6_lbl = lv.label(btn6)
    btn6_lbl.set_text('Save to DB')
    btn6.add_event_cb(lambda task: btn_event(task, {'name':'save_to_db'}), lv.EVENT.CLICKED, None)
    btn6.align_to(btn5, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    btn6_1 = lv.btn(scr)
    btn6_1_label = lv.label(btn6_1)
    btn6_1_label.set_text('Load from DB')
    btn6_1.add_event_cb(lambda task: btn_event(task, {'name':'open_db'}), lv.EVENT.CLICKED, None)
    btn6_1.align_to(btn6, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    btn7 = lv.btn(scr)
    btn7.set_style_bg_color(primary_disable, 0)
    btn7_lbl = lv.label(btn7)
    btn7_lbl.set_text('Other Settings')
    btn7.align_to(btn6_1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    btn7.add_event_cb(lambda task: btn_event(task, 'other_settings'), lv.EVENT.CLICKED, None)

    return scr

def gui_time():
    
    global scr2, calendar

    selected_date_day = 0
    selected_date_month = 0
    selected_date_year = 0

    def btn_event(event, params):
        if params == 'cancel':
            lv.scr_load(scr)

        elif params['name'] == 'save':
            set_time(params['year'], params['month'], params['day'], 0, params['hour'], params['minute'], params['seconds'])
            lv.scr_load(scr)
            #implements set time

        elif params['name'] == 'NTP':
            if sta_if.isconnected():
                ntptime.settime()
            else:
                print('Connect to WIFI')

    def event_handler(task, params):
        
        code = task.get_code()

        if code == lv.EVENT.VALUE_CHANGED:
            source = task.get_current_target()
            date = lv.calendar_date_t()

            if source.get_pressed_date(date) == lv.RES.OK:

                calendar.set_today_date(date.year, date.month, date.day)
                print("Clicked date: %02d.%02d.%02d"%(date.day, date.month, date.year))
                label1.set_text('Set Date : {} - {} - {}'.format(date.year, date.month, date.day))

                params['year']  = date.year
                params['month'] = date.month
                params['day']   = date.day
        
    scr2 = lv.obj()
    lv.scr_load(scr2)

    #CANCEL
    btn1 = lv.btn(scr2)
    btn1.set_size(120, 40)
    btn1.set_style_bg_color(primary, 0)
    btn1_label = lv.label(btn1)
    btn1_label.set_text('Cancel')
    #btn1_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn1_label.center()
    btn1.align_to(scr2, lv.ALIGN.TOP_LEFT, 0, 0)
    btn1.add_event_cb(lambda task:btn_event(task, 'cancel'), lv.EVENT.CLICKED, None)

    #SAVE
    btn2 = lv.btn(scr2)
    btn2.set_size(120, 40)
    btn2.set_style_bg_color(primary, 0)
    btn2_label = lv.label(btn2)
    btn2_label.set_text('Save')
    #btn2_label.set_style_text_font(lv.font_montserrat_28, 0)
    btn2_label.center()
    btn2.align_to(scr2, lv.ALIGN.TOP_RIGHT, 0, 0)
    btn2.add_event_cb(lambda task:btn_event(task,
    {'name':'save', 
     'hour':r1.get_selected(),
     'minute':r2.get_selected(),
     'seconds':r3.get_selected(),
     'year':selected_date_year,
     'month':selected_date_month,
     'day':selected_date_day}), lv.EVENT.CLICKED, None)

    
    label1 = lv.label(scr2)
    label1.set_text('Set Date : {} - {} - {}'.format(current_time()[0], current_time()[1], current_time()[2]))

    def refresh_label():
        label2.set_text('Set Time : {:02} : {:02} : {:02}'.format(r1.get_selected(), r2.get_selected(), r3.get_selected()))

    label1.align_to(btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)

    calendar = lv.calendar(scr2)
    calendar.set_size(240,180)
    calendar.align_to(label1, lv.ALIGN.OUT_BOTTOM_LEFT, int((320-250)/2)-10, 60 )
    
    calendar.add_event_cb(lambda task:event_handler(task, {'year':selected_date_year,
    'month':selected_date_month,
    'day':selected_date_day}), lv.EVENT.ALL, None)

    calendar.set_today_date(current_time()[0], current_time()[1], current_time()[2])
    calendar.set_showed_date(current_time()[0], current_time()[1])
    lv.calendar_header_dropdown(scr2, calendar)

    label2 = lv.label(scr2)
    
    label2.align_to(calendar, lv.ALIGN.OUT_BOTTOM_LEFT, -20, 10)

    #generate values for rollers
    dump = []
    for i in range(0,24):
        dump.append(str(i))
        
    opts1 = "\n".join(dump)
    del dump
    
    dump = []
    for i in range(0,60):
        dump.append(str(i))
        
    opts2 = "\n".join(dump)
    del dump

    r1 = lv.roller(scr2)
    r1.set_width(80)
    r1.set_height(60)
    r1.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT,15,20)
    r1.set_options(opts1, lv.roller.MODE.NORMAL)
    r1.set_selected(current_time()[4], lv.ANIM.ON)

    r2 = lv.roller(scr2)
    r2.set_width(80)
    r2.set_height(60)
    r2.align_to(r1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    r2.set_options(opts2, lv.roller.MODE.NORMAL)
    r2.set_selected(current_time()[5], lv.ANIM.ON)

    r3 = lv.roller(scr2)
    r3.set_width(80)
    r3.set_height(60)
    r3.align_to(r2, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    r3.set_options(opts2, lv.roller.MODE.NORMAL)
    r3.set_selected(current_time()[6], lv.ANIM.ON)

    r1_lbl = lv.label(scr2)
    r1_lbl.set_text('Hour')
    r1_lbl.align_to(r1, lv.ALIGN.OUT_TOP_MID, 0, 0)

    r2_lbl = lv.label(scr2)
    r2_lbl.set_text('Minute')
    r2_lbl.align_to(r2, lv.ALIGN.OUT_TOP_MID, 0, 0)

    r3_lbl = lv.label(scr2)
    r3_lbl.set_text('Seconds')
    r3_lbl.align_to(r3, lv.ALIGN.OUT_TOP_MID, 0, 0)

    label3 = lv.label(scr2)
    label3.set_text('Sync with online NTP Time Server')
    label3.align_to(r1, lv.ALIGN.OUT_BOTTOM_LEFT, -20 ,10)

    btn3 = lv.btn(scr2)
    btn3_lbl = lv.label(btn3)
    btn3_lbl.set_text('Sync to NTP server')
    btn3.align_to(label3, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    btn3.add_event_cb(lambda event: btn_event(event, {'name':'NTP'}) ,lv.EVENT.CLICKED, None)

    #call refresh label
    lv.timer_create(lambda task: refresh_label(), 900, None)    


def gui_edit_trigger(num, flag):
    #num is to call trigger[num]
    #flag is to check 'new' or 'edit'
    #changes are stored in temp_trigger_item

    print('Printing Num : {}'.format(num))

    temp_trigger_item = trigger

    if flag == 'edit':
        temp_trigger_item = trigger[num]
        print('Btn Pressed : {}'.format(str(temp_trigger_item)))
    
    elif flag == 'new':
        print('Creating new Trigger')
        #template should match with INITIAL TIMERS
        temp_trigger_item = {'name':'New Trigger', 'hb':0, 'mb':0, 'sb':5, 'dur':5,
        'pin':5, 'timerno':0, 'cardnum':0, 'daysoweek':[0,1,2,3,4,5,6], 'sec_start':0}

    def check_daysoweek(checkbox_array):

        temp_daysoweek = []

        for num, check in enumerate(checkbox_array,0):
            if check.get_state() == True:
                temp_daysoweek.append(num)
    
        print(temp_daysoweek)
        return temp_daysoweek

    def btn_event(task, params):
        
        if params == 'cancel':
            lv.scr_load(scr)

        elif params['param'] == 'save' and params['flag'] == 'edit':
            print(params)
            temp_trigger_item['name']       = params['name']
            temp_trigger_item['hb']         = params['hb']
            temp_trigger_item['mb']         = params['mb']
            temp_trigger_item['sb']         = params['sb']
            temp_trigger_item['dur']        = params['dur']
            temp_trigger_item['pin']        = params['pin']
            temp_trigger_item['timerno']    = params['timerno']
            temp_trigger_item['cardnum']    = params['cardnum']
            temp_trigger_item['daysoweek']  = params['daysoweek']
            temp_trigger_item['sec_start']  = params['sec_start']
            print('Triger Edit : Settings saved')

            lv.scr_load(scr)

        elif params['param'] == 'save' and params['flag'] == 'new':
            
            del params['param']
            del params['flag']

            trigger.append(params)
            gui_main()

            print('new key added : {}'.format(params) )

    global scr3

    scr3 = lv.obj()
    lv.scr_load(scr3)

    btn1 = lv.btn(scr3)
    btn1.set_size(150, 40)
    btn1.set_style_bg_color(primary,0)
    btn1_label = lv.label(btn1)
    btn1_label.set_text('Cancel')
    btn1_label.center()
    btn1.align_to(scr3, lv.ALIGN.TOP_LEFT, 0, 0)
    btn1.add_event_cb(lambda task: btn_event(task, 'cancel'), lv.EVENT.CLICKED, None)

    btn2 = lv.btn(scr3)
    btn2.set_size(150, 40)
    btn2.set_style_bg_color(primary,0)
    btn2_label = lv.label(btn2)
    btn2_label.set_text('Save')
    btn2_label.center()
    btn2.align_to(scr3, lv.ALIGN.TOP_RIGHT, 0, 0)

    pinname = {'0':21, '1':19, '2':18, '3':5}

    btn2.add_event_cb(lambda task: btn_event(task, params={'param':'save', 
    'flag':flag,
    'name':ta_name.get_text(),
    'hb':r1.get_selected(),
    'mb':r2.get_selected(),
    'sb':r3.get_selected(),
    'dur':((r4.get_selected() * 60 * 60) + (r5.get_selected() * 60) + r6.get_selected()),
    'pin':pinname[str(drpdwn.get_selected())], 
    'timerno':0,
    'cardnum':0, 
    'daysoweek':check_daysoweek(checkbox),
    'sec_start':0}), lv.EVENT.CLICKED, None)

    def refresh_label():
        #label for activation time
        label3.set_text('Set trigger activation time\n{:02} : {:02} : {:02}'.format(r1.get_selected(), r2.get_selected(), r3.get_selected()))
        
        #label for duration
        durations = (r4.get_selected() * 60 * 60) + (r5.get_selected() * 60) + r6.get_selected()

        label4.set_text('Set Duration for trigger\n{:,} in seconds'.format(durations))

    label1 = lv.label(scr3)
    
    if flag == 'edit':
        label1.set_text('Edit Trigger Settings')
    
    elif flag == 'new':
        label1.set_text('New Trigger Settings')

    label1.align_to(btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)

    label2 = lv.label(scr3)
    label2.set_text('Trigger Name')
    label2.align_to(label1, lv.ALIGN.OUT_BOTTOM_LEFT,0, 10)

    def keyboard_event(task, kb, scr3):
        event = task.get_code()
        ta = task.get_target() #get ta object
        
        if event == lv.EVENT.FOCUSED:
            #enable keyboard
            kb.set_textarea(ta)
            kb.clear_flag(lv.obj.FLAG.HIDDEN)
            
            #hide others
            for i in range(6,scr3.get_child_cnt()):
                scr3.get_child(i).add_flag(lv.obj.FLAG.HIDDEN)

        if event == lv.EVENT.DEFOCUSED:
            #disable keyboard and hide
            kb.set_textarea(None)
            kb.add_flag(lv.obj.FLAG.HIDDEN)
            
            #show others
            for i in range(6,scr3.get_child_cnt()):
                scr3.get_child(i).clear_flag(lv.obj.FLAG.HIDDEN)
            
            
    ta_name = lv.textarea(scr3)
    ta_name.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    ta_name.add_text(temp_trigger_item['name']) 
    ta_name.set_size(205,40)
    ta_name.add_state(lv.STATE.FOCUSED)
    ta_name.add_event_cb(lambda task: keyboard_event(task, kb, scr3), lv.EVENT.ALL, None)
    
    kb = lv.keyboard(scr3)
    kb.align_to(ta_name, lv.ALIGN.OUT_BOTTOM_LEFT,-10, 10)
    kb.set_textarea(ta_name)
    kb.add_flag(lv.obj.FLAG.HIDDEN)

    label3 = lv.label(scr3)
    label3.set_text('Set trigger activation time')
    label3.align_to(ta_name, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    dump = []
    for i in range(0,24):
        dump.append(str(i))
        
    opts1 = "\n".join(dump)
    del dump
    
    dump = []
    for i in range(0,60):
        dump.append(str(i))

    opts2 = "\n".join(dump)
    del dump

    #Hour, Minute and Seconds to begin set using rollers
    r1 = lv.roller(scr3)
    r1.set_width(80)
    r1.set_height(80)
    r1.set_options(opts1, lv.roller.MODE.NORMAL)
    r1.align_to(label3, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 35)

    r2 = lv.roller(scr3)
    r2.set_width(80)
    r2.set_height(80)
    r2.set_options(opts2, lv.roller.MODE.NORMAL)
    r2.align_to(r1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)

    r3 = lv.roller(scr3)
    r3.set_width(80)
    r3.set_height(80)
    r3.set_options(opts2, lv.roller.MODE.NORMAL)
    r3.align_to(r2, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)

    if flag == 'edit':
        r1.set_selected(temp_trigger_item['hb'], lv.ANIM.ON)
        r2.set_selected(temp_trigger_item['mb'], lv.ANIM.ON)
        r3.set_selected(temp_trigger_item['sb'], lv.ANIM.ON)
    
    r1_lbl = lv.label(scr3)
    r1_lbl.set_text('Hour')
    r1_lbl.align_to(r1, lv.ALIGN.OUT_TOP_MID,0 ,0)

    r2_lbl = lv.label(scr3)
    r2_lbl.set_text('Minute')
    r2_lbl.align_to(r2, lv.ALIGN.OUT_TOP_MID,0 ,0)

    r3_lbl = lv.label(scr3)
    r3_lbl.set_text('Seconds')
    r3_lbl.align_to(r3, lv.ALIGN.OUT_TOP_MID,0 ,0)

    #Duration. Duration information is set in refresh_label()
    label4 = lv.label(scr3)
    label4.align_to(r1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    r4 = lv.roller(scr3)
    r4.set_width(80)
    r4.set_height(80)
    r4.set_options(opts1, lv.roller.MODE.NORMAL)
    r4.align_to(label4, lv.ALIGN.OUT_BOTTOM_LEFT,0,35)

    r5 = lv.roller(scr3)
    r5.set_width(80)
    r5.set_height(80)
    r5.set_options(opts2, lv.roller.MODE.NORMAL)
    r5.align_to(r4, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)

    r6 = lv.roller(scr3)
    r6.set_width(80)
    r6.set_height(80)
    r6.set_options(opts2, lv.roller.MODE.NORMAL)
    r6.align_to(r5, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)

    def convert(seconds):
        min, sec = divmod(seconds, 60)
        hour, min = divmod(min, 60)

        return [hour, min, sec]

    if flag == 'edit':
        convert(temp_trigger_item['dur'])
        r4.set_selected(convert(temp_trigger_item['dur'])[0], lv.ANIM.ON)
        r5.set_selected(convert(temp_trigger_item['dur'])[1], lv.ANIM.ON)
        r6.set_selected(convert(temp_trigger_item['dur'])[2], lv.ANIM.ON)

    r4_lbl = lv.label(scr3)
    r4_lbl.set_text('Hour')
    r4_lbl.align_to(r4, lv.ALIGN.OUT_TOP_MID,0 ,0)

    r5_lbl = lv.label(scr3)
    r5_lbl.set_text('Minute')
    r5_lbl.align_to(r5, lv.ALIGN.OUT_TOP_MID,0 ,0)

    r6_lbl = lv.label(scr3)
    r6_lbl.set_text('Seconds')
    r6_lbl.align_to(r6, lv.ALIGN.OUT_TOP_MID,0 ,0)

    #Relay Setup

    label5 = lv.label(scr3)
    label5.set_text('Assign Relay to Trigger')
    label5.align_to(r4, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    drpdwn = lv.dropdown(scr3)
    drpdwn.align_to(label5, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    drpdwn.set_options("\n".join(['Relay 1', 'Relay 2', 'Relay 3', 'Relay 4']))

    relayname = {21:'0', 19:'1', 18:'2' , 5:'3'}

    if flag == 'edit':
        drpdwn.set_selected(int(relayname[temp_trigger_item['pin']]))

    label6 = lv.label(scr3)
    label6.set_text('Set days of week to turn trigger :')
    label6.align_to(drpdwn, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    checkbox = []
    checkbox_lbl = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    for i in range(0, 6):

        checkbox.append(lv.checkbox(scr3))
        if i == 0:
            checkbox[i].align_to(label6, lv.ALIGN.OUT_BOTTOM_LEFT,0, 10)
        else:
            checkbox[i].align_to(checkbox[i-1], lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

        checkbox[i].set_text(checkbox_lbl[i])
        
        if flag == 'edit':
            if i in temp_trigger_item['daysoweek']:
                checkbox[i].add_state(lv.STATE.CHECKED)
        
        elif flag == 'new':
            checkbox[i].add_state(lv.STATE.CHECKED)
            
    if flag == 'edit':
        del_btn = lv.btn(scr3)
        del_btn_lbl = lv.label(del_btn)
        del_btn_lbl.set_text('Delete This Trigger!')
        del_btn.set_style_bg_color(red, 0)
        del_btn.align_to(checkbox[5], lv.ALIGN.BOTTOM_MID, 80, 100)  

    lv.timer_create(lambda task: refresh_label(), 900, None)

def gui_other_settings():

    global scr4, ta, kb

    def btn_event(task, params):

        if params == 'cancel':
            lv.scr_load(scr)

        elif params['name'] == 'wifi':
            global ssid
            global ta

            e = task.get_code()
            obj = task.get_target()
            ssid = obj.get_child(1).get_text()
            print('Wifi {}'.format(ssid))
            wifi_list.add_flag(lv.obj.FLAG.HIDDEN)
            ta.clear_flag(lv.obj.FLAG.HIDDEN)
            ta.set_placeholder_text('Insert Password for {}'.format(ssid))
            kb.clear_flag(lv.obj.FLAG.HIDDEN)

    def ta_event_cb(e,kb):
        code = e.get_code()
        ta = e.get_target()
        if code == lv.EVENT.FOCUSED:
            kb.set_textarea(ta)
            kb.clear_flag(lv.obj.FLAG.HIDDEN)

        if code == lv.EVENT.DEFOCUSED:
          
            user = ssid          
            password = ta.get_text()

            sta_if.connect(user, password)
            print('connecting {} {}'.format(str(user), str(password)))
            ta.add_flag(lv.obj.FLAG.HIDDEN)
            kb.add_flag(lv.obj.FLAG.HIDDEN)        

    def keyboard_event(e, ta):

        code = e.get_code()

        if code == lv.KEY.ENTER:
            user = ssid          
            password = ta.get_text()

            sta_if.connect(user, password)
            ta.add_flag(lv.obj.FLAG.HIDDEN)
            kb.add_flag(lv.obj.FLAG.HIDDEN)            

    def switch_handler(event):
        e = event.get_code()
        obj = event.get_target()

        if  e == lv.EVENT.VALUE_CHANGED:
            if obj.has_state(lv.STATE.CHECKED):
                print('Turn On Wifi')
                sta_if.active(True)
              

            elif obj.has_state(lv.STATE.DISABLED):
                print('Turn of Wifi')
                sta_if.active(False)

    scr4 = lv.obj()
    lv.scr_load(scr4)

    btn1 = lv.btn(scr4)
    btn1.set_size(150, 40)
    btn1.set_style_bg_color(primary,0)
    btn1_label = lv.label(btn1)
    btn1_label.set_text('Cancel')
    btn1_label.center()
    btn1.align_to(scr4, lv.ALIGN.TOP_LEFT, 0, 0)
    btn1.add_event_cb(lambda task: btn_event(task, 'cancel'), lv.EVENT.CLICKED, None)

    btn2 = lv.btn(scr4)
    btn2.set_size(150, 40)
    btn2.set_style_bg_color(primary,0)
    btn2_label = lv.label(btn2)
    btn2_label.set_text('Save')
    btn2_label.center()
    btn2.align_to(scr4, lv.ALIGN.TOP_RIGHT, 0, 0)

    label1 = lv.label(scr4)
    label1.set_text('Others settings')
    label1.align_to(btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)

    label2 = lv.label(scr4)
    
    def refresh_label():
        label2.set_text('Enable Wifi : Connected? {}'.format(sta_if.isconnected()))

    lv.timer_create(lambda task: refresh_label(), 800, None)

    label2.align_to(label1, lv.ALIGN.OUT_BOTTOM_LEFT, 10, 10)

    switch_wifi = lv.switch(scr4)
    switch_wifi.align_to(label2, lv.ALIGN.OUT_LEFT_TOP, 290, 0)

    wifi_data = []
    
    if sta_if.active() == True:
        switch_wifi.add_state(lv.STATE.CHECKED)
        wifi_data = sta_if.scan()

    elif sta_if.active() == False:
        switch_wifi.add_state(lv.STATE.DISABLED)

    switch_wifi.add_event_cb(lambda event: switch_handler(event), lv.EVENT.ALL, None)

    wifi_list = lv.list(scr4)
    wifi_list.set_size(250, 200)
    wifi_list.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT, 0,15)
    
    for wifi in wifi_data:
            wifi_list.add_btn(lv.SYMBOL.WIFI, str(wifi[0],'utf-8'))
            current_item = wifi_list.get_child_cnt()
            wifi_item = wifi_list.get_child(current_item-1)
            wifi_item.add_event_cb(lambda task: btn_event(task, {'name':'wifi',
            'ssid':str(wifi[0],
            'utf-8')}), lv.EVENT.CLICKED, None)

    
    ta = lv.textarea(scr4)
    ta.align_to(label2, lv.ALIGN.OUT_BOTTOM_LEFT,0 , 10)
    ta.set_size(280, 50)
    ta.add_event_cb(lambda e: ta_event_cb(e,kb), lv.EVENT.ALL, None)
    ta.add_flag(lv.obj.FLAG.HIDDEN)

    kb = lv.keyboard(scr4)
    kb.align_to(ta, lv.ALIGN.OUT_BOTTOM_LEFT,-10,10)
    kb.add_flag(lv.obj.FLAG.HIDDEN)
    kb.add_event_cb(lambda e: keyboard_event(e, ta), lv.EVENT.KEY, None)




        

    



def save_to_db(trigger):
    f = open('db.txt', 'w')
    f.write(str(trigger))
    print('Save to DB : {}'.format(trigger))
    f.close()

def open_db():
    
    global trigger 

    f = open('db.txt', 'r')
    db = f.readlines()
    trigger = eval(db[0])
    f.close()
    print('Loaded from DB : {}'.format(trigger))
    
'''
display brightness

LED = 22
led = machine.Pin(LED)
led_pwm = machine.PWM(led)

led_pwm.freq(1000)    #blinking speed
led_pwm.duty(1000)  # brightness
'''

#display in active time

def led_auto_brightness():
    
    inactive_time = lv.disp_get_default().get_inactive_time()

    if inactive_time > lcd_threshold and led_pwm.duty() > 5:
        
        led_pwm.duty(led_pwm.duty()-1)

    elif inactive_time < lcd_threshold and led_pwm.duty() <1023:
        led_pwm.duty(led_pwm.duty()+3)

#Main Program

#run once
set_time(2021, 12, 5, 1, 0, 0, 0) 

try:
    open_db()
except:
    print('db not found')


gui_main()

def run_auto():

    previous_ticks = 0
    ticks_threshold = 1000
    handler_threshold = 5

    while True:

        led_auto_brightness()

        current_ticks = utime.ticks_ms()

        if current_ticks - previous_ticks > handler_threshold:
            lv.tick_inc(1)
            lv.timer_handler()
        
        if current_ticks - previous_ticks > ticks_threshold:
            #print time every 1 second
            print(str(current_time()))
            previous_ticks = current_ticks
        
        for trig in trigger:
            #run matching logic for every trigger item in trigger list
            trigger_logic(trig)
        
run_auto()