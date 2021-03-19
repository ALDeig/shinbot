from aiogram.types import Message
from misc import dp

import table


@dp.message_handler(commands='start')
async def start_message(message: Message):
    await message.answer('Бот запущен')


@dp.message_handler(commands='касса')
async def get_cash(message: Message):
    """Receives data at the checkout and sends it to the table"""
    text = message.text.split()
    cell = table.get_cell_address(text[1])
    if cell:
        table.write_cash_register(cell, text[-1].replace(',', '.'))
        await message.answer('Запись сохранена')
        return

    await message.answer('Ошибка в таблице. Проблема с датой.')


@dp.message_handler(commands='расход')
async def get_expense(message: Message):
    """Receives data on expenses and sends them to the table"""
    text = message.text.split()
    name = ''
    for word in text[1:-1]:
        name += f'{word} '
    result = table.write_expense(name, value=text[-1].replace(',', '.'))
    if not result:
        await message.answer('Ошибка в таблице. Нет даты')
        return
    await message.answer('Запись сохранена')


@dp.message_handler()
async def get_message(message: Message):
    command = table.parse_message(message.text)
    if not command:
        await message.answer('Неверный формат!')
        return
    if command(0) == 'cash':
        cell = table.get_cell_address(command[1])
        if cell:
            table.write_cash_register(cell=cell, value=command[-1].replace(',', '.'))
            return
        await message.answer('Ошибка в таблице - проблема с датой.')
        return
    elif command[0] == 'expanse':
        result = table.write_expense(name=command[1], value=command[-1].replace(',', '.'))
        if not result:
            await message.answer('Ошибка в таблице. Нет даты')
            return
        await message.answer('Запись сохранена')
        return

    await message.answer('Неверный формат, повторите!')


@dp.message_handler()
async def get_other_message(message: Message):
    await message.answer('Неверный формат, повторите!')
