from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import sqlite3
import asyncio

router = Router()

conn = sqlite3.connect('nest.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        full_name VARCHAR(200),
        balance REAL DEFAULT 100
    )
""")


class Students(StatesGroup):
    full_name = State()


@router.message(CommandStart())
async def start_commands(message: Message, state: FSMContext):
    await state.set_state(Students.full_name)
    await message.answer('Добро пожаловать \nВведите своё ФИО\nПосле вы можете пользоваться командами /balance и /transfer')
    
    cur.execute("SELECT * FROM users WHERE full_name = ?", (message.from_user.full_name,))
    existing_user = cur.fetchone()

    if existing_user is None:
        cur.execute('INSERT INTO users (id, full_name) VALUES (?, ?)', 
                    (message.from_user.id, message.from_user.full_name))
        conn.commit()


@router.message(Students.full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text
    cur.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, message.from_user.id))
    conn.commit()
    await state.clear()
    await message.answer(f'Вы успешно зарегистрированы как {full_name}!')


@router.message(Command('balance'))
async def balance_posm(message: Message):
    cur.execute("SELECT balance FROM users WHERE id = ?", (message.from_user.id,))
    balance = cur.fetchone()

    if balance is not None:
        await message.reply(f'Ваш баланс: {balance[0]}')
    else:
        await message.reply('Пользователь не найден в базе данных.')


@router.message(Command('transfer'))
async def transfer_pol(message: Message, state: FSMContext):

    try:
        args = message.text.split()
        if len(args) < 3:
            raise ValueError("Неверный формат команды. Используйте: /transfer <id получателя> <сумма> Пример /transfer id пользавателя 100")

        receiver_id = int(args[1])
        amount = float(args[2])

        cur.execute("SELECT balance FROM users WHERE id = ?", (message.from_user.id,))
        sender_balance = cur.fetchone()

        if sender_balance is None:
            raise ValueError("Пользователь-отправитель не найден")
        
        if sender_balance[0] < amount:
            raise ValueError("Недостаточно средств для перевода")

        cur.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, message.from_user.id))
        cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver_id))

        conn.commit()
        await message.reply("Перевод выполнен успешно")

    except Exception as e:
        conn.rollback()
        await message.reply(f"Ошибка: {e}")
