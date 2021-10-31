## Display Binance BTC price on ILI9488

from config import user, password
from espidf import VSPI_HOST
import lvgl as lv
import json
import network
import urequests
import utime

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(user, password)
while sta_if.isconnected() != True:
     print(".")
     utime.sleep(2)

'''binance api data'''
url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
data = urequests.get(url)
data_j = json.loads(data.text)

def klines_data(chart,series,interval,ymin,ymax):
    label_log.set_text('Fetching Kline Data')
    kline_url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={}&limit=20'.format(interval)
    data_klines = urequests.get(kline_url)
    data_k_j = json.loads(data_klines.text)
    label_log.set_text('Fetch Kline Successful')
    
    for i in data_k_j:
        temp = int(float((float(i[1]) + float(i[4])) / 2))
        chart.set_next_value(series, temp)
        print(temp)
        if temp > ymax or temp < ymin:
            ymin = ymin-500
            ymax = ymax+500
            label_log.set_text('Y Range Updated')
            chart.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
        label_log.set_text('Plotting ' + str(temp))
        
    label_log.set_text('Plotting Complete')
        
'''start lvgl'''
from ili9XXX import ili9488
disp = ili9488(miso=19, mosi=23, clk=18, cs=5, dc=26, rst=27, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80,spihost=VSPI_HOST, mhz=50, factor=16, hybrid=True, width=320, height=480, invert=False, double_buffer=True, half_duplex=False, initialize=True)

from xpt2046 import xpt2046
touch = xpt2046(cs=25, spihost=VSPI_HOST, mosi=-1, miso=-1, clk=-1, cal_y0 = 423, cal_y1=3948)

'''Main screen : lv.scr_act()'''
lv.scr_act().set_style_bg_color(lv.color_hex(0x000000),0)
label = lv.label(lv.scr_act())
label.set_style_text_font(lv.font_montserrat_28,0)
label.set_text("{} : {:2} ".format(data_j['symbol'], float(data_j['price'])))
label.align_to(lv.scr_act(), lv.ALIGN.TOP_MID,0,10)
label.set_style_text_color(lv.color_hex(0x00eeff),0)

label_log = lv.label(lv.scr_act())
label_log.align_to(lv.scr_act(), lv.ALIGN.BOTTOM_LEFT,0,-10)
label_log.set_text("Log")
label_log.set_style_text_color(lv.color_hex(0x1aec1a),0)

'''Chart minute : add chart'''
chart = lv.chart(lv.scr_act())
chart.set_style_bg_color(lv.color_hex(0x000000),0)
chart.set_style_line_color(lv.color_hex(0x1aec1a),0)
chart.set_style_border_color(lv.color_hex(0x1aec1a),0)
chart.set_size(220,150)
chart.align_to(label, lv.ALIGN.OUT_BOTTOM_MID,20,10)
chart.set_type(lv.chart.TYPE.LINE)
#chart.set_update_mode(lv.chart.UPDATE_MODE.CIRCULAR)
chart.set_update_mode(lv.chart.UPDATE_MODE.SHIFT)
chart.set_point_count(20)
chart.set_div_line_count(0,0)

'''Chart minute : create series'''
ser1 = chart.add_series(lv.color_hex(0x00eeff), lv.chart.AXIS.PRIMARY_Y)

'''Chart minute : calculate chart range'''
current_btc_price = int(float(data_j['price']))
upper_range = 500
lower_range = 500
ymin= round((current_btc_price-lower_range),-2)
ymax= round((current_btc_price+upper_range),-2)

print("ymin : {}".format(str(ymin)))
print("ymax : {}".format(str(ymax)))

'''Chart minute : label and ticks'''
chart.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
chart.set_axis_tick(lv.chart.AXIS.PRIMARY_Y, 10, 5, 5, 5, True, 155)

