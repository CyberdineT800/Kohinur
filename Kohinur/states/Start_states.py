from aiogram.fsm.state import StatesGroup, State

class StartStates(StatesGroup):
    waiting_for_selecting = State()
    student = State()
    teacher = State()
    tests = State()