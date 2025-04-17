import logging
from datetime import datetime
from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.client.session.middlewares.request_logging import logger

from data.text_values import *

from loader import students, statistics, tests, test_files, teachers, subjects, groups, bot, dispatcher
from keyboards.reply.default_buttons import*
from keyboards.inline.inline_buttons import*
from states.Student_states import StudentStates
from utils.helpers import create_group_info, create_questions, create_student_statistics, is_contact, create_all_groups_info


router = Router()


##########################################################################

#         N E W    S T U D E N T   R E G I S T R A T I O N               #

##########################################################################


@router.message(StudentStates.fullname, F.text)
async def student_fullname_ask(message: types.Message, state: FSMContext):
    fullname = message.text.replace(TELEGRAM_NAME_SUFFIX, '')

    await state.update_data({'student_fullname': fullname})
    await state.set_state(StudentStates.phone)

    await message.answer(fullname +'\n' + ACCEPTED)
    await message.answer(STUDENT_PHONE_ASK, reply_markup=phone_and_back_btn)


@router.message(StudentStates.phone, F.text==BACK)
async def back_fullname_ask(message: types.Message, state: FSMContext):
    await message.answer(STUDENT_FULLNAME, reply_markup=create_btn_with_back(message.from_user.full_name+TELEGRAM_NAME_SUFFIX))
    await state.set_state(StudentStates.fullname);


@router.message(StudentStates.phone, F.content_type.in_({'text', 'contact'}))
async def student_phone_ask(message: types.Message, state: FSMContext):
    if message.content_type==ContentType.TEXT:
        phone = message.text

        if is_contact(phone):
            await message.answer(phone + '\n' + ACCEPTED)

            await state.update_data({'student_username': message.from_user.username,
                                     'student_phone': phone})
            await state.set_state(StudentStates.subject)

            all_subjects = await subjects.select_all_subjects()

            if not all_subjects:
                await message.answer(SUBJECTS_NOT_FOUND)
            else:
                await message.answer(STUDENT_SELECT_SUBJECT, reply_markup=back_btn)
                await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))
        else:
            await message.answer(WRONG_CONTACT)
            await state.set_state(StudentStates.phone)
            await message.answer(STUDENT_PHONE_ASK, reply_markup=phone_and_back_btn)
    elif message.content_type==ContentType.CONTACT:
        phone = message.contact.phone_number

        await message.answer(phone + '\n' + ACCEPTED)

        await state.update_data({'student_username': message.from_user.username,
                                 'student_phone': phone})
        await state.set_state(StudentStates.subject)

        all_subjects = await subjects.select_all_subjects()

        if not all_subjects:
            await message.answer(SUBJECTS_NOT_FOUND)
        else:
            await message.answer(STUDENT_SELECT_SUBJECT, reply_markup=back_btn)
            await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))


@router.message(StudentStates.subject, F.text==BACK)
async def student_back_phone_ask(message: types.Message, state: FSMContext):
    await message.answer(STUDENT_PHONE_ASK, reply_markup=phone_and_back_btn)
    await state.set_state(StudentStates.phone)


@router.callback_query(StudentStates.subject, F.data.startswith('subject'))
async def student_select_group(callback: types.CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split('_')[1])
    subject = await subjects.select_subject(id=subject_id)

    subject_groups = await groups.select_groups_by_subject(subject_id=subject_id)

    if len(subject_groups) > 0:
        await callback.message.answer(subject['subjectname'] + '\n' + ACCEPTED)
        await state.update_data({'student_subject_name': subject['subjectname']})
        await state.update_data({'student_subject_id': subject['id']})
        await state.set_state(StudentStates.group)

        student_counts = []
        for group in subject_groups:
            student_count = await students.count_students_by_group(student_group_id=group['group_id'])
            student_counts.append(student_count)

        group_infos = await create_all_groups_info(groups=subject_groups,
                                                   student_counts=student_counts)

        await callback.message.answer(group_infos, reply_markup=create_select_group_btns(subject_groups))
        await callback.message.delete()
    else:
        await callback.answer(NO_GROUPS, show_alert=True)


@router.message(StudentStates.group, F.text==BACK)
async def back_subject_ask(message: types.Message, state: FSMContext):
    await state.set_state(StudentStates.subject)

    all_subjects = await subjects.select_all_subjects()

    if not all_subjects:
        await message.answer(SUBJECTS_NOT_FOUND)
    else:
        await message.answer(STUDENT_SELECT_SUBJECT, reply_markup=back_btn)
        await message.answer(SUBJECTS_SELECT, reply_markup=subject_btns(all_subjects))


