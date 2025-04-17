from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *
from keyboards.inline.inline_buttons import create_student_menu_btns, create_teacher_menu_btns, subject_btns

from loader import students, teachers, subjects, bot, ADMINS
from keyboards.reply.default_buttons import*
from states.Admin_states import AdminStates
from states.Start_states import StartStates
from states.Student_states import StudentStates
from states.Teacher_states import TeacherStates


router = Router()
admin_ids = [str(admin['chat_id']) for admin in ADMINS]


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == TeacherStates.waiting_admin or \
       current_state == StudentStates.waiting_teacher:
        return

    telegram_id = str(message.from_user.id)
    fullname = message.from_user.full_name
    username = message.from_user.username
    user = None
    is_student = False
    
    try:
        global admin_ids

        if telegram_id not in admin_ids:
            user = await students.select_student(student_chat_id=telegram_id)
            is_student = True
           
            if not user:
                user = await teachers.select_teacher(teacher_chat_id=telegram_id)
                is_student = False
              
            if user:
                if is_student:
                    await message.answer(text=STUDENT_WELCOME + f"\n{user['student_fullname']}", reply_markup=types.ReplyKeyboardRemove())
                    await message.answer(text=RETRY_SELECTING, reply_markup=create_student_menu_btns(user['student_id']))
                    
                    await state.set_state(StudentStates.waiting_select)
                    await state.update_data({'current_student_id': user['student_id']})
                else:
                    await message.answer(text=TEACHER_WELCOME + f"\n{user['teacher_fullname']}", reply_markup=teacher_add_group_btn)
                    await message.answer(text=RETRY_SELECTING,  reply_markup=create_teacher_menu_btns(user['teacher_id']))
                    
                    await state.set_state(TeacherStates.waiting_select)
                    await state.update_data({'current_teacher': user})
            else:
                await message.answer(WELCOME, reply_markup=start_menu_btns)
                await state.set_state(StartStates.waiting_for_selecting)
                
                print('\n' + ADMIN_NOTIFY + f"\n@{username} \n{fullname}\n")
                
                for admin in ADMINS:
                    try:
                        await bot.send_message(
                            chat_id=admin['chat_id'],
                            text=ADMIN_NOTIFY + f"\n@{username} \n{fullname}"
                        )
                    except Exception as error:
                        logger.exception(f"Data did not send to admin: {admin}. Error: {error}")
        else:
            await message.answer(ADMIN_MENU, reply_markup=admin_main_menu_btns)
            await state.set_state(AdminStates.admin_main_menu)
    except Exception as error:
        logger.exception(error)
        
    # if user:
    #     count = await db.count_users()
    #     msg = (f"[{make_title(user['full_name'])}](tg://user?id={user['telegram_id']}) bazaga qo'shildi\.\nBazada {count} ta foydalanuvchi bor\.")
    # else:
    #     msg = f"[{make_title(full_name)}](tg://user?id={telegram_id}) bazaga oldin qo'shilgan"



##########################################################################

#          N E W    U S E R   S E L E C T I N G    R O L E               #
 
##########################################################################



@router.message(StartStates.waiting_for_selecting, F.text.in_([STUDENT, TEACHER, TESTS]))
async def selecting_role(message: types.Message, state: FSMContext):
    role = message.text.strip()
    
    if role==STUDENT:
        await message.answer(STUDENT_SELECT)
        #await message.answer(STUDENT_FULLNAME, reply_markup=create_btn_with_back(message.from_user.full_name+TELEGRAM_NAME_SUFFIX))
        await message.answer(STUDENT_FULLNAME, reply_markup=back_btn)
        await state.set_state(StudentStates.fullname)
    elif role==TEACHER:
        await message.answer(TEACHER_SELECT)
        #await message.answer(TEACHER_FULLNAME, reply_markup=create_btn_with_back(message.from_user.full_name+TELEGRAM_NAME_SUFFIX))
        await message.answer(TEACHER_FULLNAME, reply_markup=back_btn)
        await state.set_state(TeacherStates.fullname)
    elif role==TESTS:
        all_subjects = await subjects.select_all_subjects()

        if not all_subjects:
            await message.answer(SUBJECTS_NOT_FOUND)
        else:
            await message.answer(TEST_SELECT, reply_markup=back_btn)
            await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
            await state.set_state(StartStates.tests)
            

@router.message(TeacherStates.fullname, F.text==BACK)
@router.message(StudentStates.fullname, F.text==BACK)
async def back_selecting(message: types.Message, state: FSMContext):
    msg = await message.answer(RETRY_SELECTING, reply_markup=start_menu_btns)
    await state.set_state(StartStates.waiting_for_selecting)
    
    try:
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
        await bot.delete_message(msg.chat.id, msg.message_id - 2)
    except Exception as err:
        logger.exception(f"Deleting message error: {err}")
       
        


@router.message(StartStates.tests, F.text==BACK)
async def back_selecting(message: types.Message, state: FSMContext):
    msg = await message.answer(RETRY_SELECTING, reply_markup=start_menu_btns)
    await state.set_state(StartStates.waiting_for_selecting)
    
    try:
        await bot.delete_message(msg.chat.id, msg.message_id - 1)
        await bot.delete_message(msg.chat.id, msg.message_id - 2)
    except Exception as err:
        logger.exception(f"Deleting message error: {err}")
        
        