import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

from fsm import TocMachine
from utils import send_text_message, send_carousel_message, send_button_message, send_image_message

load_dotenv()

machine = TocMachine(
    states=["user", "main_menu", "about_angus", "show_location", "show_lesson_introduce", "show_angus_info", "show_timetable", "iwant_check_CB_level", "iwant_check_CB_search", "iwant_hand_in_HW_type", 'iwant_hand_in_HW_name', 'iwant_hand_in_HW_locateDB', 'iwant_hand_in_HW_image', 'iwant_order_dayname', 'iwant_order_meal', 'iwant_order_cost'],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "about_angus",
            "conditions": "is_going_to_about_angus",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "iwant_hand_in_HW_type",
            "conditions": "is_going_to_iwant_hand_in_HW_type",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "iwant_order_dayname",
            "conditions": "is_going_to_iwant_order_dayname",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "iwant_check_CB_level",
            "conditions": "is_going_to_iwant_check_CB_level",
        },
        {
            "trigger": "advance",
            "source": "iwant_check_CB_level",
            "dest": "iwant_check_CB_search",
            "conditions": "is_going_to_iwant_check_CB_search",
        },
        {
            "trigger": "advance",
            "source": "about_angus",
            "dest": "show_location",
            "conditions": "is_going_to_show_location",
        },
        {
            "trigger": "advance",
            "source": "about_angus",
            "dest": "show_timetable",
            "conditions": "is_going_to_show_timetable",
        },
        {
            "trigger": "advance",
            "source": "about_angus",
            "dest": "show_lesson_introduce",
            "conditions": "is_going_to_show_lesson_introduce",
        },
        {
            "trigger": "advance",
            "source": "about_angus",
            "dest": "show_angus_info",
            "conditions": "is_going_to_show_angus_info",
        },
        {
            "trigger": "advance",
            "source": "show_location",
            "dest": "about_angus",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "show_lesson_introduce",
            "dest": "about_angus",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "show_timetable",
            "dest": "about_angus",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "show_angus_info",
            "dest": "about_angus",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "about_angus",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "iwant_check_CB_search",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "iwant_hand_in_HW_type",
            "dest": "iwant_hand_in_HW_name",
            "conditions": "is_going_to_iwant_hand_in_HW_name",
        },
        {
            "trigger": "advance",
            "source": "iwant_hand_in_HW_name",
            "dest": "iwant_hand_in_HW_locateDB",
            "conditions": "is_going_to_iwant_hand_in_HW_locateDB",
        },
        {
            "trigger": "advance",
            "source": "iwant_hand_in_HW_locateDB",
            "dest": "iwant_hand_in_HW_image",
            "conditions": "is_going_to_iwant_hand_in_HW_image",
        },
        {
            "trigger": "advance",
            "source": "iwant_order_dayname",
            "dest": "iwant_order_meal",
            "conditions": "is_going_to_iwant_order_meal",
        },
        {
            "trigger": "advance",
            "source": "iwant_order_meal",
            "dest": "iwant_order_cost",
            "conditions": "is_going_to_iwant_order_cost",
        },
        {
            "trigger": "advance",
            "source": "iwant_order_cost",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "iwant_hand_in_HW_image",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {"trigger": "go_back", "source": ["about_angus"], "dest": "user"}
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "請按指示操作，謝謝！")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")

if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
