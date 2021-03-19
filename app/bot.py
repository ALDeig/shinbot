from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor, types
from misc import dp, bot

import config
import handlers
import table


async def send_report_month(*args):
    """Sends monthly statistics"""

    text = table.make_report_month()
    await bot.send_message(chat_id=config.ADMIN_ID, text=text)


async def send_reminder_cash(*args):
    """Sends a cash register reminder"""

    text = table.check_cash_for_day()
    await bot.send_message(chat_id=config.CHECK_USER_ID, text=text)


@dp.message_handler()
async def get_message(message: types.Message):
    result = table.parse_message(message.text)
    if not result:
        await message.answer('Неверный формат!')
    elif result.command == 'cash':
        cell = table.get_cell_address(result.name)
        if cell:
            table.write_cash_register(cell=cell, value=result.value.replace(',', '.'))
            await message.answer('Запись сохранена')
            return
        await message.answer('Ошибка в таблице - проблема с датой.')
    elif result.command == 'expense':
        result = table.write_expense(name=result.name, value=result.value.replace(',', '.'))
        if not result:
            await message.answer('Ошибка в таблице. Нет даты')
            return
        await message.answer('Запись сохранена')
        return


scheduler = AsyncIOScheduler()
scheduler.add_job(send_reminder_cash, 'cron', day='*', hour='21', minute='00')
scheduler.add_job(send_report_month, 'cron', day='1', hour='8', minute='00')


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
