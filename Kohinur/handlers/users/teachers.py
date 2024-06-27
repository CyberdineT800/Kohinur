import logging
from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta
from aiogram.fsm.storage.base import StorageKey
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *

from loader import teachers, attendance, payments, statistics, tests, students, groups, subjects, bot, ADMINS, dispatcher
from keyboards.reply.default_buttons import*
from keyboards.inline.inline_buttons import*
from states.Start_states import StartStates
from states.Teacher_states import TeacherStates
from utils.helpers import create_all_groups_info, create_group_info, create_questions, is_contact, open_json_file


router = Router()


##########################################################################

#            N E W    T E A C H E R   R E G I S T R A T I O N            #
 
##########################################################################


@router.message(TeacherStates.fullname, F.text)
async def teacher_fullname_ask(message: types.Message, state: FSMContext):
    fullname = message.text.replace(TELEGRAM_NAME_SUFFIX, '')
    
    await state.update_data({'teacher_fullname': fullname})
    await state.set_state(TeacherStates.subject)

    await message.answer(fullname +'\n' + ACCEPTED, reply_markup=back_btn)
    await message.answer(TEACHER_SUBJECT_ASK)
    
    all_subjects = await subjects.select_all_subjects()

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
    


@router.message(TeacherStates.subject, F.text==BACK)
async def back_fullname_ask(message: types.Message, state: FSMContext):
    await message.answer(TEACHER_FULLNAME, reply_markup=create_btn_with_back(message.from_user.full_name+TELEGRAM_NAME_SUFFIX))
    await state.set_state(TeacherStates.fullname);
    

@router.callback_query(TeacherStates.subject, F.data.startswith('subject_'))
async def teacher_subject_ask_btn(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.replace('subject_', ''))
    subject = await subjects.select_subject(id=subject_id)
    
    await callback.message.answer(subject['subjectname'] + '\n' + ACCEPTED)
    await callback.message.answer(TEACHER_PHONE_ASK, reply_markup=phone_and_back_btn)
    
    await state.update_data({'teacher_subject': subject['subjectname'],
                             'teacher_subject_id': subject_id})
    await state.set_state(TeacherStates.phone)
    


@router.message(TeacherStates.phone, F.text==BACK)
async def back_subject_ask(message: types.Message, state: FSMContext):
    await state.set_state(TeacherStates.subject)
    
    all_subjects = await subjects.select_all_subjects()
    await message.answer(TEACHER_SUBJECT_ASK, reply_markup=back_btn)

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
    


@router.message(TeacherStates.phone, F.content_type.in_({'text', 'contact'}))
async def teacher_phone_ask(message: types.Message, state: FSMContext):
    if message.content_type==ContentType.TEXT:
        phone = message.text
    
        if is_contact(phone):
            await message.answer(phone + '\n' + ACCEPTED)
            
            username = message.from_user.username
            await state.update_data({'teacher_username': username})
                
            await state.update_data({'teacher_phone': phone})
            await state.set_state(TeacherStates.sending_datas_to_admin)
            
            datas = await state.get_data()
            infos = create_teacher_infos(datas)
            
            await message.answer(infos, reply_markup=create_btn_with_back(TEACHER_SEND_DATAS))
        else:
            await message.answer(WRONG_CONTACT)
            await message.answer(TEACHER_PHONE_ASK, reply_markup=phone_and_back_btn)
            await state.set_state(TeacherStates.phone)
    elif message.content_type==ContentType.CONTACT:
        await message.answer(message.contact.phone_number + '\n' + ACCEPTED)
        
        username = message.from_user.username
        await state.update_data({'teacher_username': username})
        
        await state.update_data({'teacher_phone': message.contact.phone_number})
        await state.set_state(TeacherStates.sending_datas_to_admin)
        
        datas = await state.get_data()
        infos = create_teacher_infos(datas)
            
        await message.answer(infos, reply_markup=create_btn_with_back(TEACHER_SEND_DATAS))
        


@router.message(TeacherStates.sending_datas_to_admin, F.text==BACK)
async def back_phone_ask(message: types.Message, state: FSMContext):
    await state.set_state(TeacherStates.phone)
    await message.answer(TEACHER_PHONE_ASK, reply_markup=phone_and_back_btn)
    


