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

numbers = [1,2,3,4,5,6,7,8,9,10,11,12]

'''Generate Question'''
class question:

        def __init__(self):

                temp1 = 0
                temp2 = 0

                '''generate question'''
                while temp1 not in numbers:
                        temp1 = urandom.randrange(1,12)
                
                while temp2 not in numbers:
                        temp2 = urandom.randrange(1,12)

                self.question1 = temp1
                self.question2 = temp2

                '''generate answer'''
                
                #real answer
                self.answer_real = temp1 * temp2

                #anwer_2 
                temp = 0

                while temp == 0 or temp == self.answer_real:
                        temp = urandom.randrange(1,12) * urandom.randrange(1,12)

                self.answer_2 = temp

                #answer_3

                temp = 0
                
                while temp == 0 or temp == self.answer_2 or temp == self.answer_real :
                        temp = urandom.randrange(1,12) * urandom.randrange(1,12)

                self.answer_3 = temp

                #answer_4

                temp = 0
                
                while temp == 0 or temp == self.answer_3 or temp == self.answer_2 or temp == self.answer_real :
                        temp = urandom.randrange(1,12) * urandom.randrange(1,12)

                self.answer_4 = temp
                
                print("q1 : {}".format(self.question1))
                print("q2 : {}".format(self.question2))
                print("ar : {}".format(self.answer_real))
                print("a2 : {}".format(self.answer_2))
                print("a3 : {}".format(self.answer_3))
                print("a4 : {}".format(self.answer_4))

                self.list = [self.answer_real, self.answer_2, self.answer_3, self.answer_4]
                self.randomlist = []
                
                while len(self.randomlist) != 4:
                        temp = urandom.choice(self.list)
                        if temp not in self.randomlist:
                                self.randomlist.append(temp)
                
                print(self.randomlist)
                        
                
'''GUI : Button Events'''

def button_event(obj, question, answer):

        #check answer
        print("real answer : " + str(question.answer_real))
        print("given answer :" + str(answer.get_text()))
        #if correct -> animate -> wait
        answer_int = int(answer.get_text())
        if answer_int == question.answer_real:
                answer.set_text(lv.SYMBOL.RIGHT)
                obj.set_style_bg_color(lv.color_hex(0x0ed145),0)
                print('Correct Answer')
                print(answer)
                
        if answer_int != question.answer_real:
                answer.set_text(lv.SYMBOL.CLOSE)
                obj.set_style_bg_color(lv.color_hex(0xfa3636),0)
                print('Incorrect Answer')
                 
        #if wrong -> animate -> wait
        #reset question
        reset_question()

'''GUI : Main Display'''

q = question()

scr = lv.scr_act()
label = lv.label(scr)
label.set_style_text_font(lv.font_montserrat_28,0)
label.set_text('Math Exercise')
label.align_to(scr, lv.ALIGN.TOP_MID,0,10)

question_label = lv.label(scr)
question_label.set_text('Answer as quickly as you can')
question_label.align_to(label, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)

the_question_btn = lv.btn(scr)
the_question_btn.set_size(250,50)

the_question_label = lv.label(the_question_btn)

the_question = '{} x {}'.format(q.question1, q.question2)
the_question_label.set_text(the_question)
the_question_label.set_style_text_font(lv.font_montserrat_28,0)
the_question_label.center()

the_question_btn.align_to(question_label, lv.ALIGN.OUT_BOTTOM_MID,0,10)

pick_answer_label = lv.label(scr)
pick_answer_label.set_text('Pick your answer')
pick_answer_label.align_to(the_question_btn, lv.ALIGN.OUT_BOTTOM_MID,0,30)

answer1_btn = lv.btn(scr)
answer1_btn.set_size(125,80)
answer1_btn.align_to(pick_answer_label, lv.ALIGN.OUT_BOTTOM_LEFT,70,10)
answer1_btn.add_event_cb(lambda e:button_event(answer1_btn, q, answer1_label), lv.EVENT.CLICKED, None)
answer1_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
answer1_label = lv.label(answer1_btn)
answer1_label.set_style_text_font(lv.font_montserrat_28,0)
answer1_label.set_text(str(q.randomlist[0]))
answer1_label.center()


answer2_btn = lv.btn(scr)
answer2_btn.set_size(125,80)
answer2_btn.align_to(pick_answer_label, lv.ALIGN.OUT_BOTTOM_LEFT,-70,10)
answer2_btn.add_event_cb(lambda e:button_event(answer2_btn, q, answer2_label), lv.EVENT.CLICKED, None)
answer2_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
answer2_label = lv.label(answer2_btn)
answer2_label.set_style_text_font(lv.font_montserrat_28,0)
answer2_label.set_text(str(q.randomlist[1]))
answer2_label.center()

answer3_btn = lv.btn(scr)
answer3_btn.set_size(125,80)
answer3_btn.align_to(answer1_btn, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
answer3_btn.add_event_cb(lambda e:button_event(answer3_btn, q, answer3_label), lv.EVENT.CLICKED, None)
answer3_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
answer3_label = lv.label(answer3_btn)
answer3_label.set_style_text_font(lv.font_montserrat_28,0)
answer3_label.set_text(str(q.randomlist[2]))
answer3_label.center()

answer4_btn = lv.btn(scr)
answer4_btn.set_size(125,80)
answer4_btn.align_to(answer2_btn, lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
answer4_btn.add_event_cb(lambda e:button_event(answer4_btn, q, answer4_label), lv.EVENT.CLICKED, None)
answer4_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
answer4_label = lv.label(answer4_btn)
answer4_label.set_style_text_font(lv.font_montserrat_28,0)
answer4_label.set_text(str(q.randomlist[3]))
answer4_label.center()

def reset_question():

        global q
        
        q = question()

        the_question = '{} x {}'.format(q.question1, q.question2)
        the_question_label.set_text(the_question)       
        answer1_label.set_text(str(q.randomlist[0]))
        answer2_label.set_text(str(q.randomlist[1]))
        answer3_label.set_text(str(q.randomlist[2]))
        answer4_label.set_text(str(q.randomlist[3]))
        '''
        answer1_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
        answer2_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
        answer3_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
        answer4_btn.set_style_bg_color(lv.color_hex(0x3653fa),0)
        '''








                

                
                






