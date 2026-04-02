import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import telebot

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= WEBHOOK =================
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return {"ok": True}

# ================= FILE SERVER =================
@app.get("/file/{file_id}")
def get_file(file_id: str):
    file_path = os.path.join(DOWNLOAD_DIR, file_id)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# ================= HANDLE FILE =================
def handle_file(message, file_id, file_name="file"):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    unique_name = f"{uuid.uuid4()}_{file_name}"
    file_path = os.path.join(DOWNLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(downloaded_file)

    download_link = f"{WEBHOOK_URL}/file/{unique_name}"

    bot.reply_to(message, f"✅ File uploaded!\n\n🔗 Download: {download_link}")

# ================= HANDLERS =================
@bot.message_handler(content_types=['document'])
def doc_handler(message):
    handle_file(message, message.document.file_id, message.document.file_name)

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    file_id = message.photo[-1].file_id
    handle_file(message, file_id, "photo.jpg")

@bot.message_handler(content_types=['video'])
def video_handler(message):
    handle_file(message, message.video.file_id, "video.mp4")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "📁 Send me any file, I will convert it to a download link!")

# ================= STARTUP =================
@app.on_event("startup")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