@router.message(TeacherStates.sending_datas_to_admin, F.text==TEACHER_SEND_DATAS)
async def send_datas_to_admins(message: types.Message, state: FSMContext):
    await state.update_data({'teacher_chat_id': str(message.chat.id),
                             'teacher_salary': 1500000})

    datas = await state.get_data()
    infos = create_teacher_infos(datas)
    
    teacher = await teachers.upsert_teacher(datas)
    ADMINS = open_json_file('data\\admins.json')
    
    for admin in ADMINS:
        try:
            msg = await bot.send_message(
                chat_id=admin['chat_id'],
                text=infos,
                reply_markup=create_accepting_btns(call_data=f'{message.chat.id}_teacher_{teacher["teacher_id"]}')
            )
            
            await bot.send_message(
                chat_id=admin['chat_id'],
                text=ADMIN_NOTE,
                reply_to_message_id=msg.message_id
            )
        except Exception as error:
            logger.exception(f"Teacher datas did not send to admin: {admin}. Error: {error}")
    

    await state.set_state(TeacherStates.waiting_admin)
    await message.answer(SENDED, reply_markup=types.ReplyKeyboardRemove())




##########################################################################
 
#                T E A C H E R   M A I N   M E N U                       #
 
##########################################################################



@router.callback_query(TeacherStates.waiting_select, F.data.startswith('teacher_'))
async def teacher_menu_clicked(callback: types.CallbackQuery, state: FSMContext):
    datas = callback.data.split('_')
    selection = datas[1]
    teacher_id = int(datas[2])
    teacher = await teachers.select_teacher(teacher_id=teacher_id)

    await state.update_data({'current_teacher': teacher})

    if 'test' in selection:
        pass
    elif 'group' in selection:
        teacher_groups = await groups.select_groups_by_teacher(teacher_id=teacher_id)
        
        if len(teacher_groups) > 0:
            student_counts = []
            for group in teacher_groups:
                student_count = await students.count_students_by_group(student_group_id=group['group_id'])
                student_counts.append(student_count)

            group_infos = await create_all_groups_info(groups=teacher_groups,
                                                       student_counts=student_counts)

            await callback.message.edit_text(group_infos, reply_markup=create_select_group_btns(teacher_groups))
        else:
            callback.answer(TEACHER_NO_GROUPS, show_alert=True)        
        



@router.callback_query(TeacherStates.waiting_select, F.data.startswith('groups_page_'))
async def paginate_groups(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TeacherStates.waiting_select)
    
    page = int(callback.data.split('_')[2])
    
    data = await state.get_data()
    teacher_id = data.get('current_teacher', 1)['teacher_id']
    teacher_groups = await groups.select_groups_by_teacher(teacher_id=teacher_id)
    
    student_counts = []
    for group in teacher_groups:
        student_count = await students.count_students_by_group(student_group_id=group['group_id'])
        student_counts.append(student_count)

    group_infos = await create_all_groups_info(groups=teacher_groups,
                                               student_counts=student_counts,
                                               page=page)
    
    await callback.message.edit_text(group_infos, reply_markup=create_select_group_btns(teacher_groups, page=page))




@router.callback_query(TeacherStates.waiting_select, F.data.startswith('user_select_group_'))
async def teacher_group_selected(callback: types.CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[-1])
    group = await groups.select_group_with_teacher(group_id=group_id)

    group_students_count = await students.count_students_by_group(student_group_id=group['group_id'])
    
    if group_students_count > 0:
        group_info = await create_group_info(group=group,
                                             group_students_count=group_students_count)
    
        await callback.message.answer(group_info)
        await callback.message.answer(RETRY_SELECTING, reply_markup=teacher_group_menu_btns)
    
        await state.set_state(TeacherStates.teacher_group_selected)
        await state.update_data({'teacher_current_group': group})
    
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    else:
        await callback.answer(STUDENT_COUNT_ERROR, show_alert=True)


@router.message(TeacherStates.teacher_group_selected, F.text==BACK)
async def teacher_groups_menu_back(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    teacher = datas['current_teacher']

    await message.answer(text=RETURNED + f"\n{teacher['teacher_fullname']}", reply_markup=teacher_add_group_btn)
    await message.answer(text=RETRY_SELECTING,  reply_markup=create_teacher_menu_btns(teacher['teacher_id']))
                    
    await state.set_state(TeacherStates.waiting_select)
    await state.update_data({'current_teacher': teacher})




##########################################################################
 
#                T E A C H E R   G R O U P   M E N U                     #
  
##########################################################################

#               C R E A T E   T E A M   T E S T I N G
    

@router.message(TeacherStates.teacher_group_selected, F.text==TEACHER_GROUP_TESTS)
async def teacher_test_subject_ask(message: types.Message, state: FSMContext):
    all_subjects = await subjects.select_all_subjects()

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await state.set_state(TeacherStates.teacher_test_subject_selecting)
        
        await message.answer(TEACHER_TEST_START, reply_markup=back_btn)
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))


