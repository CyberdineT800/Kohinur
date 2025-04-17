import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from aiogram.client.session.middlewares.request_logging import logger

from data import config

from loader import dispatcher, db, statistics, students, tests, test_files, attendance, payments, subjects, teachers, groups, bot

#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)


def setup_handlers(dispatcher: Dispatcher) -> None:
    """HANDLERS"""
    from handlers import setup_routers

    dispatcher.include_router(setup_routers())


def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from middlewares.throttling import ThrottlingMiddleware

    # Spamdan himoya qilish uchun klassik ichki o'rta dastur. So'rovlar orasidagi asosiy vaqtlar 0,5 soniya
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    dispatcher.callback_query.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))



def setup_filters(dispatcher: Dispatcher) -> None:
    """FILTERS"""
    from filters import ChatPrivateFilter

    # Chat turini aniqlash uchun klassik umumiy filtr
    # Filtrni handlers/users/__init__ -dagi har bir routerga alohida o'rnatish mumkin
    dispatcher.message.filter(ChatPrivateFilter(chat_type=["private"]))


async def setup_aiogram(dispatcher: Dispatcher, bot: Bot) -> None:
    logger.info("Configuring aiogram")
    setup_handlers(dispatcher=dispatcher)
    setup_middlewares(dispatcher=dispatcher, bot=bot)
    setup_filters(dispatcher=dispatcher)
    logger.info("Configured aiogram")


async def database_connected():
    global db
    
    await db.create()

    students.pool = db.pool
    await students.create_table()
    print("Connected Students table ...")

    tests.pool = db.pool
    await tests.create_table()
    print("Connected Tests table ...")

    test_files.pool = db.pool
    await test_files.create_table()
    print("Connected Test Files table ...")

    attendance.pool = db.pool
    await attendance.create_table()
    print("Connected Attendance table ...")

    payments.pool = db.pool
    await payments.create_table()
    print("Connected Payments table ...")

    subjects.pool = db.pool
    await subjects.create_table()
    print("Connected Subjects table...")

    teachers.pool = db.pool
    await teachers.create_table()
    print("Connected Teachers table ...")
    
    groups.pool = db.pool
    await groups.create_table()
    print("Connected Groups table ...")
    
    statistics.pool = db.pool
    await statistics.create_table()
    print("Connected Statistics table ...\n\n")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    from utils.set_bot_commands import set_default_commands
    from utils.notify_admins import on_startup_notify

    logger.info("Database connected")
    await database_connected()

    logger.info("\n\nStarting polling\n")
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(bot=bot, dispatcher=dispatcher)
    await on_startup_notify(bot=bot)
    await set_default_commands(bot=bot)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot):
    logger.info("\nStopping polling\n\n")
    await bot.session.close()
    await dispatcher.storage.close()


def main():
    """CONFIG"""

    dispatcher.startup.register(aiogram_on_startup_polling)
    dispatcher.shutdown.register(aiogram_on_shutdown_polling)

    try:
        #asyncio.run(dispatcher.start_polling(bot, close_bot_session=True, allowed_updates=['message', 'chat_member', 'callback_query']))
        asyncio.run(dispatcher.start_polling(bot, close_bot_session=False, allowed_updates=['message', 'chat_member', 'callback_query']))
        print("Hammasi joyida !\n")
    except Exception as e:
        logger.error(f"\n\nBot stopped due to an exception: {e}\n\n")
    finally:
        asyncio.run(aiogram_on_shutdown_polling(dispatcher, bot))
       


if __name__ == "__main__":
    print("\n\nBot ishga tushdi !\n")
    
    # try:
    #     main()
    # except Exception as e:
    #     logger.error(f"\n\nBot stopped due to an exception: {e}\n\n")

    
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"\n\nBot stopped due to an exception: {e}\n\n")
            
        print("Qayta ishga tushirilmoqda ... ")