'''Chart minute : chart label'''
chart_label = lv.label(lv.scr_act())
chart_label.align_to(chart, lv.ALIGN.OUT_BOTTOM_LEFT,-50,5)
update_counter = 60
chart_label.set_text('1 minute chart : Next update {}'.format(update_counter))
chart_label.set_style_text_color(lv.color_hex(0x1aec1a),0)

'''plot series kline data'''
klines_data(chart, ser1, '1m', ymin, ymax)

'''Chart hourly : for trend'''
chart_hourly = lv.chart(lv.scr_act())
chart_hourly.set_style_bg_color(lv.color_hex(0x000000),0)
chart_hourly.set_style_line_color(lv.color_hex(0x1aec1a),0)
chart_hourly.set_style_border_color(lv.color_hex(0x1aec1a),0)
chart_hourly.set_size(220,150)
chart_hourly.align_to(chart, lv.ALIGN.OUT_BOTTOM_MID,0,30)
chart_hourly.set_type(lv.chart.TYPE.LINE)
#chart.set_update_mode(lv.chart.UPDATE_MODE.CIRCULAR)
chart_hourly.set_update_mode(lv.chart.UPDATE_MODE.SHIFT)
chart_hourly.set_point_count(20)
chart_hourly.set_div_line_count(0,0)

'''Chart_hourly : calculate chart daily range'''

'''Chart_hourly : create series'''
ser2 = chart_hourly.add_series(lv.color_hex(0x00eeff), lv.chart.AXIS.PRIMARY_Y)

'''Chart_hourly : label and ticks'''
chart_hourly.set_range(lv.chart.AXIS.PRIMARY_Y, ymin-1000, ymax+1000)
chart_hourly.set_axis_tick(lv.chart.AXIS.PRIMARY_Y, 10, 5, 5, 5, True, 155)

'''Chart hourly plot series kline data'''
klines_data(chart_hourly, ser2, '1h', ymin, ymax)

'''Chart_hourly : Label'''
chart_hourly_label = lv.label(lv.scr_act())
chart_hourly_label.align_to(chart_hourly, lv.ALIGN.OUT_BOTTOM_LEFT,-50,5)
chart_hourly_label.set_text('hourly chart')
chart_hourly_label.set_style_text_color(lv.color_hex(0x1aec1a),0)


'''loop counters'''
minute_counter = 0
current_tick = 0;
previous_tick = 0;
treshold_tick = 1000;
second_counter = 0

'''Main Loop : update chart after kline'''
while True:
    
    current_tick = utime.ticks_ms()

    '''update every 60sec'''
    if second_counter > 59 :
        second_counter = 0
        label_log.set_text("Updating Data")
        data = urequests.get(url)
        data_j = json.loads(data.text)
        current_btc_price = int(float(data_j['price']))
        
        '''adjust the chart range if value goes above and below'''
        if current_btc_price > ymax:
            ymax += 500
            chart.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
            chart_hourly.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
            label_log.set_text("Chart range updated")

            
        if current_btc_price < ymin:
            ymin -= 500
            chart.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
            chart_hourly.set_range(lv.chart.AXIS.PRIMARY_Y, ymin, ymax)
            label_log.set_text("Chart range updated")

        
        
        '''plot to chart'''
        chart.set_next_value(ser1, current_btc_price)
        label.set_text("{} : {:2} ".format(data_j['symbol'], float(data_j['price'])))
        label_log.set_text("Data Updated" + str(utime.gmtime()))
            
        '''update hourly chart'''
        if minute_counter > 59:
            label_log.set_text("Fetching new hourly Kline")
            klines_data(chart_hourly, ser2, '1h', ymin, ymax)
            minute_counter = 0
            label_log.set_text("Hourly kline updated")
    
        minute_counter += 1

    '''update every second'''
    if current_tick - previous_tick > treshold_tick:
    
        '''update minute counter'''
        if update_counter < 0 :
            update_counter = 59
        
        chart_label.set_text('1 minute chart : Next update {}'.format(update_counter))
        update_counter -= 1

        previous_tick = current_tick
        second_counter += 1
       
    

    

    






