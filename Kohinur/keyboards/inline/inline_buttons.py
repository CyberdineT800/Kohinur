from datetime import datetime, date, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.text_values import CANCEL, NEXT_PAGE, NO_TEXT, PREV_PAGE, SOMETHING, SPLITTER, STUDENT_ATTENDANCE_EXIST_STATUS, STUDENT_GROUPS, TEACHER_GROUPS, TEACHER_SUBJECTS, TEACHER_TESTS, CONFIRM, PAID, UNPAID, YES_TEXT


def subject_btns(subjects):
    inline_keyboard = []
    n = len(subjects)

    for i in range(0, n, 2):
        row = []
        row.append(InlineKeyboardButton(text=subjects[i]['subjectname'], callback_data=f"subject_{subjects[i]['id']}"))
        
        if i + 1 < n:
            row.append(InlineKeyboardButton(text=subjects[i + 1]['subjectname'], callback_data=f"subject_{subjects[i + 1]['id']}"))
        
        inline_keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_accepting_btns (call_data):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=YES_TEXT, callback_data=f'accept_{call_data}'),
            InlineKeyboardButton(text=NO_TEXT, callback_data=f'not_accept_{call_data}'),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_test_accepting_btns (student_id, teacher_chat_id, stat_id):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=YES_TEXT, callback_data=f'test_confirm_{student_id}_{teacher_chat_id}_{stat_id}'),
            InlineKeyboardButton(text=NO_TEXT, callback_data=f'test_not_confirm_{student_id}_{teacher_chat_id}_{stat_id}'),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_teacher_menu_btns (teacher_id):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=TEACHER_TESTS, callback_data=f'teacher_tests_{teacher_id}'),
            InlineKeyboardButton(text=TEACHER_GROUPS, callback_data=f'teacher_groups_{teacher_id}'),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_student_menu_btns (student_id):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=STUDENT_GROUPS, callback_data=f'select_student_groups_{student_id}'),
            InlineKeyboardButton(text=SOMETHING, callback_data=f'select_student_groups_{student_id}'),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_select_group_btns(groups, page=0, items_per_page=5):
    inline_keyboard = []
    n = len(groups)
    start = page * items_per_page
    end = start + items_per_page

    row = []
    for i in range(start, min(end, n)):
        row.append(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"user_select_group_{groups[i]['group_id']}"))
    
    inline_keyboard.append(row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text=PREV_PAGE, callback_data=f"groups_page_{page - 1}"))
    if end < n:
        nav_row.append(InlineKeyboardButton(text=NEXT_PAGE, callback_data=f"groups_page_{page + 1}"))
    
    if nav_row:
        inline_keyboard.append(nav_row)
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_attendance_group_students_btns(group_attendance):    
    inline_keyboard = []
    student_ids = group_attendance.keys()
    i = 1
    
    for student_id in student_ids:        
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{i}) {group_attendance[student_id]['student_fullname']} {group_attendance[student_id]['status']}",
                    callback_data=f"student_attendance_{student_id}_{group_attendance[student_id]['status']}"
            )])

        i += 1
        
        
    inline_keyboard.append([InlineKeyboardButton(
        text=CONFIRM,
        callback_data="attendance_confirm"
    )])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def create_attendance_group_payments_btns(group_payments):    
    inline_keyboard = []
    student_ids = group_payments.keys()
    i = 1
    
    for student_id in student_ids:        
        row = []
        
        row.append(InlineKeyboardButton(
                       text=f"↓ {i}) {group_payments[student_id]['student_fullname']} ↓",
                       callback_data="payment"))
                
        inline_keyboard.append(row)
        row = []   

        row.append(InlineKeyboardButton(
                       text="-10",
                       callback_data=f"student_payment_minus_{student_id}"))

        row.append(InlineKeyboardButton(
                       text=str(group_payments[student_id]['amount']),
                       callback_data="payment"))

        row.append(InlineKeyboardButton(
                       text="+10",
                       callback_data=f"student_payment_plus_{student_id}"))
        
        inline_keyboard.append(row)
        row = []

        row.append(InlineKeyboardButton(
                       text=str(group_payments[student_id]['payment_last_date']),
                       callback_data="payment"))

        last_payment = group_payments[student_id]['payment_last_date']
        today = date.today()
        
        if last_payment.month == today.month:
            row.append(InlineKeyboardButton(
                           text=UNPAID,
                           callback_data=f"student_payment_update_{student_id}"))
        else:
            row.append(InlineKeyboardButton(
                           text=PAID,
                           callback_data=f"student_payment_update_{student_id}"))
            

        inline_keyboard.append(row)

        # inline_keyboard.append([InlineKeyboardButton(
        #             text=SPLITTER,
        #             callback_data="payment")])

        i += 1
        
        
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text=CANCEL,
                callback_data="payments_cancel"),
                
            InlineKeyboardButton(
                text=CONFIRM,
                callback_data="payments_confirm"),
        ])
    

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_day_btns(selected_days):
    inline_keyboard = []
    row = []
    i = 0
    added = False
    
    for day, selected in selected_days.items():
        status = "✅" if selected else "❌"
        
        row.append(InlineKeyboardButton(text=f"{day} {status}", callback_data=f"days_{day}"))
        
        if i >= 3 and not added:
            inline_keyboard.append(row)
            row = []
            added = True

        i += 1

    inline_keyboard.append(row)
    inline_keyboard.append([InlineKeyboardButton(text=CONFIRM, callback_data="days_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def create_day_time_btns(selected_days, selected_times):
    inline_keyboard = []
    
    for day, selected in selected_days.items():
        if selected:
            row = []
            time = selected_times[day]
            row.append(InlineKeyboardButton(text=f"{day} -> {time:02d}:00", callback_data=f"times_{day}"))
            row.append(InlineKeyboardButton(text="🔽", callback_data=f"times_{day}_decrease"))
            row.append(InlineKeyboardButton(text="🔼", callback_data=f"times_{day}_increase"))
            inline_keyboard.append(row)
            
    inline_keyboard.append([InlineKeyboardButton(text=CONFIRM, callback_data="times_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



inline_keyboard = [
    [
        InlineKeyboardButton(text="-5", callback_data='test_count_remove'),
        InlineKeyboardButton(text="+5", callback_data='test_count_add'),
    ],
    [
        InlineKeyboardButton(text=CONFIRM, callback_data='test_count_confirm'),
    ],
]

test_count_btns = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