@router.message(TeacherStates.teacher_test_subject_selecting, F.text==BACK)
async def teacher_group_menu_back(message: types.Message, state: FSMContext):    
    await state.set_state(TeacherStates.teacher_group_selected)
    await message.answer(RETRY_SELECTING, reply_markup=teacher_group_menu_btns)



@router.callback_query(TeacherStates.teacher_test_subject_selecting, F.data.contains('subject_'))
async def teacher_test_count_ask(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split('_')[1])
    subject = await subjects.select_subject(id=subject_id)
    
    if subject['numberofavailabletests'] == 0:
        await callback.answer(TESTS_NOT_FOUND, show_alert=True)
    else:
        try:
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        
            await callback.message.answer(subject['subjectname'] + '\n' + ACCEPTED)
            await callback.message.answer(AVAILABLE_TESTS_COUNT + str(subject['numberofavailabletests']), reply_markup=back_btn)
            await callback.message.answer(TEST_COUNT + "5", reply_markup=test_count_btns)
        
            await state.update_data({'teacher_current_test_subject': subject})
            await state.set_state(TeacherStates.teacher_test_count_selecting)
        except Exception as err:
            logging.exception(f"Error teachers.teacher_test_count_ask: {err}")    
    

@router.message(TeacherStates.teacher_test_subject_selecting, F.text==BACK)
async def teacher_test_subject_back(message: types.Message, state: FSMContext):    
    all_subjects = await subjects.select_all_subjects()

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await state.set_state(TeacherStates.teacher_test_subject_selecting)
        
        await message.answer(TEACHER_TEST_START, reply_markup=back_btn)
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))


