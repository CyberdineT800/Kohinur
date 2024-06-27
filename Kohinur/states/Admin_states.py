from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    reason_non_acceptance = State()