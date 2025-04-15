import logging
from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta
from aiogram.fsm.storage.base import StorageKey
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *

from loader import dispatcher, payments, groups, students, teachers, subjects, tests, bot, ADMINS
from keyboards.reply.default_buttons import*
from keyboards.inline.inline_buttons import*
from states.Start_states import StartStates
from states.Teacher_states import TeacherStates
from states.Admin_states import AdminStates
from filters.admin import IsBotAdminFilter
from utils.helpers import create_all_groups_info, create_group_info, create_payment_info


router = Router()


#@router.message(F.photo, IsBotAdminFilter(ADMINS))
@router.message(F.photo)
async def back_selecting(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await message.reply(text=f"<code>{file_id}</code>")


##########################################################################
 
#                N E W    U S E R    A C C E P T I N G                   #
 
##########################################################################


@router.callback_query(F.data.contains('accept_'), IsBotAdminFilter(ADMINS))
async def admin_accepting(callback: types.CallbackQuery, state: FSMContext):
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
        if 'teacher' in table:
            await teachers.delete_teacher_by_id(teacher_id=id)
        elif 'student' in table:
            await students.delete_student_by_id(student_id=id)
            
        await state.set_state(AdminStates.reason_non_acceptance)
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
        
    
        
@router.message(AdminStates.reason_non_acceptance, F.text, IsBotAdminFilter(ADMINS))
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
    await state.clear()




##########################################################################
 
#                   A D M I N    M A I N   M E N U                       #

##########################################################################


@router.message(AdminStates.admin_main_menu, F.text==GROUPS, IsBotAdminFilter(ADMINS))
async def admin_selecting_group(message: types.Message, state: FSMContext):
    all_groups = await groups.select_all_groups_with_teachers()
        
    if len(all_groups) > 0:
        student_counts = []
        for group in all_groups:
            student_count = await students.count_students_by_group(student_group_id=group['group_id'])
            student_counts.append(student_count)

        group_infos = await create_all_groups_info(groups=all_groups,
                                                   student_counts=student_counts)

        await message.answer(text=group_infos, reply_markup=create_select_group_btns(all_groups))
    else:
        message.answer(TEACHER_NO_GROUPS)
        


@router.callback_query(AdminStates.admin_main_menu, F.data.startswith('groups_page_'), IsBotAdminFilter(ADMINS))
async def paginate_groups(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.admin_main_menu)
    
    page = int(callback.data.split('_')[2])  
    all_groups = await groups.select_all_groups_with_teachers()
    
    student_counts = []
    for group in all_groups:
        student_count = await students.count_students_by_group(student_group_id=group['group_id'])
        student_counts.append(student_count)

    group_infos = await create_all_groups_info(groups=all_groups,
                                               student_counts=student_counts,
                                               page=page)
    
    await callback.message.edit_text(group_infos, reply_markup=create_select_group_btns(all_groups, page=page))




@router.callback_query(AdminStates.admin_main_menu, F.data.startswith('user_select_group_'), IsBotAdminFilter(ADMINS))
async def admin_group_selected(callback: types.CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[-1])
    group = await groups.select_group_with_teacher(group_id=group_id)

    group_students_count = await students.count_students_by_group(student_group_id=group['group_id'])
    
    if group_students_count > 0:
        group_info = await create_group_info(group=group,
                                             group_students_count=group_students_count)
    
        await callback.message.answer(group_info)
        await callback.message.answer(RETRY_SELECTING, reply_markup=admin_group_menu_btns)
    
        await state.set_state(AdminStates.admin_group_menu_selected)
        await state.update_data({'admin_current_group': group})
    
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    else:
        await callback.answer(STUDENT_COUNT_ERROR, show_alert=True)


@router.message(AdminStates.admin_group_menu_selected, F.text==BACK, IsBotAdminFilter(ADMINS))
async def teacher_groups_menu_back(message: types.Message, state: FSMContext):
    await message.answer(ADMIN_MENU, reply_markup=admin_main_menu_btns)
    await state.set_state(AdminStates.admin_main_menu)


    
##########################################################################

#                C H E C K   G R O U P   P A Y M E N T S 
    

@router.message(AdminStates.admin_group_menu_selected, F.text==PAYMENT, IsBotAdminFilter(ADMINS))
async def admin_group_selected(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    group = datas['admin_current_group']
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



@router.callback_query(AdminStates.admin_group_menu_selected, F.data.contains('student_payment'), IsBotAdminFilter(ADMINS))
async def admin_click_student_payment(callback: types.CallbackQuery, state: FSMContext):
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
        
        group = datas['admin_current_group']
        
        if last_payment.month == today.month:
            student = await students.select_student(student_id=student_id)
            subject = await subjects.select_subject(id=group['group_subject_id'])
            
            payment_datas = {
                    'student_fullname': student['student_fullname'],
                    'student_group_name': group['group_name'],
                    'student_subject_name': subject['subjectname'],
                    'payment_amount': current_payment['amount'],
                    'payment_last_date': current_payment['payment_last_date']
                }

            payment_info = await create_payment_info(datas=payment_datas)

            current_payment['payment_last_date'] = today + timedelta(days=30)
            current_payment['amount'] = 0
            
            await bot.send_message(chat_id=student['student_chat_id'], text=payment_info)

            await callback.answer(PAYMENTS_SENDED, show_alert=True)
            
            group_payments[student_id] = current_payment
            await callback.message.edit_reply_markup(reply_markup=create_attendance_group_payments_btns(group_payments))
        else:
            await callback.answer(STUDENT_PAYMENT_DATE_ERROR, show_alert=True)
      


@router.callback_query(AdminStates.admin_group_menu_selected, F.data=="payments_confirm", IsBotAdminFilter(ADMINS))
async def admin_confirm_payments(callback: types.CallbackQuery, state: FSMContext):
    datas = await state.get_data()
    group_payments = datas['current_group_payments']
    group_id = datas['admin_current_group']['group_id']

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



@router.callback_query(AdminStates.admin_group_menu_selected, F.data=="payments_cancel", IsBotAdminFilter(ADMINS))
async def admin_cancel_payments(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
       