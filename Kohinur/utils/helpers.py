import json
import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, reply_keyboard_markup

from data.text_values import TESTS_READY_ERROR


def open_json_file(f_name):
    try:
        with open(f_name, 'rb') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        with open(f_name) as f:
            f.write({"{}"})
        return {}
    except:
        return []
    

def open_txt_file(f_name):
    res = []
    with open (f_name, "r") as file:
        while True:
            line = file.readline()
            if line.strip() == "":
                break
            res.append(line.strip())
       
    return res



async def create_questions(bot, chat_id, questions, count):
    if count > len(questions):
        raise ValueError(TESTS_READY_ERROR)

    random.shuffle(questions)

    selected_questions = questions[:count]

    msg_ids = {}
    j = 1

    for question in selected_questions:
        answers = question['answers']
        if isinstance(answers, str):
            answers = json.loads(answers)

        n = len(answers)
        answer_txt = ""
        
        inline_keyboard = []
        row = []

        for i in range(n):
            answer_txt += f"{chr(i + 65)}) {answers[i]}\n"
            row.append(InlineKeyboardButton(text=str(chr(i + 65)), callback_data=f"answer_{question['id']}_{i}"))

        inline_keyboard.append(row)
        answer_btns = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
        if question['questionphotoid']:
            message = await bot.send_photo(
                chat_id=chat_id, 
                photo=question['questionphotoid'], 
                caption=f"<blockquote>{j}) {question['questiontxt']}</blockquote>" + "\n\n" + answer_txt,
                reply_markup=answer_btns
            )
        else:
            message = await bot.send_message(
                chat_id=chat_id,
                text=f"<blockquote>{j}) {question['questiontxt']}</blockquote>" + "\n\n" + answer_txt,
                reply_markup=answer_btns
            )

        msg_ids[message.message_id] = question
        j += 1

    return msg_ids



def is_contact(contact):
    if contact.startswith('+'):
        contact = contact[1:]
    if contact.startswith('998'):
        contact = contact[3:]
    if len(contact)!=9:
        return False
    try:
        contact = int(contact)
        return True
    except:
        return False
    


def string_to_weekday(string):
    string = string.lower()
    
    if 'du' in string:
        return 'Dushanba'
    elif 'se' in string:
        return 'Seshanba'
    elif 'chor' in string:
        return 'Chorshanba'
    elif 'pay' in string:
        return 'Payshanba'
    elif 'ju' in string:
        return 'Juma'
    elif 'shan' in string:
        return 'Shanba'
    else:
        return 'Yakshanba'


def give_all_weekdays(days):
    days = days.replace(' ', '').split(',')
    res = []
    
    for day in days:
        res.append(string_to_weekday(day))
        
    return ", ".join(res)


async def create_group_info (group, group_students_count, index = -1):
    if index != -1:
        res = f"<blockquote>{index}) Guruh nomi: {group['group_name']}</blockquote>"
    else:
        res = f"<blockquote> Guruh nomi: {group['group_name']}</blockquote>"
        
    res += f"     O'qituvchi: {group['group_teacher_fullname']}\n"
    res += f"     Talabalar soni: {group_students_count}\n"
    res += f"     Dars kunlari: {give_all_weekdays(group['group_days'])}\n"
    res += f"     Dars vaqtlari: {group['group_times'].replace(',', ', ')}\t"
    res += f"   (dars vaqtlari kunlarga mos ravishda berilgan)"
    
    return res


async def create_all_groups_info(groups, student_counts, page=0, items_per_page=5):
    res = ""
    n = len(groups)
    start = page * items_per_page
    end = start + items_per_page
    
    for i in range(start, min(end, n)):
        res += await create_group_info(groups[i], student_counts[i], i + 1)
        res += '\n\n\n'
        
    return res


async def create_payment_info(datas):
    res = "<blockquote>To'lov haqida ma'lumot</blockquote>\n\n"
    res += f"  O'quvchi: {datas['student_fullname']}\n"
    res += f"  Guruh: {datas['student_group_name']}\n"
    res += f"  Fan: {datas['student_subject_name']}\n"
    res += f"  Miqdor: {datas['payment_amount']}\n"
    res += f"  Sana: {datas['payment_last_date']}\n\n"
    res += "#tulov"
        
    return res


async def create_attendance_info(datas):
    res = "<blockquote>Davomat haqida ma'lumot</blockquote>\n\n"
    res += f"  O'quvchi: {datas['student_fullname']}\n"
    res += f"  Guruh: {datas['student_group_name']}\n"
    res += f"  Fan: {datas['student_subject_name']}\n"
    res += f"  Status: {datas['attendance_status']}\n"
    res += f"  Sana: {datas['attendance_date']}\n\n"
    res += "#davomat"
        
    return res
