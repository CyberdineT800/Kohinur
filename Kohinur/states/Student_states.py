from aiogram.fsm.state import StatesGroup, State

class StudentStates(StatesGroup):
    fullname = State()
    phone = State()
    subject = State()
    group = State()
    sending_datas_to_teacher = State()
    waiting_teacher = State()
    start_test = State()
    waiting_select = State()
