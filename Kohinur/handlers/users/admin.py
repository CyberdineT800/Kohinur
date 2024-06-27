import logging
from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *

from loader import dispatcher, students, teachers, subjects, tests, bot, ADMINS
from keyboards.reply.default_buttons import*
from keyboards.inline.inline_buttons import*
from states.Start_states import StartStates
from states.Teacher_states import TeacherStates
from states.Admin_states import AdminStates
from filters.admin import IsBotAdminFilter


router = Router()


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