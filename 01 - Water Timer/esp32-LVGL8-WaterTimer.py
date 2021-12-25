'''Water Timer UI'''

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

WIDTH = 320
HEIGHT_HEADER = 80

#Timer DB using -> https://github.com/sungkhum/MicroPyDatabase

import micropythondatabase as mdb

#Create/Open DB
try:
    db = mdb.Database.create("mydb")
    print('New database created')
except:
    print('Database already exist .. opening')
    db = mdb.Database.open("mydb")


'''
Table design =

"mytable": {
    "name":name,
    "hour_begin":hour,
    "minute_begin":minute_begin,
    "sec_begin":sec_begin,
    "duration": duration,
    "status":status
    }
'''    


'''Creating DB'''
#if DB not exist -> create
try:
    db_table = db.create_table("mytable",["name", "hour_begin", "minute_begin", "sec_begin", "duration", "status"])
    print('New table created')
    db_table = db.open_table("mytable")
    print('table opened')

#if DB exist -> use existing
except:
    print('table already exist .. opening')
    db_table = db.open_table("mytable")


def calculate_new_time(duration_sec, hour_begin, minute_begin, sec_begin):
    '''get duration and current time hour, minute and seconds and returns a new time tuple'''
    systemdate = utime.gmtime()
    #print(systemdate)
    temp_begin_sec = utime.mktime((systemdate[0], systemdate[1], systemdate[2], hour_begin, minute_begin, sec_begin, 0,0)) 
    #print(temp_begin_sec)
    temp_begin_sec = temp_begin_sec + duration_sec
    new_time_tuple = utime.localtime(temp_begin_sec)
    #print(new_time)
    return new_time_tuple   

def to_seconds(hour, minute, sec):
    '''change h:m:s to seconds'''
    seconds = hour * 60 * 60
    seconds += (minute * 60)
    seconds += sec
    return seconds

def compare_time(current_time_tuple, calculated_time_tuple):
    '''compare two time tuple return true or flase'''
    if current_time_tuple == calculated_time_tuple:
        boolean = True
    else:
        boolean = False  
    return boolean

def activate(db_table):
    '''function check localtime and db.time and duration, if true update --> db_table['status'] '''
    for i in range(1, db_table.current_row):
        
        data = db_table.find_row(i)
        data = data['d']
        trigger_tuple = calculate_new_time(data['duration'], data['hour_begin'], data['minute_begin'], data['sec_begin'])
                    
        #activate (if local time >= time in db)
        if (utime.localtime()[3] == data['hour_begin'] and utime.localtime()[4] == data['minute_begin'] and utime.localtime()[5] == data['sec_begin']) and data['status'] == 0:
            print('Trigger math {} : --> Activated'.format(data['name']))
            data['status'] = 1
            db_table.update_row(i, data)
        
        #deactivate (if local time == stop time in db)
        if (utime.localtime()[3] == trigger_tuple[3] and utime.localtime()[4] == trigger_tuple[4] and utime.localtime()[5] == trigger_tuple[5]) and data['status'] == 1:                    
            print('Trigger match {}: --> Dectivated'.format(data['name']))
            data['status'] = 0
            db_table.update_row(i, data)
            
                
'''Draw main Screen'''

scr = lv.scr_act()
scr.set_style_bg_color(lv.color_hex(0x95A5A6),0)
lv.scr_load(scr)

header = lv.obj(scr)
header.clear_flag(lv.obj.FLAG.SCROLLABLE)
header.set_size(WIDTH-20, 50)
header.align_to(scr, lv.ALIGN.TOP_MID,0,10)
header.set_style_radius(lv.STATE.DEFAULT, 0)
header.set_style_bg_color(lv.color_hex(0x34495E),0)
#header.set_style_bg_grad_color(lv.color_hex(0xffffff),0)
#header.set_style_bg_grad_dir(lv.GRAD_DIR.VER,lv.PART.MAIN)
header.set_style_border_color(lv.color_hex(0x34495E),0)

label = lv.label(header)
label.set_style_text_color(lv.color_hex(0xffffff),0)

def gui_refresh_date():
    label.set_text('{}/{}/{}   {:02}:{:02}:{:02}'.format(utime.localtime()[2], utime.localtime()[1], utime.localtime()[0], utime.localtime()[3], utime.localtime()[4],utime.localtime()[5]))

lv.timer_create(lambda task: gui_refresh_date(), 800, None)
label.set_style_text_font(lv.font_montserrat_28,0)
label.center()

def draw_part_event_cb(e):
    objc = e.get_code()
    objt = e.get_target()
    dsc = lv.obj_draw_part_dsc_t.__cast__(e.get_param())

    s_row = lv.point_t()
    s_col = lv.point_t()
    
    if objc == lv.EVENT.PRESSING:
        '''only in effect if cell is pressed'''
        objt.get_selected_cell(s_row, s_col)
        print("selected row:{}, col:{}".format(s_row.x, s_col.x))

    if objc == lv.EVENT.DRAW_PART_BEGIN:
        '''only change when draw part begins'''
        
        if dsc.part == lv.PART.ITEMS:
            
            #print('true!')
            row = dsc.id // objt.get_col_cnt()
            col = dsc.id - row * objt.get_col_cnt()
            #print("row : {}, column : {} ".format(row,col))
            
            if row == 0:
                #change header style
                dsc.label_dsc.align = lv.TEXT_ALIGN.CENTER
                dsc.label_dsc.color = lv.color_hex(0xffffff)
                dsc.rect_dsc.bg_color = lv.color_hex(0x6b765b)
                
            if row > 0 and col > 0:
                #center colum 1 and 2
                dsc.label_dsc.align = lv.TEXT_ALIGN.CENTER                
        
table = lv.table(scr)
table.set_size(300, 250)
table.set_cell_value(0,0, "Name")
table.set_cell_value(0,1, "Begin Time")
table.set_cell_value(0,2, "Dur")
#table column width
table.set_col_width(0, 110)
table.set_col_width(1, 100)
table.set_col_width(2, 90)
table.align_to(header, lv.ALIGN.OUT_BOTTOM_MID,0,10)
table.add_event_cb(draw_part_event_cb, lv.EVENT.ALL, None)

#populate the table from db_table
for i in range(1,db_table.current_row):
    data = db_table.find_row(i)['d']
    table.set_cell_value(i,0, data["name"])
    table.set_cell_value(i,1, '{}:{}:{}'.format(str(data['hour_begin']),str(data['minute_begin']), str(data['sec_begin'])))
    table.set_cell_value(i,2, '{}'.format(str(data['duration'])))

    
btn = lv.btn(scr)
btn.align_to(table, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
btn.set_style_bg_color(lv.color_hex(0x745b76),0)
btn_lbl = lv.label(btn)
btn_lbl.set_text('Add')
btn_lbl.set_style_text_font(lv.font_montserrat_28,0)

while True:
    activate(db_table)