@router.callback_query(TeacherStates.teacher_test_count_selecting, F.data.startswith('test_count_'))
async def teacher_selecting_test_count(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace('test_count_', '').strip()
    count = int(callback.message.text.replace(TEST_COUNT, ''))
    
    if action == 'add':
        count = count + 5
        await bot.edit_message_text(text=TEST_COUNT+str(count), \
                                    chat_id=callback.message.chat.id, \
                                    message_id=callback.message.message_id, \
                                    reply_markup=test_count_btns)
    elif action == 'remove':
        if count > 5:
            count = count - 5
            await bot.edit_message_text(text=TEST_COUNT+str(count), \
                                        chat_id=callback.message.chat.id, \
                                        message_id=callback.message.message_id, \
                                        reply_markup=test_count_btns)
        else:
            await callback.answer(TEST_COUNT_ERROR, show_alert=True)
    elif action == 'confirm':
        try:
            await state.update_data({'teacher_current_test_count': count})

            datas = await state.get_data()
            available_test_count = datas['teacher_current_test_subject']['numberofavailabletests']
            
            if available_test_count >= count:
                group_students = await students.select_students_by_group(student_group_id=datas['teacher_current_group']['group_id'])

                sended = 0
                sended_msg_ids = []
                sended_chat_ids = []
                
                test_info = await create_test_info(datas)

                for student in group_students:
                    try:
                        stat_datas = {'teacher_id': datas['current_teacher']['teacher_id'],
                                      'student_id': student['student_id'],
                                      'subject_id': datas['teacher_current_test_subject']['id'],
                                      'correct_answers_count': 0,
                                      'all_tests_count': count,
                                      'statistics_date': datetime.now()}
                        
                        stat = await statistics.upsert_statistics(stat_datas)
                        
                        msg = await bot.send_message(chat_id=int(student['student_chat_id']),
                                                     text=test_info,
                                                     reply_markup=create_test_accepting_btns(student_id=student['student_id'],
                                                                                             teacher_chat_id=datas['current_teacher']['teacher_chat_id'],
                                                                                             stat_id=stat['statistics_id']))
                        await bot.send_message(chat_id=int(student['student_chat_id']),
                                               text=TEST_TIME_NOTIFY)
                        
                        sended_msg_ids.append(msg.message_id)
                        sended_chat_ids.append(int(student['student_chat_id']))
                        sended += 1
                    except Exception as err:
                        logging.exception(f"Sending test info error: {err}")
         
                
                await callback.message.answer(test_info)
                await callback.message.answer(SENDED_STUDENTS_COUNT + f"{sended}/{len(group_students)}", reply_markup=back_btn)
            

                await state.update_data({'teacher_test_sended_msgs': sended_msg_ids,
                                         'teacher_test_sended_chats': sended_chat_ids})
                await state.set_state(TeacherStates.teacher_test_waiting_start)

                await callback.message.delete()
            else:
                await callback.answer(AVAILABLE_TESTS_COUNT_ERROR, show_alert=True)
        except Exception as err:
            await callback.answer(str(err), show_alert=True)
            print(f"Error sending questions: {err}")


@router.message(TeacherStates.teacher_test_waiting_start, F.text==BACK)
async def teacher_test_subject_back(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    teacher = datas['current_teacher']

    await message.answer(text=f"\n{teacher['teacher_fullname']}", reply_markup=teacher_add_group_btn)
    await message.answer(text=RETRY_SELECTING,  reply_markup=create_teacher_menu_btns(teacher['teacher_id']))
                    
    await state.set_state(TeacherStates.waiting_select)
    await state.update_data({'current_teacher': teacher})




#########################################################################

#             C H E C K   G R O U P   A T T E N D A N C E 
    

@router.message(TeacherStates.teacher_group_selected, F.text==TEACHER_GROUP_ATTENDANCE)
async def teacher_get_students_attendances_list(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    group = datas['teacher_current_group']
    group_id = group['group_id']
    group_students = await students.select_students_by_group(student_group_id=group_id)

    today_date = date.today()
    existing_attendance = await attendance.select_attendance(
        attendance_group_id=group_id,
        attendance_date=today_date
    )
    
    if existing_attendance:
        group_attendance = {}
        
        for student in group_students:
            existing_status = STUDENT_ATTENDANCE_EXIST_STATUS
            for entry in existing_attendance:
                if entry['attendance_student_id'] == student['student_id']:
                    existing_status = entry['attendance_status']
                    break
 
            group_attendance[student['student_id']] = {
                'student_fullname': student['student_fullname'],
                'status': existing_status 
            }
    else:        
        group_attendance = {}
        for student in group_students:
            group_attendance[student['student_id']] = {
                'student_fullname': student['student_fullname'],
                'status': STUDENT_ATTENDANCE_EXIST_STATUS  
            }

    await state.update_data({"current_group_attendance": group_attendance})
    await message.answer(STUDENT_ATTENDANCE, reply_markup=create_attendance_group_students_btns(group_attendance))



@router.callback_query(TeacherStates.teacher_group_selected, F.data.contains('student_attendance'))
async def teacher_click_student_attendance(callback: types.CallbackQuery, state: FSMContext):
    datas = callback.data.split('_')
    current_status = datas[-1]
    student_id = int(datas[-2])

    new_status = STUDENT_ATTENDANCE_NOT_EXIST_STATUS if current_status == STUDENT_ATTENDANCE_EXIST_STATUS else STUDENT_ATTENDANCE_EXIST_STATUS
    
    datas = await state.get_data()
    group_attendance = datas['current_group_attendance']
    
    group_attendance[student_id] = {
                                 'student_fullname': group_attendance[student_id]['student_fullname'],
                                  'status': new_status      
                             }
    
    await callback.message.edit_reply_markup(reply_markup=create_attendance_group_students_btns(group_attendance=group_attendance))




@router.callback_query(TeacherStates.teacher_group_selected, F.data.contains("attendance_confirm"))
async def teacher_confirm_attendance(callback: types.CallbackQuery, state: FSMContext):
    datas = await state.get_data()
    group_attendance = datas['current_group_attendance']
    group = datas['teacher_current_group']

    student_ids = group_attendance.keys()
    
    for student_id in student_ids:
        attendance_date = {
                'attendance_student_id': student_id,
                'attendance_group_id': group['group_id'],
                'attendance_date': date.today(),
                'attendance_status': group_attendance[student_id]['status']
            }
        
        await attendance.upsert_attendance(data=attendance_date)
        
    await callback.message.answer(ATTENDANCE_SAVED)
    await callback.message.delete()



#########################################################################

#                C H E C K   G R O U P   P A Y M E N T S 
    

@router.message(TeacherStates.teacher_group_selected, F.text==TEACHER_GROUP_PAYMENT)
async def teacher_get_students_payments_list(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    group = datas['teacher_current_group']
    group_id = group['group_id']
    
    group_students = await students.select_students_by_group(student_group_id=group_id)
    group_payments = await payments.select_payment(payment_group_id=group_id)
    
    if len(group_payments) == 0:
        group_payments = {}
        
        for student in group_students:
            default_payment = {
                'payment_student_id': student['student_id'],
                'payment_group_id': group_id,
                'payment_amount': 0,
                'payment_date': date.today()
            }
            
            payment = await payments.upsert_payment(default_payment)
            group_payments[student['student_id']] = {
                'payment_id': payment['payment_id'],
                'student_fullname': student['student_fullname'],
                'payment_last_date': date.today(), 
                'amount': 0 
            }
            
        await state.update_data({"current_group_payments": group_payments})
        await message.answer(STUDENT_PAYMENTS, reply_markup=create_attendance_group_payments_btns(group_payments))
    else:
        student_fullnames = {student['student_id']: student['student_fullname'] for student in group_students}
        new_group_payments = {}
        
        for student in group_students:
            group_student_id = student['student_id']
            new_payment = None
            
            for payment in group_payments:
                student_id = payment['payment_student_id']
                if student_id == group_student_id:
                    new_payment = payment
                    break
                
            if new_payment:
                new_group_payments[group_student_id] = {
                    'payment_id': new_payment['payment_id'],
                    'student_fullname': student_fullnames[group_student_id],
                    'payment_last_date': new_payment['payment_date'], 
                    'amount': new_payment['payment_amount']
                }
            else:
                default_payment = {
                    'payment_student_id': student['student_id'],
                    'payment_group_id': group_id,
                    'payment_amount': 0,
                    'payment_date': date.today()
                }
            
                payment = await payments.upsert_payment(default_payment)
                new_group_payments[student['student_id']] = {
                    'payment_id': payment['payment_id'],
                    'student_fullname': student['student_fullname'],
                    'payment_last_date': date.today(), 
                    'amount': 0 
                }
                
            
        group_payments = new_group_payments

        await state.update_data({"current_group_payments": new_group_payments})
        await message.answer(STUDENT_PAYMENTS, reply_markup=create_attendance_group_payments_btns(new_group_payments))



@router.callback_query(TeacherStates.teacher_group_selected, F.data.contains('student_payment'))
async def teacher_click_student_payment(callback: types.CallbackQuery, state: FSMContext):
    datas = callback.data.split('_')
    action_type = datas[-2]
    student_id = int(datas[-1])
    
    datas = await state.get_data()
    group_payments = datas['current_group_payments']
    current_payment = group_payments.get(student_id, {})
    
    if action_type == 'minus':
        if current_payment['amount'] > 0:
            current_payment['amount'] -= 10
        
            group_payments[student_id] = current_payment
            await callback.message.edit_reply_markup(reply_markup=create_attendance_group_payments_btns(group_payments))
    
    elif action_type == 'plus':
        current_payment['amount'] += 10
        
        group_payments[student_id] = current_payment
        await callback.message.edit_reply_markup(reply_markup=create_attendance_group_payments_btns(group_payments))

    elif action_type == 'update':
        today = date.today()
        last_payment = current_payment['payment_last_date']
        
        if last_payment + timedelta(days=30) <= today:
            current_payment['payment_last_date'] = today
            current_payment['amount'] = 0
            await callback.answer(STUDENT_PAYMENT_DATE_UPDATE, show_alert=False)
            
            group_payments[student_id] = current_payment
            await callback.message.edit_reply_markup(reply_markup=create_attendance_group_payments_btns(group_payments))
        else:
            await callback.answer(STUDENT_PAYMENT_DATE_ERROR, show_alert=True)
      


@router.callback_query(TeacherStates.teacher_group_selected, F.data=="payments_confirm")
async def teacher_confirm_payments(callback: types.CallbackQuery, state: FSMContext):
    datas = await state.get_data()
    group_payments = datas['current_group_payments']
    group_id = datas['teacher_current_group']['group_id']
    
    for student_id, payment_data in group_payments.items():
        payment_update_data = {
            'payment_id': payment_data['payment_id'],
            'payment_student_id': student_id,
            'payment_group_id': group_id,
            'payment_amount': payment_data['amount'],
            'payment_date': payment_data['payment_last_date']
        }
        
        await payments.upsert_payment(payment_update_data)
    
    await callback.message.answer(PAYMENTS_SAVED)
    await callback.message.delete()



@router.callback_query(TeacherStates.teacher_group_selected, F.data=="payments_cancel")
async def teacher_confirm_payments(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
   

##########################################################################
 
#                    A D D   N E W   G R O U P                           #
 
##########################################################################


@router.message(TeacherStates.waiting_select, F.text==TEACHER_ADD_NEW_GROUP)
async def teacher_add_new_group(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1);
    await message.answer(ASK_NEW_GROUP_NAME, reply_markup=back_btn)
    
    await state.set_state(TeacherStates.teacher_new_group_start);



@router.message(TeacherStates.teacher_new_group_start, F.text==BACK)
async def teacher_start_menu_back(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    teacher = datas['current_teacher']

    await message.answer(text=RETURNED + f"\n{teacher['teacher_fullname']}", reply_markup=teacher_add_group_btn)
    await message.answer(text=RETRY_SELECTING,  reply_markup=create_teacher_menu_btns(teacher['teacher_id']))
                    
    await state.set_state(TeacherStates.waiting_select)
    await state.update_data({'current_teacher': teacher})



@router.message(TeacherStates.teacher_new_group_start, F.text)
async def teacher_read_new_group_name(message: types.Message, state: FSMContext):
    group_name = message.text
    
    all_subjects = await subjects.select_all_subjects()

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await state.set_state(TeacherStates.teacher_new_group_subject)
        await state.update_data({"teacher_new_group_name": group_name})
        
        await message.answer(group_name + '\n' + ACCEPTED)
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
        


@router.message(TeacherStates.teacher_new_group_subject, F.text==BACK)
async def teacher_start_menu_back(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1);
    await message.answer(ASK_NEW_GROUP_NAME, reply_markup=back_btn)
    
    await state.set_state(TeacherStates.teacher_new_group_start);
 


@router.callback_query(TeacherStates.teacher_test_subject_selecting, F.data.contains('subject_'))
async def teacher_test_count_ask(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split('_')[1])
    subject = await subjects.select_subject(id=subject_id)
    
    if subject['numberofavailabletests'] == 0:
        await callback.answer(TESTS_NOT_FOUND, show_alert=True)
    else:
        try:
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        
            await callback.message.answer(subject['subjectname'] + '\n' + ACCEPTED)
            await callback.message.answer(AVAILABLE_TESTS_COUNT + str(subject['numberofavailabletests']), reply_markup=back_btn)
            await callback.message.answer(TEST_COUNT + "5", reply_markup=test_count_btns)
        
            await state.update_data({'teacher_current_test_subject': subject})
            await state.set_state(TeacherStates.teacher_test_count_selecting)
        except Exception as err:
            logging.exception(f"Error tests.test_start: {err}")    
    


##########################################################################
 
#            N E W    S T U D E N T    A C C E P T I N G                 #
 
##########################################################################


@router.callback_query(F.data.contains('accept_'))
async def teacher_accepting(callback: types.CallbackQuery, state: FSMContext):
    datas = callback.data.split('_')
    sended_chat_id = datas[-3]
    table = datas[-2]
    id = int(datas[-1])
    
    state_with: FSMContext = FSMContext(
        storage=dispatcher.storage, 
        key=StorageKey(
            chat_id=int(sended_chat_id),
            user_id=int(sended_chat_id),  
            bot_id=bot.id))
    
    await state_with.clear()
    
    if 'not' in datas[0]:
        if 'student' in table:
            await students.delete_student_by_id(student_id=id)
            
        await state.set_state(TeacherStates.reason_non_acceptance)
        await state.update_data({'sending_user_chat_id': sended_chat_id})
        
        await callback.message.reply(REASON)

        await callback.message.edit_text(text=callback.message.text + '\n\n' + f"<blockquote>{NO_TEXT}</blockquote>")
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id+1)
    else:
        await bot.send_message(
                chat_id=sended_chat_id,
                text=USER_ACCEPTED
            )
            
        await callback.message.edit_text(text=callback.message.text + '\n\n' + f"<blockquote>{YES_TEXT}</blockquote>")
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id+1)


@router.message(TeacherStates.reason_non_acceptance, F.text)
async def admin_accepting(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    sending_chat_id = datas['sending_user_chat_id']

    reason = message.text

    msg = await bot.send_message(
            chat_id=sending_chat_id,
            text=USER_NOT_ACCEPTED
        )
    await bot.send_message(
            chat_id=sending_chat_id,
            text=REASON + reason,
            reply_to_message_id=msg.message_id
        )
    
    await message.answer(SENDED)