from aiogram.fsm.state import StatesGroup, State

class TestStates(StatesGroup):
    select_subject = State()
    test_counting = State()
    test_sended = State()