import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, LocationSendMessage, ImageSendMessage

import pygsheets
import gspread

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"

def send_carousel_message(reply_token, col):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text = 'Carousel template',
        template = ImageCarouselTemplate(columns = col)
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_button_message(reply_token, title, text, btn, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='button template',
        template = ButtonsTemplate(
            title = title,
            text = text,
            thumbnail_image_url = url,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url,
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def search_contact_book(level):
    gc = pygsheets.authorize(service_file='./.secret/angus-english-contactbook-c6fea4c17668.json')
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/11MhNivSD54pAMKyBoM9RpoRTBhjwuxqg9PAcD09YPsE/edit#gid=0")
    ws = sheet.worksheet_by_title("聯絡簿")

    content = ""
    if level == "小五":
        content = ws.get_value("B2")
    elif level == "小六":
        content = ws.get_value("B3")
    elif level == "國一":
        content = ws.get_value('B4')
    elif level == "國二":
        content = ws.get_value("B5")
    elif level == "國三":
        content = ws.get_value("B6")
    elif level == "高一":
        content = ws.get_value("B7")
    elif level == "高二":
        content = ws.get_value("B8")
    elif level == "高三":
        content = ws.get_value("B9")
    else:
        content = "年級有誤"
    
    return content

def locate_HW_book(HW, student):
    gc = pygsheets.authorize(service_file='./.secret/angus-english-contactbook-HW-2dc8394de662.json')
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1yOZv8p4yUdmU64UmsTnMs2BFbzh46NjcNpG2Dei5Gwg/edit?usp=sharing")
    ws = sheet.worksheet_by_title(HW)

    for i in range(1,500):
        index = 'A'+str(i)
        name = ws.get_value(index)
        if name == student:
            return i 
    return -1

def write_HW_book(HW, content, index):
    gc = pygsheets.authorize(service_file='./.secret/angus-english-contactbook-HW-2dc8394de662.json')
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1yOZv8p4yUdmU64UmsTnMs2BFbzh46NjcNpG2Dei5Gwg/edit?usp=sharing")
    ws = sheet.worksheet_by_title(HW)

    col = 'D'+str(index)
    ws.update_value(col, content)


def order_cost(day, date, name, meal, pay):
    gc = pygsheets.authorize(service_file='./.secret/angus-english-contactbook-order_book-6e6eba419b4f.json')
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1xHHJUl6clGIdbTNudJaYt4k6vmyYSW8wmKYG_BUQTP4/edit?usp=sharing")
    ws = sheet.worksheet_by_title(day)
    j = 1
    index_dict = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    for i_name in range(1,50):
        index = 'A'+str(i_name)
        student = ws.get_value(index)
        if student == name:
            j = 1
            break
        else:
            j = -1
    if j == -1:
        return -1

    for i_date in index_dict:
        col = i_date+'1'
        sheet_date = ws.get_value(col)
        if sheet_date == date:
            j = 1
            break
        else:
            j = -1
    if j == -1:
        return -1

    if j == 1:
        ws.update_value(i_date+str(i_name), str(pay))
        ws.update_value(i_date+str(i_name+20), str(meal))
        return 1
