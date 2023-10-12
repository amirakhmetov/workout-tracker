import logging
from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from config import workouts_token
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=workouts_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

class Pull(StatesGroup):
    # date = State()
    amount = State()


class Push(StatesGroup):
    # date = State()
    amount = State()

kb = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton('Pull-ups', callback_data='pull-ups')
btn2 = InlineKeyboardButton('Push-ups', callback_data='push-ups')
kb.add(btn1).add(btn2)

kb_date = InlineKeyboardMarkup()
btn_date1 = InlineKeyboardButton('Today', callback_data='today')
btn_date2 = InlineKeyboardButton('Another', callback_data='another')
kb_date.add(btn_date1).add(btn_date2)


@dp.message_handler(commands='start')
async def start(msg:types.Message):
    conn = sqlite3.connect('workouts.db1')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pullups(date, amount)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pushups(date, amount)")
    conn.commit()
    await msg.answer("Choose your workout", reply_markup=kb)

@dp.callback_query_handler(text='pull-ups', state=None)
async def pull(cb:types.CallbackQuery):
    await bot.send_message(chat_id=cb.from_user.id, text='Enter the amount of reps')
    await Pull.amount.set()

@dp.message_handler(lambda message: message.text, state=Pull.amount)
async def amount(msg:types.Message):
    date = msg.date.today()
    reps = msg.text
    data = [date, reps]
    conn = sqlite3.connect('workouts.db1')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO pullups VALUES(?, ?)", data)
    conn.commit()
    await Pull.next()
    await msg.answer("The data has been collected! Stay tuned")

@dp.callback_query_handler(text='push-ups', state=None)
async def pull(cb: types.CallbackQuery):
    await bot.send_message(chat_id=cb.from_user.id, text='Enter the amount of reps')
    await Push.amount.set()


@dp.message_handler(lambda message: message.text, state=Push.amount)
async def amount(msg: types.Message):
    date = msg.date.today()
    reps = msg.text
    data = [date, reps]
    conn = sqlite3.connect('workouts.db1')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO pushups VALUES(?, ?)", data)
    conn.commit()
    await Push.next()
    await msg.answer("The data has been collected! Stay tuned")

# @dp.callback_query_handler(text='today', state=Pull.date)
# async def today(cb:types.CallbackQuery):
#     conn = sqlite3.connect('workouts.db1')
#     cursor = conn.cursor()
#     date = cb.message.date.today()
#     data = [date, None]
#     cursor.execute("INSERT OR IGNORE INTO pullups VALUES(?, ?)", data)
#     conn.commit()
#     await bot.send_message(chat_id=cb.from_user.id, text='Got you! Now enter the amount of reps')
#     await Pull.amount.set()

# @dp.callback_query_handler(text='another', state=)
# async def another(cb:types.CallbackQuery):
#     await bot.send_message(chat_id=cb.from_user.id, text='OK, enter the date')
#     await bot.send_message(chat_id=cb.from_user.id, text='Got you! Now enter the amount of reps')
#     await Pull.amount.set()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)