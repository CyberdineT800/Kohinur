import logging
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *

from loader import students, teachers, subjects, tests, bot, ADMINS
from keyboards.reply.default_buttons import*
from keyboards.inline.inline_buttons import*
from states.Start_states import StartStates
from states.Test_states import TestStates
from utils.helpers import create_questions

router = Router()


@router.callback_query(StartStates.tests, F.data.startswith('subject'))
async def test_start(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split('_')[1])
    subject = await subjects.select_subject(id=subject_id)

    if subject['numberofavailabletests'] == 0:
        await callback.answer(TESTS_NOT_FOUND, show_alert=True)
    else:
        try:
            #print(callback.message.chat.id, callback.message.message_id - 1)
            await bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        
            await callback.message.answer(subject['subjectname'] + '\n' + ACCEPTED)
            await callback.message.answer(AVAILABLE_TESTS_COUNT + str(subject['numberofavailabletests']), reply_markup=back_btn)
            await callback.message.answer(TEST_COUNT + "5", reply_markup=test_count_btns)
        
            await state.set_state(TestStates.test_counting)
            await state.update_data({"subject_id": subject_id,
                                     "available_tests_count": subject['numberofavailabletests']})
        except Exception as err:
            logging.exception(f"Error tests.test_start: {err}")
        
    
@router.message(TestStates.test_counting, F.text==BACK)
async def back_counting(message: types.Message, state: FSMContext):
    all_subjects = await subjects.select_all_subjects()
    
    await message.answer(TEST_SELECT, reply_markup=back_btn)
    msg = await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
    await state.set_state(StartStates.tests)
    
    try:
        await bot.delete_message(msg.chat.id, msg.message_id - 2)
        await bot.delete_message(msg.chat.id, msg.message_id - 3)
    except Exception as err:
        logger.exception(f"Deleting message error: {err}")
        

@router.callback_query(TestStates.test_counting, F.data.startswith('test_count_'))
async def selecting_test_count(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace('test_count_', '').strip()
    count = int(callback.message.text.replace(TEST_COUNT, ''))
    
    datas = await state.get_data()

    if action == 'add':
        if count + 5 <= datas['available_tests_count']:
            count = count + 5
            await bot.edit_message_text(text=TEST_COUNT+str(count), \
                                        chat_id=callback.message.chat.id, \
                                        message_id=callback.message.message_id, \
                                        reply_markup=test_count_btns)
        else:
            await callback.answer(TEST_COUNT_ERROR, show_alert=True)
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
            subject_id = datas['subject_id']
            available_test_count = datas['available_tests_count']
            
            if available_test_count >= count:
                msg = await callback.message.answer(TESTS_READING, reply_markup=end_testing_btn)

                questions = await tests.select_tests_by_subjectid(subject_id=subject_id)
                ques_msgs = await create_questions(bot, callback.message.chat.id, questions, count)

                await state.update_data({'ques_msgs': ques_msgs, 'count': count,
                                         'test_start_time': datetime.now()})

                await state.set_state(TestStates.test_sended)
                await bot.send_message(chat_id=msg.chat.id, text=TESTS_READY)
                await bot.send_message(chat_id=msg.chat.id, text=test_time_notify(count), reply_markup=end_testing_btn)
            
                await bot.delete_message(callback.message.chat.id, msg.message_id)
                await bot.delete_message(callback.message.chat.id, msg.message_id - 1)
            else:
                await callback.answer(AVAILABLE_TESTS_COUNT_ERROR, show_alert=True)
        except Exception as err:
            await callback.answer(str(err), show_alert=True)
            logging.exception(f"Error sending questions: {err}")
            

@router.callback_query(TestStates.test_sended, F.data.startswith('answer_'))
async def do_answering(callback: types.CallbackQuery, state: FSMContext):
    now = datetime.now()
    datas = await state.get_data()
    print("Guest", callback.data)
    
    start_time = datas['test_start_time']
    count = datas['count']
    
    if (now - start_time).total_seconds() / 60 <= 2 * count:
        data = callback.data.split('_')

        test_id = int(data[1])
        answered = datas.get(f'test_result_{test_id}', -1)
    
        if answered == -1:
            test = await tests.select_test(id=test_id)
            test = test[0]

            answer_id = int(data[2])

            if test['questionphotoid']:
                await bot.edit_message_caption(chat_id=callback.message.chat.id, \
                                               message_id=callback.message.message_id, \
                                               caption=callback.message.caption + '\n\n' + f'<blockquote>{chr(answer_id + 65)}</blockquote>')
            else:
                await bot.edit_message_text(chat_id=callback.message.chat.id, \
                                            message_id=callback.message.message_id, \
                                            text=callback.message.text + '\n\n' + f'<blockquote>{chr(answer_id + 65)}</blockquote>')
            
            await state.update_data({f'test_result_{test_id}': answer_id})
    else:
        await callback.answer(TESTS_ALREADY_ENDED, show_alert=True)
        

@router.message(TestStates.test_sended, F.text == TEST_END_REQUEST)
async def test_ending(message: types.Message, state: FSMContext):
    try:
        datas = await state.get_data()
        keys = datas.keys()

        result = 0
        all_tests_count = datas['count']
        ques_msg_ids = datas['ques_msgs']

        try:
            j = 1
            for test_id, msg_id in ques_msg_ids.items():
                test = await tests.select_test(id=test_id)
                test = test[0]
                key = f'test_result_{test_id}'
                answer_id = datas.get(key, -1)

                if answer_id == test['correctanswerindex']:
                    result += datas[key]
                    adding = TEST_CORRECT
                elif answer_id < 0:
                    adding = TEST_NOT_SELECTED
                else:
                    adding = TEST_INCORRECT

                if test['questionphotoid']:
                    await bot.edit_message_caption(chat_id=message.chat.id,
                                                   message_id=msg_id,
                                                   caption=f"{j}) {test['questiontxt']} \n\n<blockquote> {adding} </blockquote> {chr(answer_id + 65)}")
                else:
                    await bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=msg_id,
                                                text=f"{j}) {test['questiontxt']} \n\n<blockquote> {adding} </blockquote> {chr(answer_id + 65)}")  
                j += 1    
                    
        except Exception as e:
            logging.exception(f"Error in test_editing: {e}")

        subject_id = datas['subject_id']
        subject = await subjects.select_subject(id=subject_id)

        await message.answer(TEST_END)
        await message.answer(f"<blockquote>{subject['subjectname']}</blockquote>\n{TEST_RESULT}{result}/{all_tests_count}", reply_markup=start_menu_btns)

        await state.clear()
        await state.set_state(StartStates.waiting_for_selecting)

    except Exception as e:
        logging.exception(f"Error in test_ending: {e}")
