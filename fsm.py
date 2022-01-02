from datetime import date
from transitions.extensions import GraphMachine

from utils import locate_HW_book, order_cost, send_text_message, send_carousel_message, send_button_message, send_image_message, search_contact_book, write_HW_book

import message_interface
import os
import time

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, LocationSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text == "menu"

    def is_going_to_about_angus(self, event):
        text = event.message.text
        return text == "認識黃杰"

    def is_going_to_show_location(self, event):
        text = event.message.text
        return text == "補習班位置"

    def is_going_to_show_lesson_introduce(self, event):
        text = event.message.text
        return text == "課程介紹"

    def is_going_to_show_angus_info(self, event):
        text = event.message.text
        return text == "黃杰的聯絡資訊"

    def is_going_to_show_timetable(self, event):
        text = event.message.text
        return text == "本學期課表"

    def is_going_to_iwant_order_dayname(self, event):
        text = event.message.text
        return text == "我要訂餐"
    
    def is_going_to_iwant_check_CB_level(self, event):
        text = event.message.text
        return text == "我要找聯絡簿"
    
    def is_going_to_iwant_check_CB_search(self, event):
        global level
        level = event.message.text
        return level == "小五" or level == "小六" or level == "國一" or level == "國二" or level == "國三" or level == "高一" or level == "高二" or level == "高三"

    def is_going_to_iwant_hand_in_HW_type(self, event):
        text = event.message.text
        return text == "我要交作業"

    def is_going_to_iwant_hand_in_HW_name(self, event):
        text = event.message.text
        HW_type = ['英檢初級初試', '英檢初級複試', '英檢中級初試', '英檢中級複試', '英檢中高級初試', '英檢中高級複試', '多益', '國中部寫作', '高一寫作', '高二寫作', '高三寫作']
        global HW_name
        if text in HW_type:
            HW_name = text
        return text in HW_type
    
    def is_going_to_iwant_hand_in_HW_locateDB(self, event):
        text = event.message.text
        global std_name
        std_name = text
        return len(text) > 0

    def is_going_to_iwant_hand_in_HW_image(self, event):
        # if event.message.type == 'image':
        #     sendimage = line_bot_api.get_message_content(event.message.id)
        #     path = './image (from student)/' + event.message.id + '.png'
        #     with open(path, 'wb') as fd:
        #         for chenk in sendimage.iter_content():
        #             fd.write(chenk)
        #     return True

        text = event.message.text
        global HW_content
        HW_content = text
        return len(text) > 0

    def is_going_to_iwant_order_meal(self, event):
        text = event.message.text
        global tdate
        global day
        global order_name
        order = []
        order = text.split(' ')
        tdate = order[0]
        day = order[1]
        order_name = order[2]
        return len(text) > 0

    def is_going_to_iwant_order_cost(self, event):
        text = event.message.text
        global meal
        global cost
        order = []
        order = text.split(' ')
        meal = order[0]
        cost = order[1]
        return len(text) > 0

    def on_enter_main_menu(self, event):
        print("entering main menu")
        reply_token = event.reply_token
        message = message_interface.main_menu
        message_to_reply = FlexSendMessage("main_menu", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        #self.go_back()

    def on_enter_about_angus(self, event):
        print("entering about_angus")
        reply_token = event.reply_token
        message = message_interface.about_angus
        message_to_reply = FlexSendMessage("關於黃杰", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        #self.go_back()

    def on_enter_show_location(self, event):
        print("entering show_location")
        reply_token = event.reply_token
        line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        message = LocationSendMessage(
            title = "黃杰英語的位置",
            address = "桃園市蘆竹區吉林路28號2F", 
            latitude = 25.050661,
            longitude = 121.296944,
        )
        line_bot_api.reply_message(reply_token, message)
        #self.go_back_about_angus()

    def on_enter_show_lesson_introduce(self, event):
        print("entering show_lesson_introduce")
        reply_token = event.reply_token
        message = message_interface.lesson_introduce
        message_to_reply = FlexSendMessage("lesson introduce", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        #self.go_back_about_angus()

    def on_enter_show_angus_info(self, event):
        print("entering show_angus_info")
        reply_token = event.reply_token
        message = message_interface.angus_info
        message_to_reply = FlexSendMessage("angus info", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        #self.go_back_about_angus()

    def on_enter_show_timetable(self, event):
        print("entering show_timetable")
        reply_token = event.reply_token
        message = message_interface.timetable
        message_to_reply = FlexSendMessage("timetable", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        #self.go_back_about_angus()

    def on_enter_iwant_check_CB_level(self, event):
        print("entering iwant_check_CB_level")
        content = ""
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入年級")

    def on_enter_iwant_check_CB_search(self, event):
        print("entering iwant_check_CB_search")
        content = search_contact_book(level)
        reply_token = event.reply_token
        message_to_reply = TemplateSendMessage(
                            alt_text = 'Buttons template',
                            template = ButtonsTemplate(
                                title = "本週的聯絡簿",
                                text = content,
                                actions = [
                                    MessageTemplateAction(
                                        label = "返回主選單",
                                        text = "menu"
                                    )
                                ]
                            )
                        )
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_iwant_hand_in_HW_type(self, event):
        print("entering iwant_hand_in_HW_type")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入作業類別\n若不請楚請移至表單參考下方項目")

    def on_enter_iwant_hand_in_HW_name(self, event):
        print("entering iwant_hand_in_HW_type")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入學生姓名")

    def on_enter_iwant_hand_in_HW_locateDB(self, event):
        print("entering iwant_hand_in_HW_locateDB")
        reply_token = event.reply_token
        global DB_location
        DB_location = locate_HW_book(HW_name, std_name)
        if DB_location > 0:
            send_text_message(reply_token, "請開始繳交")
        elif DB_location == -1:
            send_text_message(reply_token, "你並沒有被派發作業\n若有問題請詢問黃杰")

    def on_enter_iwant_hand_in_HW_image(self, event):
        print("entering iwant_hand_in_HW_image")
        write_HW_book(HW_name, HW_content, DB_location)
        reply_token = event.reply_token
        send_text_message(reply_token, "雲端寫入完畢，請輸入menu回到主頁！")
        # line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        # time.sleep(5)
        # if event.message.type == 'image':
        #     sendimage = LineBotApi.get_message_content(event.message.id)
        #     path = './image (from student)/' + event.message.id + '.png'
        #     with open(path, 'wb') as fd:
        #         for chenk in sendimage.iter_content():
        #             fd.write(chenk)
        # else:
        #     print('qq')

    def on_enter_iwant_order_dayname(self, event):
        print("entering iwant_order_dayname")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入今天日期、星期和你的姓名\nex: 12/25 星期六 聖誕老公公")

    def on_enter_iwant_order_meal(self, event):
        print("entering iwant_order_meal")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入餐點和價錢\nex: 排骨飯 70")

    def on_enter_iwant_order_cost(self, event):
        print("entering iwant_order_cost")
        j = 1
        j = order_cost(day, tdate, order_name, meal, cost)
        reply_token = event.reply_token
        if j == 1:
            send_text_message(reply_token, "點餐與扣款成功！\n輸入menu即可回到主頁面")
        elif j == -1:
            send_text_message(reply_token, "系統內沒有你的資料，或是上面輸入格式有誤，請重新確認！\n輸入menu即可回到主頁面")