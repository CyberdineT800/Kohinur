from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from data.config import BOT_TOKEN

from utils.db.postgres import Database
from utils.db.tests import Tests
from utils.db.test_files import TestFiles
from utils.db.students import Students
from utils.db.payments import Payments
from utils.db.attendance import Attendance
from utils.db.teachers import Teachers
from utils.db.subjects import Subjects
from utils.db.groups import Groups
from utils.db.statistics import Statistics
from aiogram.client.default import DefaultBotProperties

from utils.helpers import open_json_file

# import os
# main_dir = os.getcwd()+"/Kohinur/Kohinur"
# tests_dir = os.path.join(main_dir, "data")
# os.makedirs(tests_dir, exist_ok=True)
# destination = os.path.join(main_dir, "data", "admins.json")

ADMINS = open_json_file("data/admins.json")

db = Database()
students = Students()
tests = Tests()
test_files = TestFiles()
attendance = Attendance()
payments = Payments()
subjects = Subjects()
teachers = Teachers()
groups = Groups()
statistics = Statistics()

storage = MemoryStorage()
dispatcher = Dispatcher(storage=storage)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
