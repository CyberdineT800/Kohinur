from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data.text_values import *

def create_btn_with_back (text):
    keyboard=ReplyKeyboardMarkup(

        keyboard=[
            [
                KeyboardButton(text=text),
            ],
            [
                KeyboardButton(text=BACK),
            ],

        ],
        resize_keyboard=True,
    )
    
    return keyboard


back_btn=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=BACK),
        ],
    ],
    resize_keyboard=True,
)


end_testing_btn=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=TEST_END_REQUEST),
        ],
    ],
    resize_keyboard=True,
)


teacher_add_group_btn=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=TEACHER_ADD_NEW_GROUP),
        ],
    ],
    resize_keyboard=True,
)


teacher_group_menu_btns=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=TEACHER_GROUP_ATTENDANCE),
            KeyboardButton(text=TEACHER_GROUP_TESTS),
        ],
        [
            KeyboardButton(text=BACK),
        ],
    ],
    resize_keyboard=True,
)


admin_main_menu_btns=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=GROUPS),
            #KeyboardButton(text=STATISTICS),
        ],
    ],
    resize_keyboard=True,
)


admin_group_menu_btns=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=PAYMENT),
            KeyboardButton(text=STATISTICS),
        ],
        [
            KeyboardButton(text=BACK),
        ],
    ],
    resize_keyboard=True,
)


start_menu_btns=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=STUDENT),
            KeyboardButton(text=TEACHER),
        ],
        [
            KeyboardButton(text=TESTS),
        ],
    ],
    resize_keyboard=True,
)


phone_and_back_btn=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=SEND_CONTACT, request_contact=True),
        ],
        [
            KeyboardButton(text=BACK),
        ],
    ],
    resize_keyboard=True,
)



