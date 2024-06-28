from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    reason_non_acceptance = State()
    admin_main_menu = State()
    admin_group_menu_selected = State()