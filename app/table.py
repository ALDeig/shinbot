from datetime import date, timedelta
from typing import Union, NamedTuple

import config
import pygsheets

gc = pygsheets.authorize(service_file='creds.json')
sh = gc.open_by_key(config.spreadsheet_id)
wks = sh[0]


class ResultParseMessage(NamedTuple):
    command: str
    name: str
    value: str


def get_cell_address(place: str) -> Union[str, bool]:
    """Finds a cell for writing values"""

    today = date.today().strftime('%d.%m.%y')
    try:
        col = wks.find(place)[0].col
        row = wks.find(today)[0].row
    except IndexError:
        return False

    cell = pygsheets.Address((row, col)).label

    return cell


def write_cash_register(cell: str, value: str) -> bool:
    """Writes a value for selected place"""

    wks.update_value(cell, value)
    return True


def add_expense(name: str, value: str, row: int) -> bool:
    """Create new row in table and writes expense in the row"""

    wks.insert_rows(row, 1)
    cell1 = pygsheets.Cell(pygsheets.Address((row + 1, 8)), name)
    cell2 = pygsheets.Cell(pygsheets.Address((row + 1, 9)), value)
    wks.update_values(cell_list=[cell1, cell2])

    return True


def sum_expenses_and_write_in_table(old_value: str, value: str, row: str) -> None:
    if old_value.replace('.', '').isdigit():
        new_value = float(old_value) + float(value)
        cell = pygsheets.Address((row, 10)).label
        wks.update_value(cell, new_value)


def write_expense(name: str, value: str) -> bool:
    """Writes expense to table"""

    today = date.today().strftime('%d.%m.%y')
    try:
        row = wks.find(today)[0].row
    except IndexError:
        return False
    if wks.get_value(pygsheets.Address((row, 9)).label):
        add_expense(name, value, row)
        old_value = wks.get_value(pygsheets.Address((row, 10)).label)
    else:
        old_value = '0'
        cell1 = pygsheets.Cell(pygsheets.Address((row, 8)), name)
        cell2 = pygsheets.Cell(pygsheets.Address((row, 9)), value)
        wks.update_values(cell_list=[cell1, cell2])

    sum_expenses_and_write_in_table(old_value=old_value, value=value, row=row)

    return True


def make_report_month() -> str:
    """Counts cash and expense per month. Counts the balance and generates a report."""

    places = [0, 0, 0, 0, 0]
    cols = (2, 3, 4, 5, 9)
    tmp_date = date.today() - timedelta(days=20)
    start_date = date(tmp_date.year, tmp_date.month, 1).strftime('%d.%m.%y')
    try:
        row_start = wks.find(start_date)[0].row
        row_end = wks.find(date.today().strftime('%d.%m.%y'))[0].row - 1
    except IndexError as e:
        return f'Ошибка формаирования отчёта. Проблема с датой: {e}'
    cnt = 0
    for col in cols:
        start = pygsheets.Address((row_start, col)).label
        end = pygsheets.Address((row_end, col)).label
        results = wks.get_values(start=start, end=end)
        for sum_ in results:
            if sum_[0].replace('.', '').isdigit():
                places[cnt] += float(sum_[0])

        cnt += 1
    places.append(sum(places[:4]) - places[4])
    result = f'Итог: климовск - {places[0]:.2f}, мчс - {places[1]:.2f}, щербинка - {places[2]:.2f}, ' \
             f'домодедово - {places[3]:.2f}, расход - {places[4]:.2f}, остаток - {places[5]:.2f}'

    return result


def check_cash_for_day() -> str:
    """Checks the cash desk for the day"""

    cols = {2: 'климовск', 3: 'мчс', 4: 'щербинка', 5: 'домодедово'}
    result = 'Есть данные по всем кассам'
    today = date.today().strftime('%d.%m.%y')
    try:
        row = wks.find(today)[0].row
    except IndexError:
        return f'Ошибка - в таблице нет даты.'

    cnt = 0
    for col in cols.keys():
        cell = pygsheets.Address((row, col)).label
        if not wks.get_value(cell):
            if cnt == 0:
                result = 'Нет данных по кассам:'
                cnt += 1
            result += f' {cols[col]}'

    return result


def parse_message(message: str) -> NamedTuple or None:
    message = message.split()
    if message[0].lower() == 'касса':
        return ResultParseMessage(command='cash', name=message[1], value=message[-1])
    elif message[0].lower() == 'расход':
        name = ''
        for word in message[1:-1]:
            name += f'{word} '
        return ResultParseMessage(command='expense', name=name[:-1], value=message[-1])

    return