@router.callback_query(StudentStates.group, F.data.startswith('groups_page_'))
async def paginate_groups(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(StudentStates.group)

    page = int(callback.data.split('_')[2])

    data = await state.get_data()
    subject_id = data.get('student_subject_id')
    subject_groups = await groups.select_groups_by_subject(subject_id=subject_id)

    student_counts = []
    for group in subject_groups:
        student_count = await students.count_students_by_group(student_group_id=group['group_id'])
        student_counts.append(student_count)

    group_infos = await create_all_groups_info(groups=subject_groups,
                                               student_counts=student_counts,
                                               page=page)

    await callback.message.edit_text(group_infos, reply_markup=create_select_group_btns(subject_groups, page=page))


@router.callback_query(StudentStates.group, F.data.startswith('user_select_group_'))
async def student_datas_sending_request(callback: types.CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[-1])
    group = await groups.select_group(group_id=group_id)

    await state.update_data({'student_chat_id': str(callback.message.chat.id),
                             'student_group_id': group_id,
                             'student_group_name': group['group_name']})

    datas = await state.get_data()
    student_infos = create_student_infos(datas)

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await state.set_state(StudentStates.sending_datas_to_teacher)
    await callback.message.answer(student_infos, reply_markup=create_btn_with_back(STUDENT_SEND_DATAS))


@router.message(StudentStates.sending_datas_to_teacher, F.text==BACK)
async def back_select_group_ask(message: types.Message, state: FSMContext):
    await state.set_state(StudentStates.group)

    data = await state.get_data()
    subject_id = data.get('student_subject_id')

    subject_groups = await groups.select_groups_by_subject(subject_id=subject_id)

    if len(subject_groups) > 0:
        await state.set_state(StudentStates.group)
        student_counts = []

        for group in subject_groups:
            student_count = await students.count_students_by_group(student_group_id=group['group_id'])
            student_counts.append(student_count)

        group_infos = await create_all_groups_info(groups=subject_groups,
                                                   student_counts=student_counts)

        await message.answer(group_infos, reply_markup=create_select_group_btns(subject_groups))
    else:
        await message.answer(NO_GROUPS, show_alert=True)


@router.message(StudentStates.sending_datas_to_teacher, F.text==STUDENT_SEND_DATAS)
async def student_send_datas_to_teacher(message: types.Message, state: FSMContext):
    datas = await state.get_data()
    student_infos = create_student_infos(datas)

    group_id = datas['student_group_id']
    group = await groups.select_group(group_id=group_id)

    teacher = await teachers.select_teacher(teacher_id=group['group_teacher_id'])
    student = await students.upsert_student(datas)

    try:
        msg = await bot.send_message(
            chat_id=teacher['teacher_chat_id'],
            text=student_infos,
            reply_markup=create_accepting_btns(call_data=f'{message.chat.id}_student_{student["student_id"]}')
        )

        await bot.send_message(
            chat_id=teacher['teacher_chat_id'],
            text=TEACHER_NOTE,
            reply_to_message_id=msg.message_id
        )
    except Exception as error:
        logger.exception(f"Student datas did not send to teacher: {teacher}. Error: {error}")

    await state.set_state(StudentStates.waiting_teacher)
    await message.answer(SENDED, reply_markup=types.ReplyKeyboardRemove())



##########################################################################

#                S T U D E N T   M A I N    M E N U                      #

##########################################################################


@router.callback_query(StudentStates.waiting_select, F.data.startswith('select_student_'))
async def student_menu_clicked(callback: types.CallbackQuery, state: FSMContext):
    datas = callback.data.split('_')
    selection = datas[2]
    student_id = int(datas[3])

    student = await students.select_student(student_id=student_id)

    if 'groups' in selection:
        await callback.message.answer(STUDENT_GROUPS)

        group = await groups.select_group_with_teacher(group_id=student['student_group_id'])
        students_count = await students.count_students_by_group(student['student_group_id'])
        info = await create_group_info(group, students_count)

        await callback.message.answer(info)

    elif 'results' in selection:
        await callback.message.answer(STUDENT_RESULTS)

        stats_data = await statistics.select_grouped_statistics_by_student(student_id)
        stats_info = await create_student_statistics(stats_data)

        await callback.message.answer(stats_info, parse_mode='HTML')

    await state.set_state(StudentStates.waiting_select)
    await callback.message.answer(text=RETRY_SELECTING, reply_markup=create_student_menu_btns(student_id))
    await callback.message.delete()


##########################################################################

#             S T U D E N T   T A K E   T H E   T E S T                  #

##########################################################################


@router.callback_query(F.data.startswith('test_confirm'))
async def student_menu_clicked(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data

    datas = data.split('_')
    test_file_id = int(datas[-1])
    stat_id = int(datas[-2])
    teacher_chat_id = int(datas[-3])
    student_id = int(datas[-4])

    if 'not' in data:
        student = await students.select_student(student_id=student_id)

        await statistics.delete_statistics_by_id(statistics_id=stat_id)

        await callback.message.answer(CANCEL)

        await bot.send_message(chat_id=teacher_chat_id,
                               text=TEST_DONT_STARTED_WHO + student['student_fullname'])
    elif 'confirm' in data:
        statistic = await statistics.select_statistics(statistics_id=stat_id)
        start_date = statistic[0]['statistics_date']
        now = datetime.now()

        if (now - start_date).total_seconds() <= 86400:
            await state.update_data({'stat_id': stat_id,
                                     'current_student_id': student_id,
                                     'test_sended_date': start_date})
            await state.set_state(StudentStates.start_test)

            confirmed_stat = {
                   'statistics_id': stat_id,
                   'teacher_id': statistic[0]['teacher_id'],
                   'student_id': statistic[0]['student_id'],
                   'subject_id': statistic[0]['subject_id'],
                   'correct_answers_count': statistic[0]['correct_answers_count'],
                   'all_tests_count': statistic[0]['all_tests_count'],
                   'statistics_date': statistic[0]['statistics_date'],
                   'confirm': True,
                }

            await statistics.update_statistics(confirmed_stat)

            state_with: FSMContext = FSMContext(
            storage=dispatcher.storage,
            key=StorageKey(
                chat_id=int(teacher_chat_id),
                user_id=int(teacher_chat_id),
                bot_id=bot.id))

            datas = await state_with.get_data()

            student = await students.select_student(student_id=student_id)
            await bot.send_message(chat_id=teacher_chat_id,
                                   text=TEST_STARTED_WHO + student['student_fullname'])

            subject_id = datas['teacher_current_test_subject']['id']
            test_count = datas['teacher_current_test_count']

            await callback.message.answer(TEST_START, reply_markup=end_testing_btn)

            # SENDING TESTS
            try:
                msg = await callback.message.answer(TESTS_READING, reply_markup=end_testing_btn)

                if test_file_id == 0:
                    questions = await tests.select_test(subjectid=subject_id)
                else:
                    questions = await tests.select_test(subjectid=subject_id, testfileid=test_file_id)

                ques_msgs = await create_questions(bot, callback.message.chat.id, questions, test_count)

                await state.update_data({'ques_msgs': ques_msgs,
                                         'test_count': test_count,
                                         'test_file_id': test_file_id,
                                         'test_start_time': datetime.now()})


                await bot.send_message(chat_id=msg.chat.id, text=TESTS_READY)
                await bot.send_message(chat_id=msg.chat.id, text=test_time_notify(test_count), reply_markup=end_testing_btn)
            except Exception as err:
                logging.exception(f"Error sending questions to student: {err}")

            await state.update_data({'current_test_teacher': datas['current_teacher'],
                                     'current_test_subject': datas['teacher_current_test_subject']})

        else:
            await statistics.delete_statistics_by_id(statistics_id=stat_id)

            await callback.message.answer(TEST_TIME_ENDED)

    await callback.message.delete()


@router.callback_query(StudentStates.start_test, F.data.startswith('answer_'))
async def do_answering(callback: types.CallbackQuery, state: FSMContext):
    now = datetime.now()
    datas = await state.get_data()
    print(callback.data)

    start_time = datas['test_start_time']
    test_count = datas['test_count']

    if (now - start_time).total_seconds() / 60 <= 2 * test_count:
        data = callback.data.split('_')

        test_id = int(data[1])
        answered = datas.get(f'test_result_{test_id}', -1)

        if answered == -1:
            test = await tests.select_test(id=test_id)
            answer_id = int(data[2])

            if test[0]['questionphotoid']:
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



@router.message(StudentStates.start_test, F.text == TEST_END_REQUEST)
async def test_ending(message: types.Message, state: FSMContext):
    try:
        datas = await state.get_data()

        result = 0
        ques_msg_ids = datas['ques_msgs']
        all_test_count = datas['test_count']

        try:
            j = 1
            for test_id, msg_id in ques_msg_ids.items():
                test = await tests.select_test(id=test_id)
                test = test[0]

                key = f'test_result_{test_id}'
                answer_id = datas.get(key, -1)

                if answer_id == test['correctanswerindex']:
                    result += 1
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

        subject = datas['current_test_subject']
        teacher = datas['current_test_teacher']
        student = await students.select_student(student_id=datas['current_student_id'])

        await message.answer(TEST_END)
        await message.answer(f"<blockquote>{subject['subjectname']}</blockquote>\n{TEST_RESULT}{result}/{all_test_count}")

        test_datas = {'student_fullname': student['student_fullname'],
                      'test_subjectname': subject['subjectname'],
                      'test_name': RANDOM if datas['test_file_id'] == 0 else
                                   (await test_files.select_test_files(test_file_id=datas['test_file_id']))[0]['test_file_name'],
                      'test_result': str(f'{result}/{all_test_count}'),
                      'test_sended_time': str(datas['test_sended_date']).split('.')[0],
                      'test_ended_time': str(datetime.now()).split('.')[0]}

        await bot.send_message(chat_id=teacher['teacher_chat_id'],
                               text=create_test_result(test_datas))
        await message.answer(TEST_RESULT_SENDED, reply_markup=types.ReplyKeyboardRemove())

        stat_datas = {'statistics_id': datas['stat_id'],
                      'teacher_id': teacher['teacher_id'],
                      'student_id': student['student_id'],
                      'subject_id': subject['id'],
                      'correct_answers_count': result,
                      'all_tests_count': all_test_count,
                      'statistics_date': datetime.now()}
        await statistics.upsert_statistics(stat_datas)

        await state.set_state(StudentStates.waiting_select)
        await message.answer(text=RETRY_SELECTING, reply_markup=create_student_menu_btns(datas['current_student_id']))

    except Exception as e:
        logging.exception(f"Error in test_ending: {e}")
